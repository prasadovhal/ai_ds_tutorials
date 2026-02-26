import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from constant import GOOGLE_API_KEY

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 1. Initialize Model
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")

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