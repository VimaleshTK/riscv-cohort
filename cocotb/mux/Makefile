# Makefile

# Use Icarus Verilog as the simulator
SIM ?= icarus

# Our hardware is in Verilog
TOPLEVEL_LANG ?= verilog

# --- UPDATE THESE LINES ---
VERILOG_SOURCES += $(PWD)/rtl/mux_4to1.v
TOPLEVEL = mux_4to1
COCOTB_TEST_MODULES = test_mux
# -------------------------

# Add the test directory to Python's search path
export PYTHONPATH := $(PWD)/test

# Include cocotb's built-in rules
include $(shell cocotb-config --makefiles)/Makefile.sim
