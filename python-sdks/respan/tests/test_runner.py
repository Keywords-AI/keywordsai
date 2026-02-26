#!/usr/bin/env python3
"""
Test runner script for Respan SDK

This script provides a convenient way to run all tests or specific test suites.
"""

import sys
import os
import subprocess
from pathlib import Path


def run_tests(test_path=None, verbose=True, coverage=False):
    """
    Run pytest with optional parameters
    
    Args:
        test_path: Specific test file or directory to run
        verbose: Enable verbose output
        coverage: Enable coverage reporting
    """
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=src/respan",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with return code: {e.returncode}")
        return e.returncode


def main():
    """Main entry point for test runner"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "unit":
            # Run only unit tests
            return run_tests("tests/test_base_crud_api.py")
        
        elif command == "dataset":
            # Run dataset API tests
            return run_tests("tests/test_dataset_api.py")
        
        elif command == "evaluator":
            # Run evaluator API tests
            return run_tests("tests/test_evaluator_api.py")
        
        elif command == "integration":
            # Run integration tests
            return run_tests("tests/test_dataset_workflow_integration.py")
        
        elif command == "real":
            # Run real API tests
            return run_tests("tests/test_respan_api_integration.py")
        
        elif command == "coverage":
            # Run all tests with coverage
            return run_tests(coverage=True)
        
        elif command == "help":
            print("Available commands:")
            print("  unit        - Run base CRUD API unit tests")
            print("  dataset     - Run Respan dataset API tests")
            print("  evaluator   - Run Respan evaluator API tests")
            print("  integration - Run dataset workflow integration tests")
            print("  real        - Run Respan API integration tests")
            print("  coverage    - Run all tests with coverage report")
            print("  help        - Show this help message")
            return 0
        
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
            return 1
    
    else:
        # Run all tests
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())