"""
Example 5: MCP Connection Lifecycle
====================================
This simulates the full lifecycle of an MCP connection:
  disconnected → connecting → initializing → ready → shutting_down → disconnected

Each state transition has rules about what is allowed.
"""

import json
import time


# Define all possible states
DISCONNECTED = "disconnected"
CONNECTING = "connecting"
INITIALIZING = "initializing"
READY = "ready"
SHUTTING_DOWN = "shutting_down"

# Define valid state transitions
# Key = current state, Value = list of states you can move to
VALID_TRANSITIONS = {
    DISCONNECTED: [CONNECTING],
    CONNECTING: [INITIALIZING, DISCONNECTED],
    INITIALIZING: [READY, DISCONNECTED],
    READY: [SHUTTING_DOWN],
    SHUTTING_DOWN: [DISCONNECTED],
}


class MCPConnection:
    """Simulates an MCP connection with proper state management."""

    def __init__(self, name):
        self.name = name
        self.state = DISCONNECTED
        self.capabilities = {}
        self.log = []

    def _record(self, message):
        """Record an event in the connection log."""
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {self.name}: {message}"
        self.log.append(entry)
        print(entry)

    def _transition(self, new_state):
        """Move to a new state if the transition is valid."""
        allowed = VALID_TRANSITIONS.get(self.state, [])
        if new_state not in allowed:
            self._record(f"ERROR: Cannot go from {self.state} to {new_state}")
            return False

        old_state = self.state
        self.state = new_state
        self._record(f"State changed: {old_state} -> {new_state}")
        return True

    def connect(self):
        """Start the connection process."""
        self._record("Attempting to connect...")
        return self._transition(CONNECTING)

    def initialize(self, client_capabilities):
        """Send initialize request and negotiate capabilities."""
        if self.state != CONNECTING:
            self._record("ERROR: Must be in CONNECTING state to initialize")
            return False

        self._transition(INITIALIZING)

        # Simulate capability negotiation
        server_capabilities = {
            "tools": True,
            "resources": True,
            "prompts": True,
        }

        # Find common capabilities
        self.capabilities = {}
        for key in server_capabilities:
            if key in client_capabilities and client_capabilities[key]:
                self.capabilities[key] = True

        self._record(f"Negotiated capabilities: {list(self.capabilities.keys())}")
        return self._transition(READY)

    def call_tool(self, tool_name, arguments):
        """Call a tool (only works in READY state)."""
        if self.state != READY:
            self._record(f"ERROR: Cannot call tools in {self.state} state")
            return None

        self._record(f"Calling tool: {tool_name}({arguments})")

        # Simulate tool execution
        result = f"Result from {tool_name}"
        self._record(f"Tool returned: {result}")
        return result

    def shutdown(self):
        """Gracefully shut down the connection."""
        self._record("Initiating shutdown...")
        if self._transition(SHUTTING_DOWN):
            self._record("Cleaning up resources...")
            self._record("Flushing logs...")
            return self._transition(DISCONNECTED)
        return False


if __name__ == "__main__":
    print("=== MCP Connection Lifecycle Simulation ===\n")

    # Create a connection
    conn = MCPConnection("MyConnection")

    # Step 1: Connect
    conn.connect()

    # Step 2: Initialize with capabilities
    client_caps = {"tools": True, "resources": True, "prompts": False}
    conn.initialize(client_caps)

    # Step 3: Use the connection (call tools)
    conn.call_tool("calculator_add", {"a": 5, "b": 3})
    conn.call_tool("get_weather", {"city": "London"})

    # Step 4: Shutdown
    conn.shutdown()

    # Step 5: Try to call a tool after shutdown (should fail)
    print("\n--- Trying to use connection after shutdown ---")
    conn.call_tool("calculator_add", {"a": 1, "b": 2})

    # Print full log
    print("\n=== Full Connection Log ===")
    for entry in conn.log:
        print(f"  {entry}")
