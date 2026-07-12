"""
Example 3: Check Installation
==============================
Verifies that all required packages are installed correctly.
Run this after setting up your MCP project to make sure everything works.
"""

import sys


def check_python_version():
    """Check that Python 3.10+ is installed."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 10:
        print("  OK: Python 3.10+ is installed")
        return True
    else:
        print("  FAIL: Python 3.10+ is required")
        return False


def check_package(package_name):
    """Try to import a package and report its version."""
    try:
        module = __import__(package_name)
        # Try to get the version
        version = getattr(module, "__version__", "unknown")
        print(f"{package_name}: version {version}")
        print(f"  OK: {package_name} is installed")
        return True
    except ImportError:
        print(f"{package_name}: NOT INSTALLED")
        print(f"  FAIL: Install with 'poetry add {package_name}'")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("MCP Installation Checker")
    print("=" * 50)

    results = []

    # Check Python version
    print("\n--- Python ---")
    results.append(check_python_version())

    # Check required packages
    print("\n--- Required Packages ---")
    required_packages = ["mcp", "httpx", "pydantic"]
    for package in required_packages:
        results.append(check_package(package))

    # Check optional packages
    print("\n--- Optional Packages ---")
    optional_packages = ["uvicorn", "starlette"]
    for package in optional_packages:
        check_package(package)

    # Summary
    print("\n" + "=" * 50)
    if all(results):
        print("All required checks passed! You are ready to go.")
    else:
        print("Some checks failed. Please install missing packages.")
    print("=" * 50)
