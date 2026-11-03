"""
Example 2: MCP vs REST -- The N x M Integration Problem
========================================================
This file demonstrates WHY MCP exists by simulating the N x M problem.

Before MCP:
  - Every AI app needed custom code for every data source
  - 5 apps x 10 sources = 50 custom integrations

With MCP:
  - Every AI app implements one MCP client
  - Every data source implements one MCP server
  - 5 apps + 10 sources = 15 implementations

We simulate both approaches to show the difference.
No external dependencies needed -- just Python standard library.
"""

import json

# ============================================================
# PART 1: The OLD Way -- Custom Integrations (REST-style)
# ============================================================

print("=" * 70)
print("PART 1: WITHOUT MCP -- The N x M Integration Problem")
print("=" * 70)

# Imagine we have 3 AI applications
ai_apps = ["Claude Desktop", "Cursor", "VS Code Copilot"]

# And 4 data sources
data_sources = ["GitHub", "PostgreSQL", "Slack", "Filesystem"]

# Without MCP, each AI app needs CUSTOM code for each data source
# Let's simulate what those custom integrations look like

print("\nWithout MCP, every AI app needs custom integration code:\n")

# This dictionary represents all the custom integrations needed
# In real life, each of these would be hundreds of lines of unique code
custom_integrations = {}

for app in ai_apps:
    for source in data_sources:
        # Each integration has its own unique way of connecting
        integration_name = f"{app} <--> {source}"
        custom_integrations[integration_name] = {
            "app": app,
            "source": source,
            "status": "custom code required",
            "lines_of_code": 500,  # Estimate: each custom integration is ~500 lines
            "maintenance": "independent"
        }
        print(f"  Custom integration: {integration_name}")

total_custom = len(custom_integrations)
total_lines = total_custom * 500

print(f"\nTotal custom integrations needed: {total_custom}")
print(f"Estimated total lines of code: {total_lines}")
print(f"Each integration must be built, tested, and maintained separately!")

# ============================================================
# PART 2: Simulating Custom REST Integrations
# ============================================================

print("\n" + "=" * 70)
print("PART 2: How Custom REST Integrations Work")
print("=" * 70)

# Each data source has a DIFFERENT API format
# The AI app must know how to talk to each one differently

print("\n--- GitHub uses REST with bearer token ---")
github_request = {
    "method": "GET",
    "url": "https://api.github.com/repos/user/repo/issues",
    "headers": {
        "Authorization": "Bearer github_token_123",
        "Accept": "application/vnd.github.v3+json"
    }
}
print(json.dumps(github_request, indent=2))

print("\n--- PostgreSQL uses SQL over TCP ---")
postgres_request = {
    "protocol": "PostgreSQL wire protocol",
    "host": "localhost",
    "port": 5432,
    "query": "SELECT * FROM users WHERE active = true",
    "auth": "username/password"
}
print(json.dumps(postgres_request, indent=2))

print("\n--- Slack uses REST with OAuth ---")
slack_request = {
    "method": "POST",
    "url": "https://slack.com/api/chat.postMessage",
    "headers": {
        "Authorization": "Bearer xoxb-slack-token",
        "Content-Type": "application/json"
    },
    "body": {
        "channel": "C123456",
        "text": "Hello from AI!"
    }
}
print(json.dumps(slack_request, indent=2))

print("\n--- Filesystem uses OS system calls ---")
filesystem_request = {
    "protocol": "OS system call",
    "operation": "open + read",
    "path": "/home/user/document.txt",
    "auth": "file system permissions"
}
print(json.dumps(filesystem_request, indent=2))

print("\nNotice: EVERY data source has a DIFFERENT:")
print("  - Protocol (REST, SQL, system calls)")
print("  - Authentication method (token, password, permissions)")
print("  - Data format (JSON, SQL results, file bytes)")
print("  - Error handling (HTTP codes, SQL errors, OS errors)")
print("\nThe AI app must handle ALL of these differently!")

# ============================================================
# PART 3: The MCP Way -- One Protocol for Everything
# ============================================================

print("\n" + "=" * 70)
print("PART 3: WITH MCP -- One Protocol for Everything")
print("=" * 70)

# With MCP, every data source is accessed the SAME way
# The MCP server handles the translation to the native protocol

print("\nWith MCP, every tool call looks THE SAME:\n")

# Calling GitHub through MCP
github_mcp = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "list_issues",
        "arguments": {"repo": "user/repo"}
    }
}
print("--- GitHub via MCP ---")
print(json.dumps(github_mcp, indent=2))

