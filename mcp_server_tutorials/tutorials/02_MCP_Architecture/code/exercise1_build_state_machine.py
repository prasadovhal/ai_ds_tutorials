"""
Exercise 1: Build a Connection State Machine
=============================================
YOUR TASK:
Create an MCP connection state machine with these states:
  - disconnected, connecting, connected, authenticated, error

Rules:
  - disconnected -> connecting
  - connecting -> connected OR error
  - connected -> authenticated OR error
  - authenticated -> disconnected (logout)
  - error -> disconnected (reset)

Requirements:
  1. Create a StateMachine class
  2. Add a transition() method that validates state changes
  3. Add a get_state() method
  4. Add a get_history() method that returns all state changes
  5. Test with valid and invalid transitions
"""

# YOUR CODE HERE


if __name__ == "__main__":
    # Test your state machine
    print("Exercise 1: Build a Connection State Machine")
    print("Implement the StateMachine class above")
    print("Then uncomment the test code below")

    # sm = StateMachine()
    # print(f"Initial state: {sm.get_state()}")
    # sm.transition("connecting")
    # sm.transition("connected")
    # sm.transition("authenticated")
    # sm.transition("disconnected")
    # print(f"History: {sm.get_history()}")
    #
    # # Try invalid transition
    # sm.transition("authenticated")  # Should fail: can't go from disconnected to authenticated
