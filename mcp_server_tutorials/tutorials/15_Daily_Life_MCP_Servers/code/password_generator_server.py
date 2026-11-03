"""
Password Generator MCP Server
================================
Generate secure passwords and check password strength.

Tools:
  - generate_password(length, use_special)
  - check_strength(password)

Uses Python's random and string modules - no external dependencies.
"""

import random
import string
from mcp.server.fastmcp import FastMCP

# Create the server
mcp = FastMCP("Password Generator")


# --- Tool: generate_password ---
@mcp.tool()
def generate_password(length: int = 16, use_special: bool = True) -> str:
    """Generate a secure random password.

    Args:
        length: Length of the password (default: 16, min: 8, max: 128)
        use_special: Include special characters like !@#$%^& (default: True)
    """
    # Enforce minimum and maximum length
    if length < 8:
        return "Error: Password must be at least 8 characters long."
    if length > 128:
        return "Error: Password cannot exceed 128 characters."

    # Build the character pool
    # Always include lowercase, uppercase, and digits
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits

    # Optionally add special characters
    if use_special:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Ensure at least one character from each required group
    # This guarantees the password meets basic complexity requirements
    password_chars = []
    password_chars.append(random.choice(string.ascii_lowercase))   # At least 1 lowercase
    password_chars.append(random.choice(string.ascii_uppercase))   # At least 1 uppercase
    password_chars.append(random.choice(string.digits))            # At least 1 digit
    if use_special:
        password_chars.append(random.choice("!@#$%^&*()_+-="))    # At least 1 special

    # Fill the remaining length with random characters
    remaining = length - len(password_chars)
    for _ in range(remaining):
        password_chars.append(random.choice(chars))

    # Shuffle to randomize the guaranteed characters' positions
    random.shuffle(password_chars)

    password = "".join(password_chars)

    return (
        f"Generated Password: {password}\n"
        f"  Length: {length}\n"
        f"  Special Characters: {'Yes' if use_special else 'No'}"
    )


# --- Tool: check_strength ---
@mcp.tool()
def check_strength(password: str) -> str:
    """Check the strength of a password.

    Args:
        password: The password to check
    """
    # Initialize score and feedback
    score = 0
    feedback = []

    # Check length
    length = len(password)
    if length >= 16:
        score += 3
        feedback.append("Excellent length (16+ characters)")
    elif length >= 12:
        score += 2
        feedback.append("Good length (12+ characters)")
    elif length >= 8:
        score += 1
        feedback.append("Acceptable length (8+ characters)")
    else:
        feedback.append("TOO SHORT - use at least 8 characters")

    # Check for lowercase letters
    has_lower = any(c in string.ascii_lowercase for c in password)
    if has_lower:
        score += 1
        feedback.append("Contains lowercase letters")
    else:
        feedback.append("MISSING lowercase letters")

    # Check for uppercase letters
    has_upper = any(c in string.ascii_uppercase for c in password)
    if has_upper:
        score += 1
        feedback.append("Contains uppercase letters")
    else:
        feedback.append("MISSING uppercase letters")

    # Check for digits
    has_digit = any(c in string.digits for c in password)
    if has_digit:
        score += 1
        feedback.append("Contains numbers")
    else:
        feedback.append("MISSING numbers")

    # Check for special characters
    special_chars = set("!@#$%^&*()_+-=[]{}|;:,.<>?/~`")
    has_special = any(c in special_chars for c in password)
    if has_special:
        score += 1
        feedback.append("Contains special characters")
    else:
        feedback.append("MISSING special characters")

    # Check for common patterns (weak indicators)
    common_patterns = ["123", "abc", "password", "qwerty", "111", "aaa"]
    has_pattern = any(p in password.lower() for p in common_patterns)
    if has_pattern:
        score -= 1
        feedback.append("WARNING: Contains common patterns")

    # Determine overall strength
    if score >= 6:
        strength = "STRONG"
    elif score >= 4:
        strength = "MODERATE"
    elif score >= 2:
        strength = "WEAK"
    else:
        strength = "VERY WEAK"

    # Build report
    lines = [f"Password Strength: {strength} (score: {score}/7)", ""]
    lines.append(f"  Length: {length} characters")
    lines.append(f"\n  Analysis:")
    for item in feedback:
        # Add checkmark or warning symbol
        if item.startswith("MISSING") or item.startswith("TOO") or item.startswith("WARNING"):
            lines.append(f"    [!] {item}")
        else:
            lines.append(f"    [+] {item}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Starting Password Generator Server...")
    print("Tools: generate_password, check_strength")
    mcp.run()
