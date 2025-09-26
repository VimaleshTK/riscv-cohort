# Makefile

# Use Icarus Verilog as the simulator
SIM ?= icarus

# Our hardware is in Verilog
TOPLEVEL_LANG ?= verilog

# List your Verilog source files
VERILOG_SOURCES += $(PWD)/rtl/alu.v

# --- FIX IS HERE ---
# Add the test directory to Python's search path so it can find the test module
export PYTHONPATH := $(PWD)/test

# This is the top-level module of your design
TOPLEVEL = alu

# This is the Python file containing the test (without the .py extension)
COCOTB_TEST_MODULES = test_alu

# Include cocotb's built-in rules
include $(shell cocotb-config --makefiles)/Makefile.sim
