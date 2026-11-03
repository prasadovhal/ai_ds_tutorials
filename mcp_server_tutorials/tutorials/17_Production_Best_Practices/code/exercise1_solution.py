"""
Exercise 1 Solution - Comprehensive Test Suite for Calculator Tools
====================================================================
This solution provides 10+ assert-based tests for add, subtract,
multiply, and divide, including edge cases.
"""

# ============================================================
# Step 1: Define calculator functions
# ============================================================

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b. Raise ValueError for division by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


# ============================================================
# Step 2: Write 10+ test functions
# ============================================================

def test_add_basic():
    """Test basic addition with positive numbers."""
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(100, 200) == 300
    print("  PASS: test_add_basic")


def test_add_negative():
    """Test addition with negative numbers."""
    assert add(-1, -1) == -2
    assert add(-5, 5) == 0
    assert add(-10, 3) == -7
    print("  PASS: test_add_negative")


def test_subtract_basic():
    """Test basic subtraction."""
    assert subtract(10, 3) == 7
    assert subtract(5, 5) == 0
    assert subtract(0, 0) == 0
    print("  PASS: test_subtract_basic")


def test_subtract_negative():
    """Test subtraction resulting in negative numbers."""
    assert subtract(3, 10) == -7
    assert subtract(-5, -3) == -2
    assert subtract(0, 5) == -5
    print("  PASS: test_subtract_negative")


def test_multiply_basic():
    """Test basic multiplication."""
    assert multiply(3, 4) == 12
    assert multiply(7, 1) == 7
    assert multiply(0, 100) == 0
    print("  PASS: test_multiply_basic")


def test_multiply_negative():
    """Test multiplication with negative numbers."""
    assert multiply(-3, 4) == -12
    assert multiply(-3, -4) == 12
    assert multiply(-1, 0) == 0
    print("  PASS: test_multiply_negative")


def test_divide_basic():
    """Test basic division."""
    assert divide(10, 2) == 5.0
    assert divide(9, 3) == 3.0
    assert divide(7, 2) == 3.5
    print("  PASS: test_divide_basic")


def test_divide_by_zero():
    """Test that dividing by zero raises ValueError."""
    try:
        divide(10, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    try:
        divide(0, 0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    print("  PASS: test_divide_by_zero")


def test_large_numbers():
    """Test with very large numbers."""
    assert add(1_000_000, 2_000_000) == 3_000_000
    assert multiply(100_000, 100_000) == 10_000_000_000
    assert subtract(999_999, 999_999) == 0
    print("  PASS: test_large_numbers")


def test_floating_point():
    """Test with floating point numbers."""
    assert add(0.1, 0.2) == pytest_approx(0.3)
    assert multiply(1.5, 2.0) == 3.0
    assert divide(1, 3) == pytest_approx(0.3333, tolerance=0.001)
    print("  PASS: test_floating_point")


# ---- Helper for floating point comparison ----

def pytest_approx(expected: float, tolerance: float = 0.0001) -> object:
    """
    Returns an object that compares approximately equal.
    This is a simple version of pytest.approx for our assert tests.
    """
    class Approx:
        def __init__(self, val, tol):
            self.val = val
            self.tol = tol
        def __eq__(self, other):
            return abs(other - self.val) < self.tol
        def __repr__(self):
            return f"~{self.val}"
    return Approx(expected, tolerance)


# ============================================================
# Step 3: Run all tests and report results
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 1 Solution: Calculator Test Suite")
    print("=" * 50)

    # Collect all test functions
    all_tests = [
        test_add_basic,
        test_add_negative,
        test_subtract_basic,
        test_subtract_negative,
        test_multiply_basic,
        test_multiply_negative,
        test_divide_basic,
        test_divide_by_zero,
        test_large_numbers,
        test_floating_point,
    ]

    passed = 0
    failed = 0

    for test_func in all_tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {test_func.__name__} - {e}")
            failed += 1

    # Summary
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed out of {len(all_tests)}")
    if failed == 0:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    print("=" * 50)
