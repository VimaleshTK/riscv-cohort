import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotbext.axi import AxiMaster, AxiBus, AxiBurstType
from cocotbext.uart import UartSink

import logging
import vsc
from enum import Enum, auto
import random

# Define UartParity enum if not imported
if "UartParity" not in locals():
    UartParity = Enum("UartParity", "NONE EVEN ODD MARK SPACE")

# UART Memory Map Base Address
UART_BASE = 0x00011300
print("uart base value:", hex(UART_BASE))

# Register Offsets
# We now define them relative to their 64-bit aligned base
# Aligned Base 0x11300
BAUD_REG_ADDR = UART_BASE + 0x00     # 16 bits (Bytes 0-1)
TX_REG_ADDR = UART_BASE + 0x04       # 32 bits (Bytes 4-7)
# Aligned Base 0x11308
RX_REG_ADDR = UART_BASE + 0x08       # 32 bits (Bytes 0-3)
STATUS_REG_ADDR = UART_BASE + 0x0C   # 8 bits  (Byte 4)
# Aligned Base 0x11310
DELAY_REG_ADDR = UART_BASE + 0x10    # 16 bits (Bytes 0-1)
CTRL_REG_ADDR = UART_BASE + 0x14     # 16 bits (Bytes 4-5)
# Aligned Base 0x11318
INTERRUPT_EN_ADDR = UART_BASE + 0x18 # 8 bits  (Byte 0)
IQCYC_REG_ADDR = UART_BASE + 0x1C    # 8 bits  (Byte 4)
# Aligned Base 0x11320
RX_THRESH_ADDR = UART_BASE + 0x20    # 8 bits  (Byte 0)


def parity_extract(value):
    if value == UartParity.NONE: return 0
    elif value == UartParity.ODD: return 1
    elif value == UartParity.EVEN: return 2
    return 0

def stop_extract(value):
    if value == 0b00: return 1
    elif value == 0b01: return 1.5
    elif value == 0b10: return 2

# --- Helper functions for 64-bit Read-Modify-Write ---

async def read_64bit_word(tb, address):
    """ Reads an 8-byte (64-bit) word from an aligned address """
    aligned_addr = address & ~0x7
    tb.log.debug(f"Reading 64-bit word from aligned address {hex(aligned_addr)}")
    read_data = await tb.axi_master.read(
        address=aligned_addr,
        length=8, # 8 bytes
        arid=0x0,
        burst=AxiBurstType.INCR,
        size=3, # 2^3 = 8 bytes
        prot=0
    )
    return int.from_bytes(read_data.data, 'little')

async def write_64bit_word(tb, address, data_word):
    """ Writes an 8-byte (64-bit) word to an aligned address """
    aligned_addr = address & ~0x7
    tb.log.debug(f"Writing 64-bit word to aligned address {hex(aligned_addr)}: {hex(data_word)}")
    await tb.axi_master.write(
        address=aligned_addr,
        data=data_word.to_bytes(8, 'little'),
        awid=0x1,
        burst=AxiBurstType.INCR,
        size=3, # 2^3 = 8 bytes
        prot=0
    )

async def read_reg(tb, reg_addr, width_bytes):
    """ Performs a 64-bit RMW-read to get a register value """
    aligned_addr = reg_addr & ~0x7
    offset = reg_addr % 8
    
    word_64bit = await read_64bit_word(tb, aligned_addr)
    
    # Shift right to the byte offset, then mask
    mask = (1 << (width_bytes * 8)) - 1
    reg_val = (word_64bit >> (offset * 8)) & mask
    
    tb.log.debug(f"Read {hex(reg_val)} from addr {hex(reg_addr)}")
    return reg_val

async def write_reg(tb, reg_addr, reg_val, width_bytes):
    """ Performs a 64-bit RMW-write to set a register value """
    aligned_addr = reg_addr & ~0x7
    offset = reg_addr % 8
    
    # Read
    word_64bit = await read_64bit_word(tb, aligned_addr)
    
    # Modify
    mask = ((1 << (width_bytes * 8)) - 1) << (offset * 8) # Mask for the register's bits
    word_64bit &= ~mask # Clear the bits
    word_64bit |= (reg_val << (offset * 8)) # Set the new bits
    
    # Write
    await write_64bit_word(tb, aligned_addr, word_64bit)
    tb.log.debug(f"Wrote {hex(reg_val)} to addr {hex(reg_addr)}")


@vsc.randobj
class uart_item(object):
    def __init__(self):
        self.data = vsc.rand_bit_t(8)

