import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

# BAD PROMPT (Vague)
prompt_weak = "Write code for a calculator."

# GOOD PROMPT (Persona + Constraints)
prompt_strong = """
You are a Senior Python Developer obsessed with clean code (PEP 8).
Write a Python class for a simple calculator. 
Constraints:
1. Include type hinting.
2. Include docstrings for every method.
3. Handle division by zero errors gracefully.
"""

response = llm.invoke(prompt_strong)
print(response.content)