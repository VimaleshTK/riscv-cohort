import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def alu_basic_test(dut):
    """A simple test for our ALU"""
    dut._log.info("Starting ALU test")

    # Test ADD operation
    dut.a.value = 20
    dut.b.value = 10
    dut.op.value = 1  # Corresponds to ADD (4'b0001)
    await Timer(1, units='ns')
    assert dut.y.value == 30, f"ADD test failed: {dut.y.value} != 30"
    dut._log.info(f"ADD test passed: 20 + 10 = {dut.y.value}")

    # Test SUB operation
    dut.op.value = 2 # Corresponds to SUB (4'b0010)
    await Timer(1, units='ns')
    assert dut.y.value == 10, f"SUB test failed: {dut.y.value} != 10"
    dut._log.info(f"SUB test passed: 20 - 10 = {dut.y.value}")
