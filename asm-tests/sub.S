# See LICENSE for license details.

#*****************************************************************************
# sub.S
#-----------------------------------------------------------------------------
#
# Test sub instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  #-------------------------------------------------------------
  # Arithmetic tests
  #-------------------------------------------------------------

  andi t0, t0, 0
  andi t1, t1, 0
  andi t2, t2, 0
  andi t3, t3, 0
  li t0, 0x1A03533A12054021
  li t1, 0x3B14875C35286142
  sub t2, t1, t0
  subw t3, t1, t0

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
