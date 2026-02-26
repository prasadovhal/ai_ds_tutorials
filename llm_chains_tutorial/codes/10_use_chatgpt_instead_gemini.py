import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from constant import openai_key

# --- CONFIGURATION ---
# Replace 'sk-...' with your actual OpenAI API Key
os.environ["OPENAI_API_KEY"] = openai_key

# Initialize the Model (gpt-3.5-turbo is cheaper/faster, gpt-4o is smarter)
llm = ChatOpenAI(model="gpt-4o")

# --- THE CHAIN ---
# 1. Create a Prompt Template
prompt = ChatPromptTemplate.from_template("Tell me a funny joke about {topic}.")

# 2. Create the Chain (Prompt -> Model -> String Output)
chain = prompt | llm | StrOutputParser()

# --- EXECUTION ---
# Run the chain
response = chain.invoke({"topic": "software engineers"})

print(response)