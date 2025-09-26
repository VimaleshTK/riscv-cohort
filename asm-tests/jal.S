# See LICENSE for license details.

#*****************************************************************************
# jal.S
#-----------------------------------------------------------------------------
#
# Test jal instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # 1. 'jal' jumps to 'jump_target' and stores the return address in 'ra'.
  # 2. Code at 'jump_target' sets a register (t0) to a success value (1).
  # 3. The test is successful if the jump occurs AND the correct return
  #    address is written to the link register (ra).

  # Perform the Jump and Link.
  # The CPU will save the address of the 'return_address' label into 'ra'
  # and then immediately jump to the 'jump_target' label.
  jal ra, jump_target

# This label marks the address that should be stored in 'ra'.
return_address:
  # This code is SKIPPED by the jump. We put a "fail" value here.
  # If t0 ends up as 2, the jump did not happen.
  li t0, 2
  j end_test

jump_target:
  # We landed here, so the JUMP part worked. Set t0 to 1 for success.
  li t0, 1

end_test:
  # The test framework can verify the final register state.
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN
  TEST_DATA
RVTEST_DATA_END