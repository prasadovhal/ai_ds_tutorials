"""
Exercise 2 Solution: Tests for an MCP Server
"""


# ============================================================
# TOOL FUNCTIONS (same logic as in a real server)
# ============================================================

def add(a, b):
    return str(a + b)


def subtract(a, b):
    return str(a - b)


def multiply(a, b):
    return str(a * b)


def divide(a, b):
    if b == 0:
        return "Error: division by zero"
    return str(round(a / b, 4))


# ============================================================
# TESTS
# ============================================================

def run_test(test_name, actual, expected):
    """Run a single test and print result."""
    if actual == expected:
        print(f"  [PASS] {test_name}")
        return True
    else:
        print(f"  [FAIL] {test_name}: expected '{expected}', got '{actual}'")
        return False


def run_all_tests():
    """Run all tests and print summary."""
    results = []

    print("Running calculator tests...\n")

    # Add tests
    results.append(run_test("add(2, 3)", add(2, 3), "5"))
    results.append(run_test("add(-1, 1)", add(-1, 1), "0"))
    results.append(run_test("add(0, 0)", add(0, 0), "0"))

    # Subtract tests
    results.append(run_test("subtract(10, 3)", subtract(10, 3), "7"))
    results.append(run_test("subtract(0, 5)", subtract(0, 5), "-5"))

    # Multiply tests
    results.append(run_test("multiply(4, 5)", multiply(4, 5), "20"))
    results.append(run_test("multiply(0, 100)", multiply(0, 100), "0"))
    results.append(run_test("multiply(-3, -4)", multiply(-3, -4), "12"))

    # Divide tests
    results.append(run_test("divide(10, 2)", divide(10, 2), "5.0"))
    results.append(run_test("divide(10, 0)", divide(10, 0), "Error: division by zero"))
    results.append(run_test("divide(7, 3)", divide(7, 3), "2.3333"))

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed!")
    else:
        print("Some tests failed!")

    return passed == total


if __name__ == "__main__":
    run_all_tests()
