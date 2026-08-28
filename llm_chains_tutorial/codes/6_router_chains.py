import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

########################################################################################

from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Define distinct chains
math_chain = (
    ChatPromptTemplate.from_template("You are a mathematician. Solve: {question}")
    | llm | StrOutputParser()
)

history_chain = (
    ChatPromptTemplate.from_template("You are a historian. Explain: {question}")
    | llm | StrOutputParser()
)

general_chain = (
    ChatPromptTemplate.from_template("Answer helpfuly: {question}")
    | llm | StrOutputParser()
)

# 2. Create the Classifier (The Router)
# This chain decides WHICH path to take
classification_chain = (
    ChatPromptTemplate.from_template(
        """Given the user question, classify it as 'math', 'history', or 'other'. 
        Return ONLY the classification word.
        Question: {question}"""
    )
    | llm
    | StrOutputParser()
)

# 3. Build the Branching Logic
branch = RunnableBranch(
    (lambda x: "math" in x["topic"].lower(), math_chain),
    (lambda x: "history" in x["topic"].lower(), history_chain),
    general_chain # Fallback
)

# 4. Full System
full_chain = {
    "topic": classification_chain, 
    "question": RunnablePassthrough()
} | branch

# Test it
print("--- Math Question ---")
print(full_chain.invoke("What is the square root of 144?"))

print("\n--- History Question ---")
print(full_chain.invoke("Who was the first emperor of Rome?"))