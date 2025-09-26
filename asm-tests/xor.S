# See LICENSE for license details.

#*****************************************************************************
# xor.S
#-----------------------------------------------------------------------------
#
# Test xor instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  #-------------------------------------------------------------
  # Logical tests
  #-------------------------------------------------------------

  andi t0, t0, 0
  andi t1, t1, 0
  andi t2, t2, 0
  li t0, 0xC53D6
  li t1, 0xD6332
  xor t2, t0, t1

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
