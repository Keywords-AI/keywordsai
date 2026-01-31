#!/usr/bin/env python3
"""
Wrapper script to run the research bot.
This preserves all relative imports by running the module properly.

Usage:
    ./run_research_bot.py [module_path]

Example:
    ./run_research_bot.py tests/tracing_tests/examples/research_bot/main
    
If no module path is provided, it defaults to the research bot main module.
"""
import os
import sys
import runpy

# Change to the project root directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Get module path from command line or use default
if len(sys.argv) > 1:
    module_path = sys.argv[1]
else:
    module_path = "tests/tracing_tests/examples/research_bot/main"

# Convert slash notation to module notation (replace slashes with dots)
module_name = module_path.replace("/", ".")

# Run the module
runpy.run_module(module_name, run_name="__main__") 