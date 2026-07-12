"""
Example 2: Capability Negotiation Simulation
=============================================
This file demonstrates how MCP clients and servers negotiate capabilities.

Capability negotiation is like two people meeting for the first time:
- "I can speak English and French" (client capabilities)
- "I can speak English and Spanish" (server capabilities)
- "Great, let's communicate in English" (negotiated common ground)

In MCP, during the initialization phase:
- The client tells the server what CLIENT features it supports
- The server tells the client what SERVER features it offers
- Both sides store this information and use it to decide what they can do

This is NOT about finding common features. It is about each side
ADVERTISING its own features so the other side knows what to expect.

No external dependencies needed -- just plain Python.
"""

import json


# ============================================================
# PART 1: Define What Capabilities Exist
# ============================================================

# These are the possible SERVER capabilities in MCP.
# A server does not have to support all of them.
# During initialization, it tells the client which ones it supports.

SERVER_CAPABILITY_DEFINITIONS = {
    "tools": {
        "description": "Server can execute tools (functions)",
        "sub_capabilities": {
            "listChanged": "Server will notify when tool list changes",
        },
    },
    "resources": {
        "description": "Server can serve data resources",
        "sub_capabilities": {
            "subscribe": "Client can subscribe to resource changes",
            "listChanged": "Server will notify when resource list changes",
        },
    },
    "prompts": {
        "description": "Server can provide prompt templates",
        "sub_capabilities": {
            "listChanged": "Server will notify when prompt list changes",
        },
    },
    "logging": {
        "description": "Server supports logging",
        "sub_capabilities": {},
    },
}

# These are the possible CLIENT capabilities in MCP.
CLIENT_CAPABILITY_DEFINITIONS = {
    "roots": {
        "description": "Client can provide root URIs (workspace folders)",
        "sub_capabilities": {
            "listChanged": "Client will notify when roots change",
        },
    },
    "sampling": {
        "description": "Client supports LLM sampling requests from server",
        "sub_capabilities": {},
    },
}


# ============================================================
# PART 2: Server Capability Advertiser
# ============================================================

