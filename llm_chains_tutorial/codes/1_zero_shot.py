import os
from langchain_google_genai import ChatGoogleGenerativeAI
from constant import GOOGLE_API_KEY
import google.generativeai as genai

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


print("Available Models:")
for m in genai.list_models():
    # Only show models that support text generation
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")



llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")

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