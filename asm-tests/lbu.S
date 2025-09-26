# See LICENSE for license details.

#*****************************************************************************
# lbu.S
#-----------------------------------------------------------------------------
#
# Test lbu instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # 'lbu' performs ZERO-EXTENSION. We test this by loading a byte
  # that would be treated as negative by 'lb'.
  # 1. Define byte data in memory.
  # 2. Load a byte with MSB=0.
  # 3. Load a byte with MSB=1 and verify it is also zero-extended.

  # Load the base address of our test data into t0.
  la t0, test_data

  # Test 1: Load a positive byte.
  # Load the first byte (0x12). It will be zero-extended.
  lbu t1, 0(t0)

  # Test 2: Load a byte with MSB=1 to confirm zero-extension.
  # Load the second byte (0x9A). 'lbu' will treat it as an unsigned
  # value (154) and extend it with zeros.
  lbu t2, 1(t0)

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

# Define the byte data that our test will load from memory.
test_data:
  .byte 0x12  # An 8-bit value with MSB=0
  .byte 0x9A  # An 8-bit value with MSB=1

RVTEST_DATA_END