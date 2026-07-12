"""
Mini Project: MCP Architecture Simulator
=========================================
A complete simulation of the MCP architecture including:
- Client and Server classes
- Transport layer
- Capability negotiation
- Request/Response handling
- Connection lifecycle
- Error handling
"""

import json
import time


# ============================================================
# Transport Layer - How messages travel between client and server
# ============================================================

class StdioTransport:
    """Simulates STDIO transport (messages passed as strings)."""

    def __init__(self):
        # In real MCP, messages go through stdin/stdout
        # Here we use a simple list as a message queue
        self.message_queue = []

    def send(self, message):
        """Send a message (add to queue)."""
        json_string = json.dumps(message)
        self.message_queue.append(json_string)
        return json_string

    def receive(self):
        """Receive a message (pop from queue)."""
        if len(self.message_queue) == 0:
            return None
        json_string = self.message_queue.pop(0)
        return json.loads(json_string)


# ============================================================
# Server - Exposes tools, resources, and prompts
# ============================================================

class MCPServer:
    """Simulates an MCP server with tools and resources."""

    def __init__(self, name):
        self.name = name
        self.tools = {}
        self.resources = {}
        self.transport = StdioTransport()

    def add_tool(self, tool_name, description, handler):
        """Register a tool with the server."""
        self.tools[tool_name] = {
            "name": tool_name,
            "description": description,
            "handler": handler,
        }

    def add_resource(self, uri, content):
        """Register a resource with the server."""
        self.resources[uri] = content

    def handle_request(self, request):
        """Process a request and return a response."""
        method = request.get("method", "")
        request_id = request.get("id")
        params = request.get("params", {})

        # Handle initialize
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "serverInfo": {"name": self.name},
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"listChanged": False},
                    }
                }
            }

        # Handle tools/list
        if method == "tools/list":
            tool_list = []
            for name, info in self.tools.items():
                tool_list.append({"name": name, "description": info["description"]})
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tool_list}
            }

        # Handle tools/call
        if method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }
            # Call the tool handler
            result = self.tools[tool_name]["handler"](arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": str(result)}]}
            }

        # Handle resources/read
        if method == "resources/read":
            uri = params.get("uri", "")
            if uri not in self.resources:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32602, "message": f"Resource not found: {uri}"}
                }
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"contents": [{"uri": uri, "text": self.resources[uri]}]}
            }

        # Unknown method
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


# ============================================================
# Client - Connects to server and uses capabilities
# ============================================================

class MCPClient:
    """Simulates an MCP client that connects to a server."""

    def __init__(self, name):
        self.name = name
        self.state = "disconnected"
        self.server = None
        self.request_id = 0

    def _next_id(self):
        """Generate the next request ID."""
        self.request_id = self.request_id + 1
        return self.request_id

    def connect(self, server):
        """Connect to an MCP server."""
        print(f"\n[{self.name}] Connecting to server '{server.name}'...")
        self.server = server
        self.state = "connecting"

        # Send initialize request
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "clientInfo": {"name": self.name},
                "capabilities": {}
            }
        }

        response = server.handle_request(request)

        if "result" in response:
            self.state = "ready"
            server_name = response["result"]["serverInfo"]["name"]
            caps = response["result"]["capabilities"]
            print(f"[{self.name}] Connected to '{server_name}'")
            print(f"[{self.name}] Server capabilities: {list(caps.keys())}")
            return True
        else:
            self.state = "error"
            print(f"[{self.name}] Connection failed")
            return False

    def list_tools(self):
        """List all tools available on the server."""
        if self.state != "ready":
            print(f"[{self.name}] ERROR: Not connected")
            return []

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }

        response = self.server.handle_request(request)
        tools = response["result"]["tools"]
        print(f"[{self.name}] Available tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        return tools

    def call_tool(self, tool_name, arguments):
        """Call a tool on the server."""
        if self.state != "ready":
            print(f"[{self.name}] ERROR: Not connected")
            return None

        print(f"[{self.name}] Calling tool '{tool_name}' with {arguments}")

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        }

        response = self.server.handle_request(request)

        if "error" in response:
            print(f"[{self.name}] ERROR: {response['error']['message']}")
            return None

        result = response["result"]["content"][0]["text"]
        print(f"[{self.name}] Result: {result}")
        return result

    def read_resource(self, uri):
        """Read a resource from the server."""
        if self.state != "ready":
            print(f"[{self.name}] ERROR: Not connected")
            return None

        print(f"[{self.name}] Reading resource '{uri}'")

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "resources/read",
            "params": {"uri": uri}
        }

        response = self.server.handle_request(request)

        if "error" in response:
            print(f"[{self.name}] ERROR: {response['error']['message']}")
            return None

        content = response["result"]["contents"][0]["text"]
        print(f"[{self.name}] Content: {content}")
        return content


# ============================================================
# Tool handler functions
# ============================================================

def calculator_add(args):
    a = args.get("a", 0)
    b = args.get("b", 0)
    return a + b


def calculator_multiply(args):
    a = args.get("a", 0)
    b = args.get("b", 0)
    return a * b


def get_greeting(args):
    name = args.get("name", "World")
    return f"Hello, {name}!"


# ============================================================
# Main - Run the simulation
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MCP Architecture Simulator")
    print("=" * 60)

    # Step 1: Create a server with tools and resources
    server = MCPServer("math-server")
    server.add_tool("add", "Add two numbers", calculator_add)
    server.add_tool("multiply", "Multiply two numbers", calculator_multiply)
    server.add_tool("greet", "Generate a greeting", get_greeting)
    server.add_resource("info://server", "Math Server v1.0 - Provides calculator tools")
    server.add_resource("info://help", "Use add(a,b) or multiply(a,b) for math operations")

    # Step 2: Create a client and connect
    client = MCPClient("my-client")
    client.connect(server)

    # Step 3: Discover capabilities
    print("\n--- Discovering Tools ---")
    client.list_tools()

    # Step 4: Use tools
    print("\n--- Using Tools ---")
    client.call_tool("add", {"a": 10, "b": 20})
    client.call_tool("multiply", {"a": 7, "b": 6})
    client.call_tool("greet", {"name": "MCP Student"})

    # Step 5: Try a tool that doesn't exist
    print("\n--- Error Handling ---")
    client.call_tool("divide", {"a": 10, "b": 2})

    # Step 6: Read resources
    print("\n--- Reading Resources ---")
    client.read_resource("info://server")
    client.read_resource("info://help")
    client.read_resource("info://nonexistent")

    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)
