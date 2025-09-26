# See LICENSE for license details.

#*****************************************************************************
# ld.S
#-----------------------------------------------------------------------------
#
# Test ld instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # 1. Define a 64-bit value in memory using the .dword directive.
  # 2. Use 'la' to get the address of the data.
  # 3. Use 'ld' to load the full 64-bit value into a register.

  # Load the base address of our test data into t0.
  la t0, test_data

  # Load the 64-bit doubleword from the address in t0 into t1.
  ld t1, 0(t0)

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

# Define the 64-bit (doubleword) data that our test will load.
test_data:
  .dword 0x1122334455667788

RVTEST_DATA_END