#!/usr/bin/env python3
"""
Test runner for Coupon Management System backend tests.
Run this script to execute all backend tests.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Run all backend tests"""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')

    # Create test runner
    runner = unittest.TextTestRunner(verbosity=2)

    # Run tests
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
