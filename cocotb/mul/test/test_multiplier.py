import cocotb
from cocotb.triggers import Timer
import random

@cocotb.test()
async def multiplier_test(dut):
    """Test for a 4-bit multiplier."""

    dut._log.info("Starting multiplier test")

    # Define a few specific test cases
    test_cases = [
        (0, 0, 0),       # 0 * 0 = 0
        (1, 1, 1),       # 1 * 1 = 1
        (2, 3, 6),       # 2 * 3 = 6
        (5, 7, 35),      # 5 * 7 = 35
        (15, 15, 225),   # 15 * 15 = 225 (max for 4-bit inputs, 8-bit output)
        (10, 4, 40),     # 10 * 4 = 40
    ]

    # Run through specific test cases
    for a_val, b_val, expected_p in test_cases:
        dut._log.info(f"Testing {a_val} * {b_val}")
        dut.a.value = a_val
        dut.b.value = b_val

        await Timer(1, unit="ns") # Wait for combinational logic to settle

        actual_p = dut.p.value
        assert actual_p == expected_p, \
            f"Test failed for {a_val} * {b_val}: Expected {expected_p}, got {actual_p}"
        dut._log.info(f"PASS: {a_val} * {b_val} = {actual_p}")

    # Add some random tests for more coverage
    dut._log.info("Running random tests...")
    for _ in range(20): # Run 20 random tests
        a_val = random.randint(0, 15) # 4-bit numbers range from 0 to 15
        b_val = random.randint(0, 15)
        expected_p = a_val * b_val

        dut._log.info(f"Testing random {a_val} * {b_val}")
        dut.a.value = a_val
        dut.b.value = b_val

        await Timer(1, unit="ns")

        actual_p = dut.p.value
        assert actual_p == expected_p, \
            f"Random test failed for {a_val} * {b_val}: Expected {expected_p}, got {actual_p}"
        dut._log.info(f"PASS: {a_val} * {b_val} = {actual_p}")

    dut._log.info("All multiplier tests passed!")
