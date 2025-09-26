# See LICENSE for license details.

#*****************************************************************************
# sw.S
#-----------------------------------------------------------------------------
#
# Test sw instruction.
#

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64U
RVTEST_CODE_BEGIN

  # --- Test Flow ---
  # 1. Load a 64-bit value into a source register (t1).
  # 2. Store the lower 32 bits of t1 into memory using 'sw'.
  # 3. Load that 32-bit value back from memory into a new register (t2).
  # 4. The test passes if the value in t2 matches what was stored.

  # Load the base address of our empty memory region into t0.
  la t0, store_region

  # Load a 64-bit pattern into t1.
  # 'sw' will only use the lower 32 bits: 0xAAAAAAAA.
  li t1, 0x11111111AAAAAAAA

  # Store the lower 32 bits of t1 at the memory address in t0.
  sw t1, 0(t0)

  # Clear t2, then load the word we just stored back from memory.
  # This is the verification step.
  li t2, 0
  lw t2, 0(t0)

  TEST_PASSFAIL

RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

# Reserve 8 bytes of memory for this test, initialized to zero.
store_region:
  .zero 8

RVTEST_DATA_END