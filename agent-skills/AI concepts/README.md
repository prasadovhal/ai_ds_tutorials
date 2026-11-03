# ScienceGateway: Production AI Tutorial

A comprehensive, hands-on Python tutorial covering all AI/LLM production concepts through a real-life **Science Research Assistant AI Gateway**.


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