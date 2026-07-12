"""
Exercise 1 Solution: Build a Connection State Machine
"""


# Define valid transitions as a simple dictionary
VALID_TRANSITIONS = {
    "disconnected": ["connecting"],
    "connecting": ["connected", "error"],
    "connected": ["authenticated", "error"],
    "authenticated": ["disconnected"],
    "error": ["disconnected"],
}


class StateMachine:
    """A simple state machine for MCP connection states."""

    def __init__(self):
        # Start in disconnected state
        self.current_state = "disconnected"
        # Keep track of all state changes
        self.history = ["disconnected"]

    def get_state(self):
        """Return the current state."""
        return self.current_state

    def get_history(self):
        """Return the list of all states visited."""
        return self.history

    def transition(self, new_state):
        """Try to move to a new state. Returns True if successful."""
        # Get the list of allowed next states
        allowed = VALID_TRANSITIONS.get(self.current_state, [])

        # Check if the transition is valid
        if new_state not in allowed:
            print(f"  BLOCKED: Cannot go from '{self.current_state}' to '{new_state}'")
            print(f"  Allowed transitions: {allowed}")
            return False

        # Perform the transition
        old_state = self.current_state
        self.current_state = new_state
        self.history.append(new_state)
        print(f"  OK: {old_state} -> {new_state}")
        return True


if __name__ == "__main__":
    print("=== State Machine Solution ===\n")

    sm = StateMachine()
    print(f"Initial state: {sm.get_state()}\n")

    # Valid transitions
    print("--- Valid transitions ---")
    sm.transition("connecting")
    sm.transition("connected")
    sm.transition("authenticated")
    sm.transition("disconnected")

    # Invalid transition
    print("\n--- Invalid transition ---")
    sm.transition("authenticated")  # Can't go from disconnected to authenticated

    # Error flow
    print("\n--- Error flow ---")
    sm.transition("connecting")
    sm.transition("error")
    sm.transition("disconnected")

    # Print history
    print(f"\nFull history: {sm.get_history()}")
