# See LICENSE for license details.

#*****************************************************************************
# beq.S
#-----------------------------------------------------------------------------
#
# Test beq instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # 1. Clear registers. We'll use a0 as a status indicator.
  andi t0, t0, 0
  andi t1, t1, 0
  andi a0, a0, 0

  # 2. Load two registers with the SAME 64-bit value.
  li t0, 0xDEADBEEFCAFE
  li t1, 0xDEADBEEFCAFE

  # 3. Use BEQ. If t0 equals t1, the program should jump to the 'branch_was_taken' label.
  beq t0, t1, branch_was_taken

  # This code block will be SKIPPED if the branch is successful.
  # We set the status (a0) to 2 to indicate the branch failed (fall-through).
  li a0, 2
  j end_test

branch_was_taken:
  # The code jumps here because t0 and t1 were equal. 
  # We set the status (a0) to 1 to indicate the branch was successful.
  li a0, 1

end_test:
  # The test would check if a0 holds the value 1.
  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END