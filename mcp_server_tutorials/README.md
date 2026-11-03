# MCP Server Tutorials

A complete course on **Model Context Protocol (MCP)** — from absolute beginner to production expert.

18 chapters, 234 code examples, exercises, and mini projects covering everything you need to build, deploy, secure, and integrate MCP servers into modern AI applications.

## Course Structure

| # | Chapter | Topics |
|---|---------|--------|
| 00 | [Course Overview](tutorials/00_Course_Overview.md) | 30-day learning plan, prerequisites, how to use this course |
| 01 | [Introduction to MCP](tutorials/01_Introduction_to_MCP/) | What is MCP, why MCP, history, ecosystem, JSON-RPC basics |
| 02 | [MCP Architecture](tutorials/02_MCP_Architecture/) | Client/Host/Server model, transport layer, capability negotiation |
| 03 | [Installing MCP](tutorials/03_Installing_MCP/) | Poetry setup, SDK installation, Hello World server and client |
| 04 | [Build First MCP Server](tutorials/04_Build_First_MCP_Server/) | Tools, resources, prompts — your first working server |
| 05 | [Build MCP Client](tutorials/05_Build_MCP_Client/) | Connecting, calling tools, reading resources, error handling |
| 06 | [Understanding Tools](tutorials/06_Understanding_Tools/) | Tool schema, validation, multiple tools, state management |
| 07 | [Resources](tutorials/07_Resources/) | Static/dynamic resources, files, JSON, CSV, caching |
| 08 | [Prompts](tutorials/08_Prompts/) | Prompt templates, parameters, composition, dynamic prompts |
| 09 | [Transport](tutorials/09_Transport/) | STDIO, SSE, Streamable HTTP — when to use what |
| 10 | [MCP Security](tutorials/10_MCP_Security/) | Auth, rate limiting, input validation, prompt injection defense |
| 11 | [Logging and Observability](tutorials/11_Logging_and_Observability/) | Structured logging, tracing, metrics, Langfuse |
| 12 | [Production MCP Server](tutorials/12_Production_MCP_Server/) | Config, error handling, Docker, testing, versioning |
| 13 | [Useful MCP Servers](tutorials/13_Useful_MCP_Servers/) | 12+ practical servers (calculator, weather, filesystem, SQLite, etc.) |
| 14 | [MCP in AI Applications](tutorials/14_MCP_in_AI_Applications/) | Claude Desktop, VS Code, Cursor, Continue.dev configuration |
| 15 | [Daily Life MCP Servers](tutorials/15_Daily_Life_MCP_Servers/) | Expense tracker, fitness, recipes, bookmarks, study planner |
| 16 | [MCP and AI Agents](tutorials/16_MCP_and_AI_Agents/) | LangChain, LangGraph, LlamaIndex, CrewAI, Pydantic AI |
| 17 | [Production Best Practices](tutorials/17_Production_Best_Practices/) | Testing pyramid, CI/CD, monitoring, caching, deployment |
| 18 | [Advanced MCP](tutorials/18_Advanced_MCP/) | Streaming, concurrency, server federation, distributed MCP |

## Each Chapter Contains

- Theory in Markdown (with Mermaid diagrams)
- 5 code examples
- 3 exercises with solutions
- 1 mini project
- Interview questions
- Production tips and common mistakes

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for package management
- Basic Python knowledge (functions, classes, file I/O)
- Familiarity with LLMs and AI agents (helpful but not required)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/mcp_server_tutorials.git
cd mcp_server_tutorials

# 2. Install Poetry (Windows)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# 3. Install dependencies
poetry install

# 4. Activate the virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 5. Run your first MCP server
poetry run python tutorials/04_Build_First_MCP_Server/code/example1_minimal_server.py
```

## Key Technologies

| Technology | Purpose |
|-----------|---------|
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | `mcp` package — server and client libraries |
| [FastMCP](https://github.com/modelcontextprotocol/python-sdk) | High-level API (`from mcp.server.fastmcp import FastMCP`) |
| [Poetry](https://python-poetry.org/) | Python package management |
| [Ollama](https://ollama.ai/) | Local LLM inference (free) |
| [HuggingFace](https://huggingface.co/) | Free models and APIs |

## MCP Server in VS Code

Add this to your VS Code MCP settings or `.vscode/settings.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "poetry",
      "args": ["run", "python", "path/to/server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

## API vs MCP

| Feature | Traditional API | MCP Server |
|---------|----------------|------------|
| Audience | Human developers | AI models and agents |
| Integration | Custom code per service | Build once, works with any MCP client |
| Discovery | Manual (reading docs) | Automatic (runtime capability negotiation) |
| Structure | Endpoints (REST, GraphQL) | Tools, Resources, and Prompts |
| Adaptability | Rigid | AI adapts to available tools dynamically |

## 30-Day Learning Plan

See the [Course Overview](tutorials/00_Course_Overview.md) for a day-by-day schedule that covers all 18 chapters in 30 days, including review days and project time.

## Project Structure

```
mcp_server_tutorials/
├── README.md
├── pyproject.toml
├── tutorials/
│   ├── 00_Course_Overview.md
│   ├── 01_Introduction_to_MCP/
│   │   ├── 01_Introduction_to_MCP.md    # Theory
│   │   └── code/                         # Examples, exercises, projects
│   ├── 02_MCP_Architecture/
│   │   ├── 02_MCP_Architecture.md
│   │   └── code/
│   ├── ...
│   └── 18_Advanced_MCP/
│       ├── 18_Advanced_MCP.md
│       └── code/
└── MCP_servers/                          # Standalone MCP servers
```

## License

This project is for educational purposes. Feel free to use the code examples for learning and building your own MCP servers.
