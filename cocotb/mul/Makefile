# Makefile

# Use Icarus Verilog as the simulator
SIM ?= icarus

# Our hardware is in Verilog
TOPLEVEL_LANG ?= verilog

# --- UPDATE THESE LINES ---
VERILOG_SOURCES += $(PWD)/rtl/multiplier.v
TOPLEVEL = multiplier
COCOTB_TEST_MODULES = test_multiplier
# -------------------------

# Add the test directory to Python's search path
export PYTHONPATH := $(PWD)/test

# Include cocotb's built-in rules
include $(shell cocotb-config --makefiles)/Makefile.sim
