import os
import random
import logging
from enum import Enum

import cocotb
import vsc
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotbext.axi import AxiMaster, AxiBus, AxiBurstType
from cocotbext.uart import UartSink, UartSource

# -----------------------------------------------------------------------------
# 1. GLOBAL CONFIGURATION
# -----------------------------------------------------------------------------
CLK_PERIOD_NS = 100                 # 10 MHz Clock
CLK_FREQ      = 1_000_000_000 // CLK_PERIOD_NS
UART_BASE     = 0x00011300          # Base Address

# -----------------------------------------------------------------------------
# 2. REGISTER MAP & CONSTANTS
# -----------------------------------------------------------------------------
UartParity = Enum("UartParity", "NONE EVEN ODD MARK SPACE")

BAUD_REG      = UART_BASE + 0x00
TX_REG        = UART_BASE + 0x04
RX_REG        = UART_BASE + 0x08
STATUS_REG    = UART_BASE + 0x0C
DELAY_REG     = UART_BASE + 0x10
CTRL_REG      = UART_BASE + 0x14
INTERRUPT_EN  = UART_BASE + 0x18
IQCYC_REG     = UART_BASE + 0x1C
RX_THRESH     = UART_BASE + 0x20

# Control Register Shifts
CTRL_STOP_LSB   = 1
CTRL_PARITY_LSB = 3
CTRL_DW_LSB     = 5
CTRL_DW_MASK    = 0x1F

def parity_to_field(p: UartParity) -> int:
    if p == UartParity.ODD:  return 0b01
    if p == UartParity.EVEN: return 0b10
    return 0b00

def field_to_stop_bits(field: int):
    if field == 0b01: return 1.5
    if field == 0b10: return 2
    return 1

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS (Safe 32-bit Access)
# -----------------------------------------------------------------------------
async def axi_write32(axim: AxiMaster, addr: int, value: int, *, awid=1):
    """Safe 32-bit write to configure setup registers."""
    data = int(value & 0xFFFFFFFF).to_bytes(4, "little")
    await axim.write(address=addr, data=data,
                     awid=awid, burst=AxiBurstType.FIXED, size=2)

async def rmw16(axim: AxiMaster, reg_addr: int, value16: int):
    """Simple write wrapper for 16-bit registers (writes 32-bit aligned)."""
    aligned_addr = reg_addr & ~0x3
    is_upper = (reg_addr & 0x2) != 0
    shift = 16 if is_upper else 0
    val32 = (value16 & 0xFFFF) << shift
    await axi_write32(axim, aligned_addr, val32)

# -----------------------------------------------------------------------------
# 4. COVERAGE MODEL
# -----------------------------------------------------------------------------
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
            data_width=vsc.bit_t(5),
        )
        self.DATA = vsc.coverpoint(self.data, cp_t=vsc.uint8_t())
        self.Stop_bit = vsc.coverpoint(self.stop_bits, bins={
            "one_stop": vsc.bin(0b00),
            "one_half_stop": vsc.bin(0b01),
            "two_stop": vsc.bin(0b10)
        })
        self.Parity = vsc.coverpoint(self.parity, bins={
            "no_parity": vsc.bin(0b00),
            "odd_parity": vsc.bin(0b01),
            "even_parity": vsc.bin(0b10)
        })
        self.Data_Width = vsc.coverpoint(self.data_width, cp_t=vsc.uint8_t())

# -----------------------------------------------------------------------------
# 5. TESTBENCH CLASSES (Updated with UartSource)
# -----------------------------------------------------------------------------
class Testbench:
    def __init__(self, dut):
        self.dut = dut
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.INFO)
        # Initialize AXI Master
        self.axi_master = AxiMaster(AxiBus.from_prefix(dut, 'ccore_master_d'),
                                    clock=dut.CLK, reset=dut.RST_N, reset_active_level=False)
        self.cg = my_covergroup()

class uart_components:
    def __init__(self, dut, clk_freq, axi_baud_value, stop_bits_num, selected_parity, data_width, uart_base_addr):
        self.baud_rate = clk_freq // (16 * axi_baud_value)

        # TX Monitor: Listens to what the DUT sends out (SOUT)
        self.uart_tx = UartSink(dut.uart_cluster.uart0.SOUT, baud=self.baud_rate,
                                bits=data_width, stop_bits=stop_bits_num, parity=selected_parity)

        # RX Driver: Drives data into the DUT (SIN)
        self.uart_rx = UartSource(dut.uart_cluster.uart0.SIN, baud=self.baud_rate,
                                  bits=data_width, stop_bits=stop_bits_num, parity=selected_parity)

