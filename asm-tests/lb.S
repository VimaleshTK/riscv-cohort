# See LICENSE for license details.

#*****************************************************************************
# lb.S
#-----------------------------------------------------------------------------
#
# Test lb instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # 1. Define byte data in memory.
  # 2. Load a 'positive' byte (MSB=0) to check for zero-extension.
  # 3. Load a 'negative' byte (MSB=1) to check for sign-extension.

  # Load the base address of our test data into t0.
  la t0, test_data

  # Test 1: Load a positive byte.
  # Load the first byte (0x12) from the address in t0 into t1.
  lb t1, 0(t0)

  # Test 2: Load a negative byte to check sign-extension.
  # Load the second byte (0x9A) from the next address (t0 + 1) into t2.
  lb t2, 1(t0)

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

# Define the byte data that our test will load from memory.
test_data:
  .byte 0x12  # A positive 8-bit value (its highest bit, bit 7, is 0)
  .byte 0x9A  # A negative 8-bit value (its highest bit, bit 7, is 1)

RVTEST_DATA_END