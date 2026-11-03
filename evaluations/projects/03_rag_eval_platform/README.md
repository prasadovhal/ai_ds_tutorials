# Project 3: RAG Evaluation Platform

TF-IDF retriever + full RAG evaluation pipeline with Langfuse tracing and LangGraph.

## Run
```bash
cd projects/03_rag_eval_platform
python main.py
```

## What It Does
- Builds TF-IDF retriever from wiki corpus
- Retrieves top-3 passages per question
- Generates answers via Ollama (or heuristic fallback)
- Evaluates: context precision, context recall, faithfulness, answer relevancy
- Sends traces to Langfuse
- Demos LangGraph RAG chain (retrieve -> generate state graph)

## Dependencies
scikit-learn, requests, langfuse, langgraph (optional)
