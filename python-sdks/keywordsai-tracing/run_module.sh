#!/bin/bash
# This script allows running Python modules using slash notation
# Usage: ./run_module.sh tests/tracing_tests/examples/research_bot/main

if [ $# -eq 0 ]; then
  echo "Usage: $0 <module_path>"
  echo "Example: $0 tests/tracing_tests/examples/research_bot/main"
  exit 1
fi

# Convert slashes to dots
MODULE_PATH=$(echo $1 | tr '/' '.')

# Run the module
python -m $MODULE_PATH 