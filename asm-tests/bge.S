# See LICENSE for license details.

#*****************************************************************************
# bge.S
#-----------------------------------------------------------------------------
#
# Test bge instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # We test both conditions for BGE: 'greater than' and 'equal to'.
  # A status register (t2) is used to track success.
  # If t2 is 1 at the end, both tests passed.

  # Test 1: rs1 > rs2. Should branch.
  # Compare 20 and 10. Since 20 >= 10, the branch to 'test_equal' should be taken.
  li t0, 20
  li t1, 10
  bge t0, t1, test_equal

  # This code only runs if the first branch fails.
  li t2, 2 # Fail code for Test 1
  j end_test

test_equal:
  # Test 2: rs1 == rs2. Should branch.
  # Compare -5 and -5. Since -5 >= -5, the branch to 'final_success' should be taken.
  li t0, -5
  li t1, -5
  bge t0, t1, final_success

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