class CapabilityServer:
    """
    Simulates a server that advertises its capabilities.

    Different servers have different capabilities.
    A file server might have tools and resources but no prompts.
    A prompt library might have only prompts.
    """

    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.capabilities = {}
        print(f"[SERVER] Created: {name} v{version}")

    def enable_tools(self, list_changed=False):
        """Enable the tools capability."""
        # This means the server has tools that clients can call
        self.capabilities["tools"] = {}
        if list_changed:
            self.capabilities["tools"]["listChanged"] = True
        print(f"[SERVER] Enabled capability: tools (listChanged={list_changed})")

    def enable_resources(self, subscribe=False, list_changed=False):
        """Enable the resources capability."""
        # This means the server has data resources clients can read
        self.capabilities["resources"] = {}
        if subscribe:
            self.capabilities["resources"]["subscribe"] = True
        if list_changed:
            self.capabilities["resources"]["listChanged"] = True
        print(f"[SERVER] Enabled capability: resources (subscribe={subscribe}, listChanged={list_changed})")

    def enable_prompts(self, list_changed=False):
        """Enable the prompts capability."""
        # This means the server has prompt templates
        self.capabilities["prompts"] = {}
        if list_changed:
            self.capabilities["prompts"]["listChanged"] = True
        print(f"[SERVER] Enabled capability: prompts (listChanged={list_changed})")

    def enable_logging(self):
        """Enable the logging capability."""
        self.capabilities["logging"] = {}
        print(f"[SERVER] Enabled capability: logging")

    def get_initialize_response(self, request_id):
        """
        Build the initialization response.

        This is what the server sends back when it receives
        an 'initialize' request from the client.
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                },
                "capabilities": self.capabilities,
            },
        }
        return response


# ============================================================
# PART 3: Client Capability Checker
# ============================================================

class CapabilityClient:
    """
    Simulates a client that checks server capabilities.

    After initialization, the client stores the server's capabilities
    and uses them to decide what operations are allowed.
    """

    def __init__(self, name):
        self.name = name
        self.client_capabilities = {}
        self.server_capabilities = None
        self.server_info = None
        print(f"[CLIENT] Created: {name}")

    def enable_roots(self, list_changed=False):
        """Enable the roots capability on the client."""
        self.client_capabilities["roots"] = {}
        if list_changed:
            self.client_capabilities["roots"]["listChanged"] = True
        print(f"[CLIENT] Enabled capability: roots (listChanged={list_changed})")

    def enable_sampling(self):
        """Enable the sampling capability on the client."""
        self.client_capabilities["sampling"] = {}
        print(f"[CLIENT] Enabled capability: sampling")

    def build_initialize_request(self, request_id):
        """
        Build the initialization request.

        This is what the client sends to start the handshake.
        """
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": self.client_capabilities,
                "clientInfo": {
                    "name": self.name,
                    "version": "1.0.0",
                },
            },
        }
        return request

    def process_initialize_response(self, response):
        """
        Process the server's initialization response.

        The client stores the server's capabilities so it knows
        what operations are available.
        """
        if "error" in response:
            print(f"[CLIENT] Initialization FAILED: {response['error']['message']}")
            return False

        result = response.get("result", {})
        self.server_capabilities = result.get("capabilities", {})
        self.server_info = result.get("serverInfo", {})

        print(f"\n[CLIENT] Server: {self.server_info.get('name')} v{self.server_info.get('version')}")
        print(f"[CLIENT] Server capabilities received:")

        # Print each capability the server supports
        for capability_name, capability_details in self.server_capabilities.items():
            print(f"  - {capability_name}: {capability_details}")

        return True

    def can_use_tools(self):
        """Check if the server supports tools."""
        if self.server_capabilities is None:
            print("[CLIENT] ERROR: Not initialized yet!")
            return False
        has_tools = "tools" in self.server_capabilities
        print(f"[CLIENT] Can use tools? {has_tools}")
        return has_tools

    def can_use_resources(self):
        """Check if the server supports resources."""
        if self.server_capabilities is None:
            print("[CLIENT] ERROR: Not initialized yet!")
            return False
        has_resources = "resources" in self.server_capabilities
        print(f"[CLIENT] Can use resources? {has_resources}")
        return has_resources

    def can_subscribe_to_resources(self):
        """Check if the server supports resource subscriptions."""
        if self.server_capabilities is None:
            print("[CLIENT] ERROR: Not initialized yet!")
            return False

        resources_cap = self.server_capabilities.get("resources", {})
        can_subscribe = resources_cap.get("subscribe", False)
        print(f"[CLIENT] Can subscribe to resources? {can_subscribe}")
        return can_subscribe

    def can_use_prompts(self):
        """Check if the server supports prompts."""
        if self.server_capabilities is None:
            print("[CLIENT] ERROR: Not initialized yet!")
            return False
        has_prompts = "prompts" in self.server_capabilities
        print(f"[CLIENT] Can use prompts? {has_prompts}")
        return has_prompts


# ============================================================
# PART 4: Run the Negotiation
# ============================================================

def run_negotiation(server, client):
    """
    Run the full capability negotiation between a client and server.
    """
    print("\n" + "=" * 60)
    print("CAPABILITY NEGOTIATION")
    print("=" * 60)

    # Step 1: Client builds the initialize request
    request = client.build_initialize_request(request_id=1)
    print(f"\n[STEP 1] Client sends initialize request:")
    print(json.dumps(request, indent=2))

    # Step 2: Server builds the initialize response
    response = server.get_initialize_response(request_id=1)
    print(f"\n[STEP 2] Server sends initialize response:")
    print(json.dumps(response, indent=2))

    # Step 3: Client processes the response
    print(f"\n[STEP 3] Client processes server capabilities:")
    client.process_initialize_response(response)

    # Step 4: Client checks what it can do
    print(f"\n[STEP 4] Client checks available features:")
    client.can_use_tools()
    client.can_use_resources()
    client.can_subscribe_to_resources()
    client.can_use_prompts()


if __name__ == "__main__":

    # ========================================================
    # Scenario 1: Full-featured server
    # ========================================================
    print("=" * 60)
    print("SCENARIO 1: Full-Featured Server")
    print("A server that supports everything")
    print("=" * 60)

    server1 = CapabilityServer("full-server", "1.0.0")
    server1.enable_tools(list_changed=True)
    server1.enable_resources(subscribe=True, list_changed=True)
    server1.enable_prompts(list_changed=True)
    server1.enable_logging()

    client1 = CapabilityClient("full-client")
    client1.enable_roots(list_changed=True)
    client1.enable_sampling()

    run_negotiation(server1, client1)

    # ========================================================
    # Scenario 2: Tools-only server
    # ========================================================
    print("\n\n" + "=" * 60)
    print("SCENARIO 2: Tools-Only Server")
    print("A server that only has tools (no resources, no prompts)")
    print("=" * 60)

    server2 = CapabilityServer("calculator-server", "1.0.0")
    server2.enable_tools(list_changed=False)
    # Note: NO resources or prompts enabled

    client2 = CapabilityClient("simple-client")
    # Note: NO client capabilities enabled

    run_negotiation(server2, client2)

    # ========================================================
    # Scenario 3: Resources-only server (no subscriptions)
    # ========================================================
    print("\n\n" + "=" * 60)
    print("SCENARIO 3: Resources-Only Server (No Subscriptions)")
    print("A server that has resources but does NOT support subscriptions")
    print("=" * 60)

    server3 = CapabilityServer("data-server", "2.0.0")
    server3.enable_resources(subscribe=False, list_changed=True)
    # Note: subscribe=False -- client cannot subscribe to changes

    client3 = CapabilityClient("data-client")

    run_negotiation(server3, client3)

    # ========================================================
    # Summary
    # ========================================================
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("Capability negotiation ensures both sides know what to expect:")
    print()
    print("- Server 1 (full): tools, resources (with subscribe), prompts, logging")
    print("- Server 2 (calc): tools only")
    print("- Server 3 (data): resources only (no subscriptions)")
    print()
    print("The client checks capabilities BEFORE trying to use features.")
    print("This prevents errors from calling unsupported methods.")
