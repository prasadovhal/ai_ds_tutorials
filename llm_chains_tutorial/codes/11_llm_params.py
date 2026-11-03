import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL, openai_key
import os

os.environ["OPENAI_API_KEY"] = openai_key

# Temperature
"""
Range: 0.0 to 1.0 (sometimes up to 2.0 for OpenAI).
Low (0.0 - 0.3): Factual, deterministic, repetitive. Use for Coding, Math, Data Extraction.
High (0.7 - 1.0): Creative, diverse, unpredictable. Use for Brainstorming, Poetry, Chatbots.
"""

llm_strict = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL, temperature=0.0)

# Max Output Tokens (Length Limit)
"""
This sets a hard limit on how much the model can write.
"""
llm = ChatOpenAI(model="gpt-4o", max_tokens=150)

# 3. Stop Sequences ( The "Kill Switch")

# Stop strictly when it tries to start a new heading
"""
You can tell the model to strictly stop generating if it hits a specific word or character.
"""

llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    stop=["\n\n", "User:"]
)

# 4. Top_P and Top_K (Advanced Sampling)

"""
1. Top_K (Google specific): "Only consider the top K most likely next words."
    - Low K (e.g., 1): Greedy decoding (always picks the most likely word).
    - High K (e.g., 40): More variety.
2. Top_P (Nucleus Sampling): "Consider the smallest set of words whose cumulative probability is P."
    - Low P (0.1): Very conservative.
    - High P (0.9): Diverse.

"""
llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    top_k=40,
    top_p=0.95
)

# 5. Timeout (The "Don't Hang" Rule)
"""
Sometimes the API hangs or is slow. You don't want your app to freeze forever.
"""
# Raise an error if the model doesn't answer within 10 seconds
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    request_timeout=10 
)

## all together

llm_sniper = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    temperature=0.0,        # No creativity allowed
    top_p=0.8,              # Slight flexibility for grammar
)