# Calling PostgreSQL through MCP
postgres_mcp = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "run_query",
        "arguments": {"sql": "SELECT * FROM users WHERE active = true"}
    }
}
print("\n--- PostgreSQL via MCP ---")
print(json.dumps(postgres_mcp, indent=2))

# Calling Slack through MCP
slack_mcp = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "send_message",
        "arguments": {"channel": "general", "text": "Hello from AI!"}
    }
}
print("\n--- Slack via MCP ---")
print(json.dumps(slack_mcp, indent=2))

# Calling Filesystem through MCP
filesystem_mcp = {
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
        "name": "read_file",
        "arguments": {"path": "/home/user/document.txt"}
    }
}
print("\n--- Filesystem via MCP ---")
print(json.dumps(filesystem_mcp, indent=2))

print("\nNotice: EVERY call uses the SAME:")
print('  - Protocol (JSON-RPC 2.0)')
print('  - Method ("tools/call")')
print('  - Structure (name + arguments)')
print('  - Error handling (JSON-RPC error codes)')
print("\nThe AI app only needs to know ONE protocol!")

# ============================================================
# PART 4: Counting the Integration Savings
# ============================================================

print("\n" + "=" * 70)
print("PART 4: Integration Count Comparison")
print("=" * 70)

# Let's calculate with different numbers to show the scaling advantage

print("\n{:<20} {:<20} {:<20} {:<20}".format(
    "AI Apps (N)", "Sources (M)", "Without MCP (NxM)", "With MCP (N+M)"
))
print("-" * 80)

test_cases = [
    (3, 4),
    (5, 10),
    (10, 20),
    (20, 50),
    (50, 100),
]

for n_apps, m_sources in test_cases:
    without_mcp = n_apps * m_sources
    with_mcp = n_apps + m_sources
    savings = without_mcp - with_mcp
    print("{:<20} {:<20} {:<20} {:<20}".format(
        n_apps, m_sources, without_mcp, f"{with_mcp} (saved {savings})"
    ))

# ============================================================
# PART 5: Tool Discovery -- MCP's Killer Feature
# ============================================================

print("\n" + "=" * 70)
print("PART 5: Tool Discovery -- MCP's Killer Feature")
print("=" * 70)

print("""
With REST APIs, the AI model needs to be told about every API endpoint
in advance. Someone has to write documentation, and the developer has
to hardcode which APIs are available.

With MCP, the AI model can DISCOVER tools automatically by calling
tools/list. This is like walking into a hardware store and asking
"what tools do you have?" instead of bringing a shopping list.
""")

# Simulate tool discovery
print("--- AI App sends tools/list to the GitHub MCP Server ---")
tools_list_request = {
    "jsonrpc": "2.0",
    "id": 10,
    "method": "tools/list"
}
print(json.dumps(tools_list_request, indent=2))

print("\n--- Server responds with all available tools ---")
tools_list_response = {
    "jsonrpc": "2.0",
    "id": 10,
    "result": {
        "tools": [
            {
                "name": "list_repos",
                "description": "List repositories for a user or organization"
            },
            {
                "name": "create_issue",
                "description": "Create a new issue in a repository"
            },
            {
                "name": "search_code",
                "description": "Search for code across repositories"
            },
            {
                "name": "get_pull_request",
                "description": "Get details of a pull request"
            }
        ]
    }
}
print(json.dumps(tools_list_response, indent=2))

print("\nThe AI model now KNOWS what tools are available!")
print("It can decide which tool to use based on the user's request.")
print("No hardcoding. No documentation reading. Automatic discovery.")

# ============================================================
# PART 6: Summary
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY: Why MCP Beats Custom Integrations")
print("=" * 70)

print("""
+----------------------+----------------------------+----------------------------+
| Feature              | Custom REST Integrations   | MCP                        |
+----------------------+----------------------------+----------------------------+
| Protocol             | Different for each source  | One protocol (JSON-RPC)    |
| Authentication       | Different for each source  | Handled by MCP server      |
| Tool Discovery       | Manual (read docs)         | Automatic (tools/list)     |
| Error Handling       | Different for each source  | Standard error codes       |
| Maintenance          | N x M codebases            | N + M codebases            |
| Reusability          | None                       | Any client can use any     |
|                      |                            | server                     |
| Security             | Different models           | Standard security model    |
+----------------------+----------------------------+----------------------------+
""")


if __name__ == "__main__":
    # This file runs automatically when executed
    # All the code above runs at module level for simplicity
    pass
