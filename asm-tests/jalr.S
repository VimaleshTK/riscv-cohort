# See LICENSE for license details.

#*****************************************************************************
# jalr.S
#-----------------------------------------------------------------------------
#
# Test jalr instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # 1. Load the address of 'jump_target' into a register (t1).
  # 2. 'jalr' performs an indirect jump to the address in t1.
  # 3. 'jalr' also stores the return address in 'ra'.
  # 4. Code at 'jump_target' sets t0 to 1 to confirm the jump occurred.
  # 5. The test passes if the jump is taken AND the correct address is linked.

  # Load the target address for our indirect jump into register t1.
  la t1, jump_target

  # Perform the Jump and Link Register.
  # The CPU saves the address of 'return_address' into 'ra' and then
  # jumps to the address currently held in register t1.
  jalr ra, t1, 0

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