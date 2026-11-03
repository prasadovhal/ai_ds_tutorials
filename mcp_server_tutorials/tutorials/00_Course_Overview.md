# MCP (Model Context Protocol) - Complete Course

## From Absolute Beginner to Production Expert

---

## About This Course

This course teaches you everything about the **Model Context Protocol (MCP)** — Anthropic's open standard for connecting AI models to external data sources and tools. By the end of this course, you will be able to design, build, deploy, debug, secure, and integrate production MCP servers into modern AI applications.

---

## Who Is This For?

- Senior Data Scientists and ML Engineers
- Python developers who know LLMs, RAG, LangChain, LangGraph
- Anyone who wants to become an MCP expert
- Developers building AI-powered applications

---

## Prerequisites

- Python 3.10+
- Basic understanding of LLMs and AI agents
- Familiarity with REST APIs
- Command line basics

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Primary language |
| Poetry | Package management |
| Ollama | Local LLM inference |
| HuggingFace | Free models and APIs |
| MCP Python SDK | Building MCP servers and clients |
| SQLite | Local database examples |
| Docker | Containerization |
| pytest | Testing |

---

## Course Structure

Every chapter contains:

1. **Theory** — Markdown file with concepts, diagrams, and explanations
2. **Code** — Python files with examples, exercises, and projects
3. **Exercises** — Hands-on practice problems with solutions
4. **Mini Project** — A small project to solidify learning
5. **Interview Questions** — Prepare for MCP-related interviews
6. **Production Tips** — Real-world advice

---

## Table of Contents

### Part 1: Foundations

| Chapter | Title | Description |
|---------|-------|-------------|
| 01 | [Introduction to MCP](01_Introduction_to_MCP/01_Introduction_to_MCP.md) | What is MCP, why it exists, core concepts, comparisons with REST/GraphQL |
| 02 | [MCP Architecture Deep Dive](02_MCP_Architecture/02_MCP_Architecture.md) | Client, Host, Server, Transport, Lifecycle, Security model |
| 03 | [Installing MCP](03_Installing_MCP/03_Installing_MCP.md) | Setup Poetry, install SDK, Hello World server and client |

### Part 2: Core Concepts

| Chapter | Title | Description |
|---------|-------|-------------|
| 04 | [Build First MCP Server](04_Build_First_MCP_Server/04_Build_First_MCP_Server.md) | Create server with tool, resource, and prompt |
| 05 | [Build MCP Client](05_Build_MCP_Client/05_Build_MCP_Client.md) | Connect to servers, call tools, read resources |
| 06 | [Understanding Tools](06_Understanding_Tools/06_Understanding_Tools.md) | Tool schemas, validation, errors, state management |

### Part 3: Server Capabilities

| Chapter | Title | Description |
|---------|-------|-------------|
| 07 | [Resources](07_Resources/07_Resources.md) | Static/dynamic resources, files, databases, caching |
| 08 | [Prompts](08_Prompts/08_Prompts.md) | Prompt templates, parameters, composition, best practices |
| 09 | [Transport](09_Transport/09_Transport.md) | STDIO, HTTP, SSE, WebSocket — when to use what |

### Part 4: Production Skills

| Chapter | Title | Description |
|---------|-------|-------------|
| 10 | [MCP Security](10_MCP_Security/10_MCP_Security.md) | Auth, OAuth, secrets, rate limiting, prompt injection defense |
| 11 | [Logging and Observability](11_Logging_and_Observability/11_Logging_and_Observability.md) | Logging, debugging, tracing, Langfuse, metrics |
| 12 | [Production MCP Server](12_Production_MCP_Server/12_Production_MCP_Server.md) | Folder structure, config, Docker, testing, deployment |

### Part 5: Practical Servers

| Chapter | Title | Description |
|---------|-------|-------------|
| 13 | [Useful MCP Servers](13_Useful_MCP_Servers/13_Useful_MCP_Servers.md) | Calculator, Weather, Filesystem, SQLite, Wikipedia, and more |
| 14 | [MCP in AI Applications](14_MCP_in_AI_Applications/14_MCP_in_AI_Applications.md) | Claude Desktop, Cursor, VS Code, Continue.dev, Open WebUI |
| 15 | [Daily Life MCP Servers](15_Daily_Life_MCP_Servers/15_Daily_Life_MCP_Servers.md) | Expense tracker, fitness, habits, journal, recipes |

### Part 6: Advanced Topics

| Chapter | Title | Description |
|---------|-------|-------------|
| 16 | [MCP and AI Agents](16_MCP_and_AI_Agents/16_MCP_and_AI_Agents.md) | LangChain, LangGraph, LlamaIndex, CrewAI, Pydantic AI |
| 17 | [Production Best Practices](17_Production_Best_Practices/17_Production_Best_Practices.md) | Testing, CI/CD, monitoring, scaling, documentation |
| 18 | [Advanced MCP](18_Advanced_MCP/18_Advanced_MCP.md) | Streaming, concurrency, federation, cloud deployment |

---

## 30-Day Learning Plan

Complete the entire course in 30 days. No topics dropped — every chapter covered.

