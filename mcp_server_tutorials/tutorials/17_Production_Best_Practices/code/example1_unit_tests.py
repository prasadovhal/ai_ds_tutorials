"""
Example 1 - Unit Testing MCP Tool Functions
============================================
This example shows how to unit test MCP tool functions directly.
We define simple tool functions and run assert-based tests on them.
No server needed -- just test the logic!
"""

# ============================================================
# Step 1: Define tool functions (these would normally be @mcp.tool)
# ============================================================

def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


def divide(a: float, b: float) -> float:
    """Divide a by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()


# ============================================================
# Step 2: Define test functions using simple asserts
# ============================================================

def test_add():
    """Test the add function with various inputs."""
    # Basic addition
    assert add(2, 3) == 5, "2 + 3 should be 5"
    # Adding zero
    assert add(0, 0) == 0, "0 + 0 should be 0"
    # Negative numbers
    assert add(-1, 1) == 0, "-1 + 1 should be 0"
    # Floating point
    assert add(1.5, 2.5) == 4.0, "1.5 + 2.5 should be 4.0"
    print("  PASS: test_add")


def test_divide():
    """Test the divide function with various inputs."""
    # Basic division
    assert divide(10, 2) == 5.0, "10 / 2 should be 5.0"
    # Division resulting in float
    assert divide(7, 2) == 3.5, "7 / 2 should be 3.5"
    # Dividing zero by something
    assert divide(0, 5) == 0.0, "0 / 5 should be 0.0"
    # Test division by zero raises error
    try:
        divide(10, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected behavior
    print("  PASS: test_divide")


def test_uppercase():
    """Test the uppercase function with various inputs."""
    # Basic uppercase
    assert uppercase("hello") == "HELLO", "hello should become HELLO"
    # Already uppercase
    assert uppercase("WORLD") == "WORLD", "WORLD should stay WORLD"
    # Mixed case
    assert uppercase("Hello World") == "HELLO WORLD"
    # Empty string
    assert uppercase("") == "", "Empty string should stay empty"
    # Numbers and symbols stay the same
    assert uppercase("abc123!") == "ABC123!"
    print("  PASS: test_uppercase")


# ============================================================
# Step 3: Run all tests
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Running Unit Tests for MCP Tool Functions")
    print("=" * 50)

    # Track results
    passed = 0
    failed = 0

    # Run each test and catch any assertion errors
    for test_func in [test_add, test_divide, test_uppercase]:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {test_func.__name__} - {e}")
            failed += 1

    # Print summary
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    print("=" * 50)
