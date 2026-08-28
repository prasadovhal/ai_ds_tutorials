import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
from urllib import response
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langfuse.langchain import CallbackHandler
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL, LANGFUSE_BASE_URL, LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, openai_key

os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_BASE_URL"] = LANGFUSE_BASE_URL
os.environ["OPENAI_API_KEY"] = openai_key


# object will sit in background and log all interactions with the model
langfuse_handler = CallbackHandler()

llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
prompt = ChatPromptTemplate.from_template("Write a short poem about {topic}")

chain = prompt | llm | StrOutputParser()

print("running chain...")

response = chain.invoke({"topic": "the ocean"}, callbacks=[langfuse_handler])
print("response: ", {response})

print("check langfuse dashboard for logged interactions")