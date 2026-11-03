"""
Exercise 3 Solution: Verification Script
"""

import sys


def run_checks():
    """Run all verification checks and return results."""
    results = {}

    # Check 1: Python version
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        results["Python 3.10+"] = "PASS"
    else:
        results["Python 3.10+"] = f"FAIL (found {version.major}.{version.minor})"

    # Check 2: Import mcp
    try:
        import mcp
        results["mcp package"] = "PASS"
    except ImportError:
        results["mcp package"] = "FAIL (run: poetry add mcp)"

    # Check 3: Import httpx
    try:
        import httpx
        results["httpx package"] = "PASS"
    except ImportError:
        results["httpx package"] = "FAIL (run: poetry add httpx)"

    # Check 4: Import pydantic
    try:
        import pydantic
        results["pydantic package"] = "PASS"
    except ImportError:
        results["pydantic package"] = "FAIL (run: poetry add pydantic)"

    # Check 5: Create FastMCP server
    try:
        from mcp.server.fastmcp import FastMCP
        test_server = FastMCP("test-server")
        results["FastMCP creation"] = "PASS"
    except Exception as e:
        results["FastMCP creation"] = f"FAIL ({str(e)})"

    # Check 6: Register a tool
    try:
        from mcp.server.fastmcp import FastMCP
        test_server = FastMCP("test-server-2")

        @test_server.tool()
        def test_tool(x: int) -> str:
            return str(x)

        results["Tool registration"] = "PASS"
    except Exception as e:
        results["Tool registration"] = f"FAIL ({str(e)})"

    return results


if __name__ == "__main__":
    print("=" * 50)
    print("MCP Setup Verification")
    print("=" * 50)

    results = run_checks()

    # Print results
    print()
    all_passed = True
    for check_name, status in results.items():
        icon = "[OK]" if status == "PASS" else "[!!]"
        print(f"  {icon} {check_name}: {status}")
        if status != "PASS":
            all_passed = False

    print()
    if all_passed:
        print("All checks passed! Your MCP setup is ready.")
    else:
        print("Some checks failed. Please fix the issues above.")
    print("=" * 50)
