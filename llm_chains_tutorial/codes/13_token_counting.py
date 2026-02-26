import os
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from constant import openai_key

# --- CONFIGURATION ---
# Replace 'sk-...' with your actual OpenAI API Key
os.environ["OPENAI_API_KEY"] = openai_key

# Initialize the Model (gpt-3.5-turbo is cheaper/faster, gpt-4o is smarter)

llm = ChatOpenAI(model="gpt-4o")
with get_openai_callback() as cb:
    result = llm.invoke("Tell me a funny joke")
    
    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Cost (USD): ${cb.total_cost}")