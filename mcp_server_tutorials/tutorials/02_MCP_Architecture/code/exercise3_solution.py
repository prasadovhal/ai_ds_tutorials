"""
Exercise 3 Solution: Capability Matching System
"""


class CapabilityMatcher:
    """Matches client needs to server capabilities."""

    def __init__(self):
        # Store servers and their capabilities
        self.servers = {}
        # Store clients and their required capabilities
        self.clients = {}

    def register_server(self, server_name, capabilities):
        """Register a server with its capabilities."""
        self.servers[server_name] = capabilities
        print(f"Registered server '{server_name}' with capabilities: {capabilities}")

    def register_client(self, client_name, required_capabilities):
        """Register a client with its required capabilities."""
        self.clients[client_name] = required_capabilities
        print(f"Registered client '{client_name}' needing: {required_capabilities}")

    def match(self, client_name):
        """Find all servers that satisfy the client's requirements."""
        if client_name not in self.clients:
            print(f"Client '{client_name}' not found")
            return []

        required = self.clients[client_name]
        matching_servers = []

        for server_name, server_caps in self.servers.items():
            # Check if the server has ALL required capabilities
            has_all = True
            for req in required:
                if req not in server_caps:
                    has_all = False
                    break

            if has_all:
                matching_servers.append(server_name)

        return matching_servers

    def best_match(self, client_name):
        """Find the server with the most matching capabilities."""
        if client_name not in self.clients:
            return None

        required = self.clients[client_name]
        best_server = None
        best_score = 0

        for server_name, server_caps in self.servers.items():
            # Count how many required capabilities this server has
            score = 0
            for req in required:
                if req in server_caps:
                    score = score + 1

            if score > best_score:
                best_score = score
                best_server = server_name

        return best_server, best_score


if __name__ == "__main__":
    print("=== Capability Matching Solution ===\n")

    matcher = CapabilityMatcher()

    # Register servers
    print("--- Registering servers ---")
    matcher.register_server("basic-server", ["tools"])
    matcher.register_server("full-server", ["tools", "resources", "prompts"])
    matcher.register_server("data-server", ["resources", "prompts"])

    # Register clients
    print("\n--- Registering clients ---")
    matcher.register_client("simple-client", ["tools"])
    matcher.register_client("power-client", ["tools", "resources", "prompts"])
    matcher.register_client("reader-client", ["resources"])

    # Find matches
    print("\n--- Finding matches ---")
    for client_name in matcher.clients:
        matches = matcher.match(client_name)
        print(f"'{client_name}' can connect to: {matches}")

    # Find best match
    print("\n--- Best matches ---")
    for client_name in matcher.clients:
        best, score = matcher.best_match(client_name)
        total = len(matcher.clients[client_name])
        print(f"'{client_name}' best match: '{best}' ({score}/{total} capabilities)")
