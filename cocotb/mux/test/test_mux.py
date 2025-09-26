import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def mux_test(dut):
    """Test for a 4-to-1 Multiplexer."""

    dut.d0.value = 1
    dut.d1.value = 2
    dut.d2.value = 3
    dut.d3.value = 4

   

    dut._log.info("Testing sel = 00")
    dut.sel.value = 0
    await Timer(1, unit="ns") # Wait for combinational logic to settle
    assert dut.y.value == dut.d0.value, f"Mux output is {dut.y.value}, expected {dut.d0.value}"

    dut._log.info("Testing sel = 01")
    dut.sel.value = 1
    await Timer(1, unit="ns")
    assert dut.y.value == dut.d1.value, f"Mux output is {dut.y.value}, expected {dut.d1.value}"

    dut._log.info("Testing sel = 10")
    dut.sel.value = 2
    await Timer(1, unit="ns")
    assert dut.y.value == dut.d2.value, f"Mux output is {dut.y.value}, expected {dut.d2.value}"

    dut._log.info("Testing sel = 11")
    dut.sel.value = 3
    await Timer(1, unit="ns")
    assert dut.y.value == dut.d3.value, f"Mux output is {dut.y.value}, expected {dut.d3.value}"

    dut._log.info("All Mux tests passed!")
