# See LICENSE for license details.

#*****************************************************************************
# blt.S
#-----------------------------------------------------------------------------
#
# Test blt instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # We test two conditions for BLT to ensure signed comparison works.
  # A status register (t2) tracks success.
  # If t2 is 1 at the end, both tests passed.

  # Test 1: Simple positive comparison (rs1 < rs2). Should branch.
  # Since 10 < 20, the branch to 'test_signed' should be taken.
  li t0, 10
  li t1, 20
  blt t0, t1, test_signed

  # This code only runs if the first branch fails.
  li t2, 2 # Fail code for Test 1
  j end_test

test_signed:
  # Test 2: Signed comparison with a negative number (rs1 < rs2). Should branch.
  # Since -10 < 10, the branch to 'final_success' should be taken.
  li t0, -10
  li t1, 10
  blt t0, t1, final_success

  # This code only runs if the second branch fails.
  li t2, 3 # Fail code for Test 2
  j end_test

final_success:
  # Both branches were taken correctly. Set success flag.
  li t2, 1

end_test:
  # The test framework can verify the final register state.
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN
  TEST_DATA
RVTEST_DATA_END