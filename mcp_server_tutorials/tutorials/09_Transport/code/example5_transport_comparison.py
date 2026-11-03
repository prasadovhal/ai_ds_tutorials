"""
Example 5: Transport Comparison
================================
Compares the different MCP transport options side by side.
This is a reference script — run it to see the comparison table.
"""


def print_comparison():
    """Print a detailed comparison of MCP transports."""

    print("=" * 80)
    print("MCP Transport Comparison")
    print("=" * 80)

    # Header
    print(f"\n{'Feature':<25} {'STDIO':<20} {'SSE (HTTP+SSE)':<20} {'Streamable HTTP':<20}")
    print("-" * 85)

    # Rows
    rows = [
        ("How it works", "stdin/stdout pipes", "HTTP + event stream", "HTTP POST/GET"),
        ("Server start", "Client launches it", "Runs independently", "Runs independently"),
        ("Network support", "Local only", "Local + Remote", "Local + Remote"),
        ("Multiple clients", "No (1:1)", "Yes", "Yes"),
        ("Firewall friendly", "N/A (local)", "Yes (HTTP)", "Yes (HTTP)"),
        ("Streaming", "Yes", "Yes (SSE)", "Yes"),
        ("Complexity", "Simple", "Medium", "Medium"),
        ("Best for", "CLI tools, IDEs", "Web apps, remote", "Modern apps"),
        ("Auth support", "None needed", "Headers/tokens", "Headers/tokens"),
        ("Default in SDK", "Yes", "No", "No"),
        ("Claude Desktop", "Yes", "No", "No"),
        ("VS Code", "Yes", "No", "No"),
        ("Web deployments", "No", "Yes", "Yes"),
    ]

    for row in rows:
        feature = row[0]
        stdio = row[1]
        sse = row[2]
        streamable = row[3]
        print(f"{feature:<25} {stdio:<20} {sse:<20} {streamable:<20}")

    print("\n" + "=" * 80)

    # When to use each
    print("\nWhen to use each transport:")
    print()
    print("STDIO (Standard I/O):")
    print("  - Local development and testing")
    print("  - IDE integrations (Claude Desktop, VS Code, Cursor)")
    print("  - CLI tools")
    print("  - When simplicity is the priority")
    print()
    print("SSE (Server-Sent Events over HTTP):")
    print("  - Remote server access")
    print("  - Web application backends")
    print("  - When multiple clients need to connect")
    print("  - When you need authentication via HTTP headers")
    print()
    print("Streamable HTTP:")
    print("  - Modern web deployments")
    print("  - Cloud-native applications")
    print("  - When you need the most flexibility")
    print("  - Newer alternative to SSE")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_comparison()
