"""
Exercise 1 - Write a Comprehensive Test Suite
===============================================
TASK: Write a comprehensive test suite for calculator tools.

You need to:
1. Define calculator functions: add, subtract, multiply, divide
2. Write 10+ assert-based tests covering:
   - Normal cases (positive numbers)
   - Edge cases (zero, negative numbers, large numbers)
   - Error cases (division by zero)
3. Print PASS/FAIL for each test
4. Print a summary at the end

Starter code is provided below. Fill in the TODO sections.

Hint: Look at example1_unit_tests.py for the pattern to follow.
"""

# ============================================================
# Step 1: Define calculator functions
# ============================================================

def add(a: float, b: float) -> float:
    """Add two numbers."""
    # TODO: Implement this
    pass


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    # TODO: Implement this
    pass


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    # TODO: Implement this
    pass


def divide(a: float, b: float) -> float:
    """Divide a by b. Raise ValueError for division by zero."""
    # TODO: Implement this
    pass


# ============================================================
# Step 2: Write test functions (10+ tests total)
# ============================================================

def test_add_basic():
    """Test basic addition."""
    # TODO: Write at least 3 assert statements
    pass


def test_subtract_basic():
    """Test basic subtraction."""
    # TODO: Write at least 3 assert statements
    pass


def test_multiply_basic():
    """Test basic multiplication."""
    # TODO: Write at least 3 assert statements
    pass


def test_divide_basic():
    """Test basic division."""
    # TODO: Write at least 2 assert statements
    pass


def test_divide_by_zero():
    """Test that dividing by zero raises ValueError."""
    # TODO: Use try/except to verify the error
    pass


def test_edge_cases():
    """Test edge cases: zero, negative, large numbers."""
    # TODO: Write at least 3 assert statements for edge cases
    pass


# ============================================================
# Step 3: Run all tests
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Exercise 1: Calculator Test Suite")
    print("=" * 50)
    print("TODO: Implement the functions and tests above!")
    print("Then run this file to see your results.")
    print("=" * 50)

    # TODO: Loop through all test functions, run them,
    #       and track pass/fail counts.
    # Hint: Use a list of test functions and try/except
