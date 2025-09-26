# See LICENSE for license details.

#*****************************************************************************
# add.S
#-----------------------------------------------------------------------------
#
# Test add instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  andi t0, t0, 0 
  andi t1, t1, 0
  andi t2, t2, 0
  andi t3, t3, 0
  li t0, 0x1A352A9C
  li t1, 0x1B2D4C6A
  addi t2, t0, 0x1CB
  add t2, t0, t1
  addw t3, t0, t1

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
