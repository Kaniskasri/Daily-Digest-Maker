"""Test runner script for Daily Digest Maker."""
import sys
import pytest


def main():
    """Run all tests."""
    print("=" * 60)
    print("Running Daily Digest Maker Test Suite")
    print("=" * 60)
    print()
    
    # Run pytest with coverage
    args = [
        'tests/',
        '-v',
        '--tb=short',
        '-ra',  # Show summary of all test outcomes
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run tests
    exit_code = pytest.main(args)
    
    print()
    print("=" * 60)
    if exit_code == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
