import os
from urllib import response
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langfuse.langchain import CallbackHandler
from constant import GOOGLE_API_KEY, LANGFUSE_BASE_URL, LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, openai_key, LANGFUSE_BASE_URL

os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_BASE_URL"] = LANGFUSE_BASE_URL
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = openai_key


# object will sit in background and log all interactions with the model
langfuse_handler = CallbackHandler()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
prompt = ChatPromptTemplate.from_template("Write a short poem about {topic}")

chain = prompt | llm | StrOutputParser()

print("running chain...")

response = chain.invoke({"topic": "the ocean"}, callbacks=[langfuse_handler])
print("response: ", {response})

print("check langfuse dashboard for logged interactions")