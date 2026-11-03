import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""

LCEL (LangChain Expression Language), which uses the pipe | operator to build chains.

"""


from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

########################################################

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Template: Acts as a function taking arguments
template = ChatPromptTemplate.from_template(
    "Explain the concept of {topic} to a {audience}."
)

# 2. Output Parser: Extracts the text string from the AI response object
parser = StrOutputParser()

# 3. Chain: Connects them using the pipe operator
basic_chain = template | llm | parser

# 4. Invoke
response = basic_chain.invoke({"topic": "Black Holes", "audience": "5-year-old"})
print(response)