"""
Example 1: Client-Server Model Simulation
==========================================
This file simulates how an MCP client and server communicate.

We will NOT use the actual MCP SDK here. Instead, we build simple Python
classes that mimic what the real MCP client and server do internally.

This helps you understand the PATTERN before seeing the real implementation.

Think of this as building a toy car before working on a real engine.
The toy teaches you the principles without the complexity.

No external dependencies needed -- just plain Python.
"""


# ============================================================
# PART 1: The Server Class
# ============================================================
# The server is like a kitchen in a restaurant.
# It has tools (things it can DO) and resources (data it HAS).
# It receives requests and sends back responses.

class SimpleServer:
    """
    A simple simulation of an MCP server.

    In real MCP, the server:
    - Registers tools, resources, and prompts
    - Receives JSON-RPC requests
    - Processes them and returns JSON-RPC responses

    Our simulation does the same thing with plain Python dicts.
    """

    def __init__(self, name, version):
        # Every server has a name and version
        # This is sent to the client during initialization
        self.name = name
        self.version = version

        # Tools are stored in a dictionary
        # Key = tool name, Value = a function that does the work
        self.tools = {}

        # Resources are stored in a dictionary
        # Key = resource URI, Value = the resource data
        self.resources = {}

        # Track whether the server has been initialized
        self.initialized = False

        print(f"[SERVER] Created server: {self.name} v{self.version}")

    def register_tool(self, tool_name, description, handler_function):
        """
        Register a tool that the server can execute.

        In real MCP, tools are registered with:
        - A name (unique identifier)
        - A description (what the tool does)
        - An input schema (what arguments it accepts)
        - A handler function (the code that runs)
        """
        self.tools[tool_name] = {
            "name": tool_name,
            "description": description,
            "handler": handler_function,
        }
        print(f"[SERVER] Registered tool: {tool_name}")

    def register_resource(self, uri, content):
        """
        Register a resource that the server can serve.

        In real MCP, resources are identified by URIs like:
        - file:///data/report.csv
        - db://users/table
        """
        self.resources[uri] = {
            "uri": uri,
            "content": content,
        }
        print(f"[SERVER] Registered resource: {uri}")

    def handle_request(self, request):
        """
        Process an incoming request and return a response.

        This is the core of the server. It receives a dict (simulating
        a JSON-RPC message) and returns a response dict.
        """
        # Extract the method from the request
        method = request.get("method", "")

        # Extract the request ID (needed to match the response)
        request_id = request.get("id")

        print(f"\n[SERVER] Received request: method={method}, id={request_id}")

        # Route the request to the correct handler
        # This is like a kitchen receiving different types of orders
        if method == "initialize":
            return self._handle_initialize(request_id, request.get("params", {}))

        elif method == "tools/list":
            return self._handle_tools_list(request_id)

        elif method == "tools/call":
            return self._handle_tools_call(request_id, request.get("params", {}))

        elif method == "resources/list":
            return self._handle_resources_list(request_id)

        elif method == "resources/read":
            return self._handle_resources_read(request_id, request.get("params", {}))

        else:
            # Method not found -- return an error
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }

    def _handle_initialize(self, request_id, params):
        """Handle the initialize request."""
        self.initialized = True

        # Return server info and capabilities
        # This tells the client what the server can do
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                },
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": True},
                },
            },
        }

    def _handle_tools_list(self, request_id):
        """Handle the tools/list request."""
        # Build a list of tool descriptions (without the handler functions)
        tool_list = []
        for tool_name, tool_info in self.tools.items():
            tool_list.append({
                "name": tool_info["name"],
                "description": tool_info["description"],
            })

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tool_list},
        }

    def _handle_tools_call(self, request_id, params):
        """Handle the tools/call request."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        # Check if the tool exists
        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}",
                },
            }

        # Execute the tool
        # In real MCP, this would call the registered handler function
        handler = self.tools[tool_name]["handler"]
        result = handler(arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": str(result)}],
            },
        }

    def _handle_resources_list(self, request_id):
        """Handle the resources/list request."""
        resource_list = []
        for uri, resource_info in self.resources.items():
            resource_list.append({"uri": resource_info["uri"]})

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"resources": resource_list},
        }

    def _handle_resources_read(self, request_id, params):
        """Handle the resources/read request."""
        uri = params.get("uri", "")

        if uri not in self.resources:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {uri}",
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "text": self.resources[uri]["content"],
                    }
                ],
            },
        }


# ============================================================
# PART 2: The Client Class
# ============================================================
# The client is like a waiter in a restaurant.
# It sends requests to the server and receives responses.
# It keeps track of request IDs to match responses.

class SimpleClient:
    """
    A simple simulation of an MCP client.

    In real MCP, the client:
    - Connects to a server via a transport (stdio or HTTP)
    - Sends JSON-RPC requests
    - Receives JSON-RPC responses
    - Tracks server capabilities

    Our simulation passes messages directly (no real transport).
    """

    def __init__(self, name):
        self.name = name

        # Request ID counter -- incremented for each request
        # This ensures every request has a unique ID
        self.next_request_id = 1

        # Reference to the connected server
        # In real MCP, this would be a transport connection
        self.server = None

        # Store the server's capabilities after initialization
        self.server_capabilities = None

        # Store the server's info after initialization
        self.server_info = None

        print(f"[CLIENT] Created client: {self.name}")

    def connect(self, server):
        """
        Connect to a server.

        In real MCP, this would:
        - Launch the server process (STDIO) or open an HTTP connection
        - Establish the transport channel

        Our simulation just stores a reference to the server object.
        """
        self.server = server
        print(f"[CLIENT] Connected to server")

    def send_request(self, method, params=None):
        """
        Send a request to the server and return the response.

        This is the core method of the client.
        It builds a JSON-RPC request, sends it to the server,
        and returns the response.
        """
        # Build the JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": self.next_request_id,
            "method": method,
        }

        # Add params if provided
        if params is not None:
            request["params"] = params

        print(f"\n[CLIENT] Sending request: method={method}, id={self.next_request_id}")

        # Increment the request ID for the next request
        self.next_request_id = self.next_request_id + 1

        # Send to server and get response
        # In real MCP, this goes through the transport layer
        response = self.server.handle_request(request)

        # Check if the response is an error
        if "error" in response:
            print(f"[CLIENT] Received ERROR: {response['error']['message']}")
        else:
            print(f"[CLIENT] Received SUCCESS response for id={response['id']}")

        return response

    def initialize(self):
        """
        Perform the initialization handshake.

        This is always the first thing the client does after connecting.
        """
        print("\n" + "=" * 60)
        print("[CLIENT] Starting initialization handshake...")
        print("=" * 60)

        # Step 1: Send initialize request
        response = self.send_request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {
                "name": self.name,
                "version": "1.0.0",
            },
        })

        # Step 2: Store server capabilities and info
        if "result" in response:
            self.server_capabilities = response["result"].get("capabilities", {})
            self.server_info = response["result"].get("serverInfo", {})

            print(f"\n[CLIENT] Server name: {self.server_info.get('name')}")
            print(f"[CLIENT] Server version: {self.server_info.get('version')}")
            print(f"[CLIENT] Server capabilities: {self.server_capabilities}")

        # Step 3: Send initialized notification
        # Note: In real MCP, this is a notification (no id, no response expected)
        # Our simulation sends it as a regular message for simplicity
        print("\n[CLIENT] Sending 'initialized' notification")
        print("[CLIENT] Initialization complete! Connection is READY.")

    def list_tools(self):
        """List all tools available on the server."""
        response = self.send_request("tools/list")
        if "result" in response:
            tools = response["result"].get("tools", [])
            print(f"[CLIENT] Available tools: {[t['name'] for t in tools]}")
            return tools
        return []

    def call_tool(self, tool_name, arguments=None):
        """Call a tool on the server."""
        if arguments is None:
            arguments = {}

        response = self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments,
        })

        if "result" in response:
            content = response["result"].get("content", [])
            if content:
                print(f"[CLIENT] Tool result: {content[0].get('text', '')}")
                return content[0].get("text", "")
        return None

    def list_resources(self):
        """List all resources available on the server."""
        response = self.send_request("resources/list")
        if "result" in response:
            resources = response["result"].get("resources", [])
            print(f"[CLIENT] Available resources: {[r['uri'] for r in resources]}")
            return resources
        return []

    def read_resource(self, uri):
        """Read a resource from the server."""
        response = self.send_request("resources/read", {"uri": uri})
        if "result" in response:
            contents = response["result"].get("contents", [])
            if contents:
                print(f"[CLIENT] Resource content: {contents[0].get('text', '')[:100]}...")
                return contents[0].get("text", "")
        return None


# ============================================================
# PART 3: Putting It All Together
# ============================================================

def add_numbers(arguments):
    """A simple tool that adds two numbers."""
    a = arguments.get("a", 0)
    b = arguments.get("b", 0)
    return a + b


def get_greeting(arguments):
    """A simple tool that returns a greeting."""
    name = arguments.get("name", "World")
    return f"Hello, {name}! Welcome to MCP."


if __name__ == "__main__":
    print("=" * 60)
    print("MCP CLIENT-SERVER MODEL SIMULATION")
    print("=" * 60)

    # --- Step 1: Create the server ---
    # This is like building a kitchen
    server = SimpleServer("math-server", "1.0.0")

    # --- Step 2: Register tools on the server ---
    # This is like stocking the kitchen with equipment
    server.register_tool("add", "Add two numbers together", add_numbers)
    server.register_tool("greet", "Generate a greeting message", get_greeting)

    # --- Step 3: Register resources on the server ---
    # This is like stocking the kitchen with ingredients
    server.register_resource("data://info", "This server does math and greetings.")
    server.register_resource("data://version", "Version 1.0.0, released 2025.")

    # --- Step 4: Create the client ---
    # This is like hiring a waiter
    client = SimpleClient("my-client")

    # --- Step 5: Connect client to server ---
    # This is like the waiter walking into the kitchen
    client.connect(server)

    # --- Step 6: Initialize the connection ---
    # This is like the waiter introducing themselves to the kitchen staff
    client.initialize()

    # --- Step 7: List available tools ---
    print("\n" + "=" * 60)
    print("LISTING TOOLS")
    print("=" * 60)
    client.list_tools()

    # --- Step 8: Call a tool ---
    print("\n" + "=" * 60)
    print("CALLING TOOLS")
    print("=" * 60)
    client.call_tool("add", {"a": 15, "b": 27})
    client.call_tool("greet", {"name": "Prasad"})

    # --- Step 9: Try calling a tool that does not exist ---
    print("\n" + "=" * 60)
    print("CALLING NON-EXISTENT TOOL (ERROR CASE)")
    print("=" * 60)
    client.call_tool("multiply", {"a": 3, "b": 4})

    # --- Step 10: List and read resources ---
    print("\n" + "=" * 60)
    print("LISTING AND READING RESOURCES")
    print("=" * 60)
    client.list_resources()
    client.read_resource("data://info")

    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print("\nThis simulation showed how MCP client and server communicate.")
    print("The real MCP SDK does exactly this, but with actual transport")
    print("(stdio or HTTP) instead of direct function calls.")
