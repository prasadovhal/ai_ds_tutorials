import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langchain_google_genai import ChatGoogleGenerativeAI
from constant import GOOGLE_API_KEY

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are a disaster tweet classifier.

Classify this tweet as:
1 = Real Disaster
0 = Not Disaster

Respond ONLY in JSON format:
{{
    "prediction": 0 or 1
}}

Tweet:
{tweet}

Explain why this tweet is classified as disaster or not.
Focus on semantic reasoning.
""")


# create chain
chain = prompt | llm

# check 
tweet = "Massive earthquake destroys buildings in Turkey"

prediction = 1

response = chain.invoke({
    "tweet": tweet,
    "prediction": prediction
})

print(response.content)


# predict test set
import pandas as pd

train = pd.read_csv("train.csv")
test = pd.read_csv("test.csv")

import json

def predict(tweet):
    response = chain.invoke({"tweet": tweet})
    
    try:
        print(response.content)
        output = json.loads(response.content)
        return output["prediction"], output["confidence"]
    except:
        return 0, 0.5  # fallback
    
predictions = []

for tweet in test.iloc[:5]["text"]:
    pred, conf = predict(tweet)
    predictions.append(pred)

submission = pd.DataFrame({
    "id": test["id"],
    "target": predictions
})

# submission.to_csv("submission_llm.csv", index=False)