# -----------------------------------------------------------------------------
# 6. TEST 1: TX (64-BIT NATIVE WRITE)
# -----------------------------------------------------------------------------
@cocotb.test()
async def test_tx_64bit_native(dut):
    """
    Test 1: Packs Baud + TX Data into one 64-bit AXI transaction.
    Verifies AXI waveform and UART Output.
    """
    # Setup
    clock = Clock(dut.CLK, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))

    dut.RST_N.value = 0
    for _ in range(200): await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    for _ in range(50): await RisingEdge(dut.CLK)

    # Initialize Signals
    dut.ccore_master_d_AWVALID.value = 0
    dut.ccore_master_d_ARVALID.value = 0
    dut.ccore_master_d_WVALID.value = 0
    dut.ccore_master_d_RREADY.value = 0
    dut.ccore_master_d_BREADY.value = 0

    tb = Testbench(dut)

    # Configure Basics
    await rmw16(tb.axi_master, DELAY_REG, 0x0000)
    await rmw16(tb.axi_master, IQCYC_REG, 0x0000)

    # Configuration for TX Test
    stop_field = random.choice([0b00, 0b01, 0b10])
    stop_bits_num = field_to_stop_bits(stop_field)
    parity_sel = UartParity.NONE
    parity_field = parity_to_field(parity_sel)
    data_width = 8 # Stick to 8 for robust 64-bit testing

    # Write Control Register
    ctrl_val = 0
    ctrl_val |= ((stop_field & 0b11) << CTRL_STOP_LSB)
    ctrl_val |= ((parity_field & 0b11) << CTRL_PARITY_LSB)
    ctrl_val |= ((data_width & CTRL_DW_MASK) << CTRL_DW_LSB)
    await rmw16(tb.axi_master, CTRL_REG, ctrl_val)

    # Setup Monitor
    baud_val = 0x0005
    tb_comps = uart_components(dut, CLK_FREQ, baud_val, stop_bits_num, parity_sel, data_width, UART_BASE)

    # -------------------------------------------------------
    # 64-BIT TRANSACTION LOGIC
    # -------------------------------------------------------
    tx_char = random.randint(0, 255)

    # Pack: Upper 32 = TX Data, Lower 32 = Baud Rate
    data_64bit_int = (tx_char << 32) | baud_val
    data_bytes = data_64bit_int.to_bytes(8, 'little')

    dut._log.info(f"TX TEST: Sending 64-bit payload: {data_bytes.hex()}")

    # Send via AXI (size=3 -> 8 bytes)
    await tb.axi_master.write(address=UART_BASE, data=data_bytes, size=3)

    # Verification
    dut._log.info("TX TEST: Waiting for UART output...")
    received = await tb_comps.uart_tx.read(count=1)
    rx_byte = int(received[0])

    tb.cg.sample(rx_byte, stop_field, parity_field, data_width)

    dut._log.info(f"TX TEST: Sent {hex(tx_char)}, Recv {hex(rx_byte)}")
    assert rx_byte == tx_char, "TX Data Mismatch"

# -----------------------------------------------------------------------------
# 7. TEST 2: RX (EXTERNAL DRIVE -> AXI READ)
# -----------------------------------------------------------------------------
@cocotb.test()
async def test_rx_verification(dut):
    """
    Test 2: Drives 'SIN' pin externally and verifies CPU can read it.
    """
    # Setup
    clock = Clock(dut.CLK, CLK_PERIOD_NS, units="ns")
    cocotb.start_soon(clock.start(start_high=False))

    dut.RST_N.value = 0
    for _ in range(100): await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    for _ in range(50): await RisingEdge(dut.CLK)

    tb = Testbench(dut)

    # 1. Configure Baud (Standard Write)
    baud_val = 0x0005
    await axi_write32(tb.axi_master, BAUD_REG, baud_val)

    # 2. Configure Control (8-bit, 1 Stop, No Parity)
    # 8-bit(3)<<5 | 1stop(0)<<1 | parity(0)<<3 = 0x60
    ctrl_val = 0x60
    await rmw16(tb.axi_master, CTRL_REG, ctrl_val)

    # Setup Components
    tb_comps = uart_components(dut, CLK_FREQ, baud_val, 1, UartParity.NONE, 8, UART_BASE)

    # 3. Drive Data (External -> DUT)
    rx_char_expected = 0xB4
    dut._log.info(f"RX TEST: Driving external data {hex(rx_char_expected)} into SIN")

    await tb_comps.uart_rx.write(bytes([rx_char_expected]))
    await tb_comps.uart_rx.wait() # Wait for driver to finish

    # Safety delay for FIFO latching
    for _ in range(200): await RisingEdge(dut.CLK)

    # 4. Read via AXI
    dut._log.info("RX TEST: Reading RX_REG via AXI...")
    rdata = await tb.axi_master.read(RX_REG, 4)

    # Process Data (First byte is usually the char)
    val_int = int.from_bytes(rdata.data, byteorder='little')
    read_char = val_int & 0xFF

    dut._log.info(f"RX TEST: Read back {hex(read_char)}")

    assert read_char == rx_char_expected, \
        f"RX Mismatch: Driven {hex(rx_char_expected)} != Read {hex(read_char)}"

    dut._log.info("RX Test Passed & Coverage Dumped.")
    vsc.write_coverage_db('cov.xml')
