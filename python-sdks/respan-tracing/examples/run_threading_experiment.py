#!/usr/bin/env python3
"""
Simple runner for the threading and context propagation experiment.

This script sets up the environment and runs the comprehensive threading experiment
to demonstrate how global variables, context variables, and OpenTelemetry context
behave in multi-threaded environments.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import and run the experiment
from threading_context_experiment import main

if __name__ == "__main__":
    print("🚀 Starting Threading and Context Propagation Experiment")
    print("=" * 60)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Experiment failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Experiment finished") 