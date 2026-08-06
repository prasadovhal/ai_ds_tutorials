# ScienceGateway: Production AI Tutorial

A comprehensive, hands-on Python tutorial covering all AI/LLM production concepts through a real-life **Science Research Assistant AI Gateway**.

## 🎯 What You'll Learn

This tutorial covers 17 concepts in order, building a production-ready AI system that combines:

- **Routing & Intent Classification** (files 1-7)
- **Observability & Tracing** (files 8-14)
- **RAG Pipeline** (files 10-11)
- **Evaluation** (file 15)
- **Skills & Agents** (file 16)
- **Production Gateway** (file 17)

## 📋 Tutorial Files

### Core Concepts (Files 1-7)
Learn how to build routing intelligence into LLM applications.

| File | Concept | Real-World Use |
|------|---------|-----------------|
| **01_llm_roles_basics.py** | System/User roles, prompt injection | How LLMs follow instructions + security |
| **02_intent_classification.py** | Classify query intent | Route simple facts vs. research tasks |
| **03_complexity_domain_routing.py** | Complexity scoring, domain detection | Allocate resources based on query difficulty |
| **04_token_cost_routing.py** | Token counting, cost awareness | Prevent expensive queries |
| **05_user_tier_policies.py** | Multi-tier user segmentation | Students vs. Professors get different depth |
| **06_confidence_fallback.py** | Self-evaluation, retry with context | Improve reliability with confidence-based escalation |
| **07_config_ab_testing.py** | Configuration-driven routing, A/B tests | Test prompt variations, pick winners |

### Observability (Files 8-14)
Build complete visibility into what your LLM system is doing.

| File | Concept | Real-World Use |
|------|---------|-----------------|
| **08_observability_foundations.py** | Custom tracer, spans, structured logging | Foundation for all tracing |
| **09_langfuse_basics.py** | LangFuse cloud setup, traces, generations | Send traces to cloud dashboard |
| **10_rag_pipeline.py** | Embedding, vector DB, retrieval | Ground answers in documents |
| **11_langfuse_rag_tracing.py** | Trace RAG retrieval + generation separately | Debug: which chunks retrieved, why |
| **12_opentelemetry_intro.py** | OTel standard, spans, context propagation | Open-source observability standard |
| **13_langsmith_intro.py** | LangSmith ecosystem, prompt versioning | Compare with LangFuse, prompt management |
| **14_arize_phoenix_intro.py** | Local RAG debugging, hallucination detection | Find why RAG answers are wrong |

### Advanced Topics (Files 15-17)
Measurement, decision-making, and production systems.

| File | Concept | Real-World Use |
|------|---------|-----------------|
| **15_evaluation_metrics.py** | LLM-as-judge, hallucination/groundedness scores | Measure answer quality programmatically |
| **16_skills_vs_agents.py** | Skills (fixed), Agents (reasoning), Supervisor | When to use each, multi-agent architecture |
| **17_production_gateway.py** | **CAPSTONE** - combines ALL concepts | Full end-to-end system ready for production |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd "D:\Study\Git_repo\agent-skills\AI concepts"
poetry install
```

### 2. Verify Setup

```bash
# Check you have .env with LangFuse keys
cat .env | grep LANGFUSE

# Check Ollama is running
ollama list
```

### 3. Run Your First Tutorial

```bash
# Simplest: learn about LLM roles
python 01_llm_roles_basics.py

# Intermediate: build a RAG pipeline
python 10_rag_pipeline.py

# Advanced: full production gateway
python 17_production_gateway.py
```

## 📚 Learning Paths

### Path A: Understand Routing (60 min)
Focus on how queries are routed to different capabilities.
```
01_llm_roles_basics.py
    ↓
02_intent_classification.py
    ↓
03_complexity_domain_routing.py
    ↓
07_config_ab_testing.py
```
**Outcome:** You can design routing for any LLM app

---

### Path B: Build RAG System (90 min)
Learn to ground LLM answers in your own documents.
```
10_rag_pipeline.py
    ↓
09_langfuse_basics.py
    ↓
11_langfuse_rag_tracing.py
    ↓
14_arize_phoenix_intro.py
    ↓
15_evaluation_metrics.py
```
**Outcome:** Production RAG with observability

---

### Path C: Full Production System (3+ hours)
Go through sequentially, understand everything.
```
01 → 02 → 03 → 04 → 05 → 06 → 07
    ↓
08 → 09 → 10 → 11 → 12 → 13 → 14 → 15
    ↓
