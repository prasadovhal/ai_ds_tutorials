"""

LCEL (LangChain Expression Language), which uses the pipe | operator to build chains.

"""


import os
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from constant import GOOGLE_API_KEY

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")

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