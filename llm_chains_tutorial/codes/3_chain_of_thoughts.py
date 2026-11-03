import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

# Scenario: A complex logic puzzle
cot_prompt = """
A farmer has 17 sheep. All but 9 die. How many sheep are left?

Instructions:
1. Do not give the answer immediately.
2. Let's think step by step. Analyze the wording of the question carefully.
3. Show your reasoning logic.
4. Provide the final answer at the end.
"""

# prompt = PromptTemplate.from_template(cot_prompt)
# chain = prompt | llm

print(llm.invoke(cot_prompt).content)


# as this part we have not used prompt template, as we are solving single puzzle task, and there is no placeholder in cot_prompt
# with prompt template same problem can be written as:

# 1. Define the template with a placeholder
cot_template = PromptTemplate.from_template("""
Solve the following puzzle: {puzzle}

Instructions:
1. Let's think step by step.
2. Show your reasoning.
""")

# 2. Create the chain
cot_chain = cot_template | llm

# 3. Inject the variable
print(cot_chain.invoke({"puzzle": "A farmer has 17 sheep. All but 9 die. How many sheep are left?"}).content)