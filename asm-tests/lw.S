# See LICENSE for license details.

#*****************************************************************************
# lw.S
#-----------------------------------------------------------------------------
#
# Test lw instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test 1: Load a positive word ---

  # Get the memory address of our test data and store it in t0.
  la t0, test_data

  # Load the 32-bit word from memory (at address t0 + offset 0) into t1.
  lw t1, 0(t0)

  # --- Test 2: Load a negative word (to check sign-extension) ---

  # Load the next 32-bit word (at address t0 + offset 4) into t2.
  # Since this word's highest bit is 1, it will be sign-extended with 1s.
  lw t2, 4(t0)

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

# We must define the data that our test will load from memory.
test_data:
  .word 0x12345678  # A positive 32-bit word (its highest bit is 0)
  .word 0x87654321  # A negative 32-bit word (its highest bit is 1)

RVTEST_DATA_END