@vsc.covergroup
class my_covergroup(object):
    def __init__(self):
        self.with_sample(
            data=vsc.bit_t(8),
            stop_bits=vsc.bit_t(2),
            parity=vsc.bit_t(2),
            data_width=vsc.bit_t(4),
        )
        self.DATA = vsc.coverpoint(self.data, cp_t=vsc.uint8_t())
        self.Stop_bit = vsc.coverpoint(self.stop_bits, bins={"one_stop": vsc.bin(0b00), "one_half_stop": vsc.bin(0b01), "two_stop": vsc.bin(0b10)})
        self.Parity = vsc.coverpoint(self.parity, bins={"no_parity": vsc.bin(0b00), "odd_parity": vsc.bin(0b01), "even_parity": vsc.bin(0b10)})
        self.Data_Width = vsc.coverpoint(self.data_width, bins={"5_bits": vsc.bin(5), "6_bits": vsc.bin(6), "7_bits": vsc.bin(7), "8_bits": vsc.bin(8)})

class Testbench:
    def __init__(self, dut):
        self.dut = dut
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, 'ccore_master_d'), clock=dut.CLK, reset=dut.RST_N, reset_active_level=False)
        self.cg = my_covergroup()

class uart_components:
    def __init__(self, dut, clk_freq, axi_baud_value, stop_bit_value, selected_parity, data_width, uart_number):
        self.dut = dut
        self.txrx = uart_item()
        self.baud_rate = clk_freq // (16 * axi_baud_value)
        uart_souts = { 0x00011300: dut.uart_cluster.uart0.SOUT }
        selected_sout = uart_souts[uart_number]
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)
        self.uart_tx = UartSink(selected_sout, baud=self.baud_rate, bits=data_width, stop_bits=stop_bit_value, parity=selected_parity)


