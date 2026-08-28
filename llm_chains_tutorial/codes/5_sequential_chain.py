import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

########################################################################################

"""

RunnablePassthrough()?
It acts like a pipe that says: "Whatever the user typed at the very beginning, just pass it through to this point unchanged."

"""

from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Step 1: Name Generator Chain ---
name_prompt = ChatPromptTemplate.from_template(
    "Generate a catchy, futuristic name for a company that makes {product}. Return ONLY the name."
)
name_chain = name_prompt | llm | StrOutputParser()

# --- Step 2: Slogan Generator Chain ---
slogan_prompt = ChatPromptTemplate.from_template(
    "Write a 3-word slogan for a company named '{company_name}' that makes {product}."
)
slogan_chain = slogan_prompt | llm | StrOutputParser()

# --- Connecting the Chains ---
# We need to pass the original input ('product') AND the output of the first chain ('company_name')
# to the second chain. We use a dictionary structure for this.

overall_chain = (
    {"company_name": name_chain, "product": RunnablePassthrough()} 
    | slogan_chain
)

# Execution flow: 
# 1. User inputs "AI-powered coffee mug".
# 2. 'name_chain' runs -> returns "CyberSip".
# 3. Dictionary created: {"company_name": "CyberSip", "product": "AI-powered coffee mug"}
# 4. 'slogan_chain' receives this dictionary -> returns Slogan.

print(overall_chain.invoke("AI-powered coffee mug"))