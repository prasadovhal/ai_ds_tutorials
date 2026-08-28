import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

# We want the LLM to convert informal text to formal corporate speak.
# We provide 3 "shots" (examples) before the actual task.

few_shot_template = """
Task: Rewrite the user's slang message into professional corporate email language.

Example 1:
Input: "Yo, I'm gonna be late cause traffic is nuts."
Output: "Please be advised that I will be arriving slightly behind schedule due to unexpected heavy traffic."

Example 2:
Input: "This code is trash, fix it."
Output: "The current codebase requires significant refactoring to meet our quality standards. Please review the implementation."

Example 3:
Input: "I'm out, peace."
Output: "I am logging off for the day. Best regards."

Input: {user_input}
Output:
"""

prompt = PromptTemplate.from_template(few_shot_template)
chain = prompt | llm

print(chain.invoke({"user_input": "My wifi is dead, can't join the call."}).content)