@cocotb.test()
async def test_peripherals(dut):
    """Test to verify uart through AXI4 transactions"""
    clock = Clock(dut.CLK, 100, units="ns")  # 10 MHz clock
    cocotb.start_soon(clock.start(start_high=False))
    
    dut.RST_N.value = 0
    for _ in range(40): await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    for _ in range(10): await RisingEdge(dut.CLK)
    dut._log.info("Reset complete")

    tb = Testbench(dut)
    await RisingEdge(tb.dut.CLK)

    # --- Initialize ALL Registers using 64-bit (size=3) RMW writes ---
    await write_reg(tb, DELAY_REG_ADDR, 0x0, width_bytes=2)
    dut._log.info("DELAY register initialized.")

    await write_reg(tb, IQCYC_REG_ADDR, 0x0, width_bytes=1)
    dut._log.info("IQCYC register initialized.")

    await write_reg(tb, RX_THRESH_ADDR, 0x0, width_bytes=1)
    dut._log.info("RX_THRESH register initialized.")

    await write_reg(tb, INTERRUPT_EN_ADDR, 0x0, width_bytes=1)
    dut._log.info("INTERRUPT_EN register initialized.")

    axi_baud_value = 0x5
    await write_reg(tb, BAUD_REG_ADDR, axi_baud_value, width_bytes=2)
    dut._log.info("Baud rate register initialized.")

    # Perform a 32-bit AXI read from RX_REG
    await read_reg(tb, RX_REG_ADDR, width_bytes=4)
    await RisingEdge(tb.dut.CLK)

    # Read 8-bit STATUS_REG
    status_val = await read_reg(tb, STATUS_REG_ADDR, width_bytes=1)
    print(f"Initial Status register read: {hex(status_val)}")

    # Read back 16-bit BAUD_REG
    read_val_16bit = await read_reg(tb, BAUD_REG_ADDR, width_bytes=2)
    
    assert read_val_16bit == axi_baud_value, \
        f"Unexpected read value: {hex(read_val_16bit)} != {hex(axi_baud_value)}"
    
    print(f"Baud reg read successful (Read {hex(read_val_16bit)})")
    await RisingEdge(dut.CLK)

    uart_baud_rate = hex(dut.uart_cluster.uart0.user_ifc_baud_value.value)
    dut._log.info(f'UART0 baud rate {uart_baud_rate}')

    # --- Configure CTRL REG (using 64-bit Read-Modify-Write) ---
    ctrl_reg_16bit = await read_reg(tb, CTRL_REG_ADDR, width_bytes=2)
    dut._log.info(f'Initial CTRL reg 16-bit value: {hex(ctrl_reg_16bit)}')

    clk_freq = 10_000_000
    axi_baud_value = 0x5

    # Randomize UART parameters
    stop_bit_value = random.choice([0b00, 0b01, 0b10])
    if stop_bit_value == 0b00: selected_stop = 1
    elif stop_bit_value == 0b01: selected_stop = 1.5
    else: selected_stop = 2

    parity_bit_value = random.choice([0b00, 0b01, 0b10])
    if parity_bit_value == 0b00: selected_parity = UartParity.NONE
    elif parity_bit_value == 0b01: selected_parity = UartParity.ODD
    else: selected_parity = UartParity.EVEN
        
    uart_data_width = random.choice([5, 6, 7, 8])
    print(f"Selected UART data width: {uart_data_width}")

    tb1 = uart_components(dut, clk_freq, axi_baud_value, selected_stop, selected_parity, uart_data_width, UART_BASE)

    # Perform modifications on the 16-bit value
    ctrl_reg_16bit &= ~(0b11 << 3)
    ctrl_reg_16bit |= (parity_bit_value << 3)
    print(f'Setting parity bit value: {bin(parity_bit_value)}')

    ctrl_reg_16bit &= ~(0b11 << 1)
    ctrl_reg_16bit |= (stop_bit_value << 1)
    print(f'Setting stop_bit value: {bin(stop_bit_value)}')

    ctrl_reg_16bit &= ~(0b111 << 5) 
    ctrl_reg_16bit |= (uart_data_width << 5)
    print(f"Setting data_width_value: {bin(uart_data_width)}")

    # Write the new 16-bit value back to CTRL_REG
    await write_reg(tb, CTRL_REG_ADDR, ctrl_reg_16bit, width_bytes=2)
    
    # Read back 16-bit CTRL_REG word to verify
    read_back_ctrl = await read_reg(tb, CTRL_REG_ADDR, width_bytes=2)
    dut._log.info(f'New CTRL reg 16-bit value: {hex(read_back_ctrl)}')
    assert read_back_ctrl == ctrl_reg_16bit

    for _ in range(10):
        await RisingEdge(tb.dut.CLK)

    # --- Send and Verify Data ---
    
    status_val = await read_reg(tb, STATUS_REG_ADDR, width_bytes=1)
    print(f"Status before TX: {hex(status_val)}")

    mask = (1 << uart_data_width) - 1
    etx_data_full = random.randint(0, 0xFFFFFFFF)
    etx_data_masked = etx_data_full & mask
    
    tb.cg.sample(etx_data_masked, stop_bit_value, parity_bit_value, uart_data_width)
    print(f'TX_REG value to be written: {hex(etx_data_full)} (Expected on wire: {hex(etx_data_masked)})')

    # Write 32-bit data to the UART TX_REG
    await write_reg(tb, TX_REG_ADDR, etx_data_full, width_bytes=4)
    
    await tb1.uart_tx.wait()
    tx_data_list = tb1.uart_tx.read_nowait()
    
    print(f"Raw data from UartSink: {tx_data_list}")
    
    if tx_data_list:
        received_data = tx_data_list[0]
        print(f"Captured UART Tx Data: {hex(received_data)}")
        
        # --- Assertions ---
        assert received_data == etx_data_masked, f'Data Mismatch DUT[{hex(received_data)}] != EXP[{hex(etx_data_masked)}]]'
        
        parity_value = parity_extract(tb1.uart_tx.parity)
        ctrl_reg_parity_value = (ctrl_reg_16bit >> 3) & 0b11
        print(f"Control reg parity value: {ctrl_reg_parity_value}")
        assert parity_value == ctrl_reg_parity_value, "Parity value mismatch"

        ctrl_reg_stop_value = (ctrl_reg_16bit >> 1) & 0b11
        ctrl_reg_stop_value = stop_extract(ctrl_reg_stop_value)
        print(f"DUT Stop bits: {tb1.uart_tx.stop_bits}, CTRL REG Stop bits: {ctrl_reg_stop_value}")
        assert tb1.uart_tx.stop_bits == ctrl_reg_stop_value, "Stop bit value mismatch"
        
        print(f"DUT data bits: {tb1.uart_tx.bits}, CTRL REG data bits: {uart_data_width}")
        assert tb1.uart_tx.bits == uart_data_width, "Data width mismatch"

    else:
        assert False, "No data received by UartSink"

    status_val = await read_reg(tb, STATUS_REG_ADDR, width_bytes=1)
    print(f"Status after TX: {hex(status_val)}")

    for _ in range(100):
        await RisingEdge(tb.dut.CLK)

    vsc.write_coverage_db('cov.xml')