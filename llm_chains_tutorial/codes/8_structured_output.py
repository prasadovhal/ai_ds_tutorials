import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from constant import OLLAMA_BASE_URL, OLLAMA_MODEL

# Configure Ollama
llm = ChatOllama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

# 1. Define the Schema (The Shape of Data you want)
class PersonInfo(BaseModel):
    name: str = Field(description="The name of the person")
    age: int = Field(description="The age of the person, if known. If not, guess based on context.")
    job: str = Field(description="The person's job title or role")

# 2. Bind the Schema to the LLM
# This forces the LLM to ONLY return data fitting this class
structured_llm = llm.with_structured_output(PersonInfo)

# 3. Invoke
text = "Alice is a 30 year old software engineer living in New York."
response = structured_llm.invoke(text)

# 4. Access Data as Python Object
print(f"Name: {response.name}")
print(f"Job: {response.job}")
print(f"Type: {type(response)}") # <class '__main__.PersonInfo'>