| Day | Chapter(s) | Focus | Time |
|-----|-----------|-------|------|
| **1** | 01 | Introduction to MCP — What, Why, History, Ecosystem | 3-4 hrs |
| **2** | 01 | Ch.01 exercises + mini project (Protocol Simulator) | 2-3 hrs |
| **3** | 02 | MCP Architecture — Client, Host, Server, Transport | 3-4 hrs |
| **4** | 02 | Ch.02 exercises + mini project (Architecture Simulator) | 2-3 hrs |
| **5** | 03 | Installing MCP — Poetry, SDK, Hello World | 3-4 hrs |
| **6** | 04 | Build First MCP Server — Tool, Resource, Prompt | 3-4 hrs |
| **7** | 04 | Ch.04 exercises + mini project (Note Server) | 2-3 hrs |
| **8** | 05 | Build MCP Client — Connect, Call, Read, Handle Errors | 3-4 hrs |
| **9** | 05 | Ch.05 exercises + mini project (Universal Client) | 2-3 hrs |
| **10** | 06 | Understanding Tools — Schema, Validation, State | 3-4 hrs |
| **11** | 06 | Ch.06 exercises + mini project (Swiss Army Server) | 2-3 hrs |
| **12** | 07 | Resources — Static, Dynamic, Files, CSV, Templates | 3-4 hrs |
| **13** | 07 | Ch.07 exercises + mini project (Document Server) | 2-3 hrs |
| **14** | 08 | Prompts — Templates, Parameters, Composition | 3-4 hrs |
| **15** | 09 | Transport — STDIO, SSE, HTTP, Comparison | 3-4 hrs |
| **16** | 09 | Ch.08-09 exercises + mini projects | 3-4 hrs |
| **17** | 10 | MCP Security — Auth, Secrets, Rate Limiting, Injection | 3-4 hrs |
| **18** | 10 | Ch.10 exercises + mini project (Secure API Gateway) | 2-3 hrs |
| **19** | 11 | Logging & Observability — Structured Logs, Tracing, Metrics | 3-4 hrs |
| **20** | 12 | Production MCP Server — Config, Docker, Testing | 3-4 hrs |
| **21** | 12 | Ch.11-12 exercises + mini projects | 3-4 hrs |
| **22** | 13 | Useful MCP Servers (Part 1) — Calculator, Weather, Filesystem, SQLite | 4-5 hrs |
| **23** | 13 | Useful MCP Servers (Part 2) — Wikipedia, Web Scraper, Todo, System Monitor | 4-5 hrs |
| **24** | 14 | MCP in AI Applications — Claude Desktop, VS Code, Cursor, Continue.dev | 3-4 hrs |
| **25** | 15 | Daily Life Servers — Expenses, Fitness, Habits, Journal, Recipes | 4-5 hrs |
| **26** | 16 | MCP + AI Agents — LangChain, LangGraph, LlamaIndex, CrewAI, Pydantic AI | 4-5 hrs |
| **27** | 17 | Production Best Practices — Testing, CI/CD, Caching, Monitoring | 3-4 hrs |
| **28** | 18 | Advanced MCP — Streaming, Federation, Multi-user, Cloud | 4-5 hrs |
| **29** | Final | Build 2 Final Projects (choose from 10 options) | 5-6 hrs |
| **30** | Final | Complete final projects + Review all interview questions | 5-6 hrs |

**Total: ~100 hours over 30 days (~3.3 hrs/day average)**

### Daily Routine

1. **Read theory** (45-60 min) — Read the chapter markdown file
2. **Run examples** (30-45 min) — Execute each example, modify and experiment
3. **Do exercises** (45-60 min) — Attempt before checking solutions
4. **Build mini project** (45-60 min) — Apply everything learned
5. **Review** (15 min) — Interview questions + production tips

### For Each Chapter

1. Read the theory markdown file first
2. Run each example Python file
3. Try the exercises before looking at solutions
4. Build the mini project
5. Review interview questions
6. Read production tips

### Quick Setup

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup
cd mcp_server_tutorials/tutorials
poetry init
poetry add mcp httpx pydantic

# Activate environment
poetry shell

# Run any example
python 04_Build_First_MCP_Server/code/example1_minimal_server.py
```

---

## Key Comparisons

| Feature | REST API | GraphQL | MCP |
|---------|----------|---------|-----|
| Audience | Human developers | Human developers | AI models |
| Discovery | Manual (docs) | Schema introspection | Automatic negotiation |
| Integration | Custom per service | Custom per service | Universal protocol |
| Adaptability | Rigid endpoints | Flexible queries | AI adapts to tools |

---

## Final Projects (Chapter 18+)

After completing all chapters, build these production-grade projects:

1. **AI Coding Assistant** — Claude Desktop + Local MCP + Filesystem + GitHub + SQLite
2. **Personal Knowledge Assistant** — RAG + MCP + Local documents
3. **Company Documentation Assistant** — Search + Summarize + Q&A
4. **Support Engineer Assistant** — Logs + Metrics + Runbooks
5. **Resume Search Engine** — Parse + Index + Semantic search
6. **Personal AI Operating System** — All daily life servers unified
7. **Research Assistant** — Wikipedia + Web + Notes + Summary
8. **Local RAG Assistant** — FAISS/Qdrant + Documents + Chat
9. **AI File Manager** — Filesystem + Search + Organize + Summarize
10. **Universal MCP Hub** — Federation of all servers with routing

---

## License

This course is for educational purposes. All code examples are provided as-is for learning.

---

*Built with care for developers who want to master MCP.*
