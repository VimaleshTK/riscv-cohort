# See LICENSE for license details.

#*****************************************************************************
# andi.S
#-----------------------------------------------------------------------------
#
# Test andi instruction.
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
  li t0, 0x13372D6
  andi t1, t0, 0xFC

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
