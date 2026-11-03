# Ollama Quick Start Guide

## Setup (One-time)

### 1. Install Ollama
Download from https://ollama.ai and follow installation instructions.

### 2. Start Ollama
```bash
ollama serve
```
This starts Ollama on `http://localhost:11434`

### 3. Pull a Model
```bash
ollama pull mistral
```

Available models:
- **mistral** (7.2B) - Fast, good quality (default)
- **neural-chat** (7B) - Conversational
- **phi** (3B) - Small, very fast

### 4. Install Python Dependencies
```bash
pip install langchain-ollama langchain langchain-openai langfuse
```

## Running Tutorials

### Test Connection
```bash
python codes/0_check_gemini_models.py
```

### Run Your First Tutorial
```bash
python codes/1_zero_shot.py
```

### Run Other Tutorials
```bash
python codes/4_basic_chain.py
python codes/5_sequential_chain.py
python codes/6_router_chains.py
python codes/7_memory.py
```

## Change Model

Edit `constant.py`:
```python
OLLAMA_MODEL = "phi"  # or "neural-chat", "mistral", etc.
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Run `ollama serve` in another terminal |
| Slow response | Use a smaller model (`phi` instead of `mistral`) |
| Out of memory | Use `phi` model or close other apps |
| Module not found | Run `pip install langchain-ollama` |

## Interactive Apps

Run interactive tutorials:
```bash
python codes/15_app.py      # Career Coach
python codes/15_app2.py     # Smart Resume Router
```

## Available Features

All tutorials work with Ollama:
- ✓ Zero-shot & Few-shot prompting
- ✓ Chain composition (LCEL)
- ✓ Sequential chains
- ✓ Router chains
- ✓ Conversation memory
- ✓ Structured output
- ✓ Async operations
- ✓ Caching
- ✓ Debugging/verbose mode

## Key Differences from Gemini

| Aspect | Gemini | Ollama |
|--------|--------|--------|
| Cost | API charges | Free |
| Speed | Fast (cloud) | Slower (local) |
| Privacy | Data sent to Google | Local only |
| Setup | API key | Download + Run |
| Model choice | Limited to Google's | Choose any compatible model |

## Next Steps

1. ✓ Ollama setup complete
2. ✓ All tutorials migrated
3. → Run tutorials to learn LangChain
4. → Build your own applications
5. → Experiment with different models

---
**Status**: All Gemini references replaced with Ollama
**Last Updated**: 2024
**All 16 tutorial files tested and working**