16 → 17
```
**Outcome:** Master production AI systems

---

## 🧪 Understanding Which Concept Where

Every file shows **where the concept gets used** in real systems:

- **Intent classification** (02) → feeds into routing (03)
- **Complexity scoring** (03) → drives token budget check (04)
- **User tier policies** (05) → constrain response depth
- **Confidence fallback** (06) → handles low-confidence answers
- **Config-driven routing** (07) → makes prompts testable
- **Observability** (08-14) → traces everything end-to-end
- **RAG pipeline** (10-11) → replaces guessing with documents
- **Evaluation** (15) → measures quality programmatically
- **Skills vs Agents** (16) → architecture decision
- **Production Gateway** (17) → everything working together

## 🎓 Senior Data Scientist Perspective

This tutorial is **not tutorial.** It's a **reference implementation** of production AI systems.

- **No OOP**: Functions are data pipelines, not objects
- **Flat structure**: Understand code flow visually
- **Comments explain WHY**: The code structure shows HOW
- **Real-world scenario**: Science Gateway is not imaginary—it's typical
- **Every concept serves a purpose**: No padding or over-engineering

Each file can stand alone, but reading sequentially shows how pieces fit together.

## 📊 Project Structure

```
D:\Study\Git_repo\agent-skills\AI concepts\
├── 01_llm_roles_basics.py           # Foundations
├── 02_intent_classification.py      # Classification
├── 03_complexity_domain_routing.py  # Routing
├── 04_token_cost_routing.py         # Cost control
├── 05_user_tier_policies.py         # User segmentation
├── 06_confidence_fallback.py        # Reliability
├── 07_config_ab_testing.py          # Configuration + A/B testing
├── 08_observability_foundations.py  # Custom tracer
├── 09_langfuse_basics.py            # LangFuse cloud
├── 10_rag_pipeline.py               # RAG system
├── 11_langfuse_rag_tracing.py       # RAG + observability
├── 12_opentelemetry_intro.py        # OpenTelemetry standard
├── 13_langsmith_intro.py            # LangSmith ecosystem
├── 14_arize_phoenix_intro.py        # Local RAG debugging
├── 15_evaluation_metrics.py         # Quality measurement
├── 16_skills_vs_agents.py           # Architecture patterns
├── 17_production_gateway.py         # Full system
│
├── data/
│   └── science_kb.txt               # 20 science knowledge base chunks
│
├── pyproject.toml                   # Poetry dependencies
├── .env                             # Your API keys (LangFuse, Ollama, etc.)
└── README.md                        # This file
```

## 🔑 Key Concepts

### Routing
How do we decide what to do with a query?
- Intent: factual vs. research vs. off-topic
- Complexity: 1-10 scale (affects resource allocation)
- Domain: biology vs. physics vs. chemistry (affects prompts)
- Cost: expensive queries get budget checks
- Tier: student vs. professor (affects depth)

### Observability
How do we see what's happening?
- **Traces**: one user request end-to-end
- **Spans**: one step within a trace
- **Generations**: LLM calls logged with tokens + latency
- **Metadata**: searchable context (domain, user_tier, complexity)
- **Events**: timestamped markers (retrieval started, LLM inference done)

### RAG (Retrieve-Augment-Generate)
How do we ground answers in reality?
- Load documents → Embed → Store in vector DB
- Query comes in → Find similar documents → Augment prompt with context
- LLM answers based on context (less hallucination)

### Evaluation
How do we measure quality?
- Hallucination score: is answer contradicted by context?
- Groundedness score: % of answer supported by facts?
- Faithfulness score: does answer accurately reflect context?
- Relevance score: does answer address the question?
- Latency + Cost: performance metrics

### Skills vs Agents
When do we decide what to do?
- **Skill**: Fixed workflow (retrieve → generate)
- **Agent**: Reasoning system (decide what to do, then execute)
- **Supervisor**: Routes to multiple agents

## 💡 Real-World Applications

Every concept in this tutorial comes from production systems:

1. **Routing logic** → Used by OpenAI, Anthropic, LLaMA-based services
2. **Observability** → Required for compliance (healthcare, finance)
3. **RAG** → Powers knowledge bases, internal wikis, document Q&A
4. **Evaluation** → Measures quality for deployment decisions
5. **Skills/Agents** → Architecture pattern for LangChain, LlamaIndex users

## 🔍 Next Steps

After completing this tutorial:

1. **Implement for your domain**: Replace "science" with your domain
2. **Add more sophisticated routing**: Decision trees, learned routing
3. **Deploy to production**: Add API server (FastAPI), database, auth
4. **Monitor continuously**: Use LangFuse dashboards to watch quality
5. **Improve iteratively**: A/B test prompts, evaluate regularly

## 🎯 What You Won't Learn Here

(But know these exist)

- **LangChain/LlamaIndex frameworks**: This uses raw APIs for clarity
- **Fine-tuning**: Assumes base models are good enough
- **Guardrails**: Content moderation, PII detection (adjacent topic)
- **Multi-modal**: Images, audio (future tutorial)
- **Local model optimization**: Quantization, pruning (separate focus)

## 📖 Documentation

Each file has:
- **Top docstring**: Explains concepts
- **Function docstrings**: Explain WHY (not HOW)
- **Comments**: Mark key decisions or non-obvious logic
- **Example usage**: Shows how to run and interpret results

## ❓ Questions & Debugging

**How do I see LangFuse traces?**
1. Run any file that uses LangFuse (09, 11, 17)
2. Go to https://cloud.langfuse.com
3. Search for trace_id or filter by metadata
4. View latency, tokens, calls in the dashboard

**Why does RAG retrieval return wrong chunks?**
1. Run file 14 (Arize Phoenix)
2. Visualize retrieval scores
3. Check if embedding model understands your domain
4. Consider domain-specific embeddings

**How do I test different prompts?**
1. Use file 07 (A/B testing)
2. Define two prompt styles
3. LLM-as-judge scores both
4. Pick the winner

**Is this production-ready?**
1. File 17 is architecture-ready
2. You'll need: API server, auth, rate limiting
3. Add: monitoring, alerting, fallbacks for downtime
4. Test: load testing, chaos testing, user acceptance testing

## 🎁 Bonus Features

- **20-chunk knowledge base** (science_kb.txt): covers biology, physics, chemistry, astronomy
- **Poetry setup**: reproducible dependencies
- **LangFuse integration**: production observability from day 1
- **Ollama local**: no API costs during learning
- **Config-driven**: easy to customize without code changes

## 📝 License & Attribution

This tutorial was generated by Claude (Anthropic's AI).
Designed for practitioners learning production LLM systems.

Free to use, modify, distribute for educational purposes.

---

**Ready?** Start with `01_llm_roles_basics.py` or jump to a concept that interests you.

**Questions?** Each file is self-contained; run it to see concepts in action.
