"""
"Smart Career Coach" CLI App.
    What this App does:
        1. Memory: Remembers your name and target job title.
        2. Chains: Takes your messy resume summary and rewrites it professionally.
        3. Logic: Generates 3 custom interview questions based on that new resume.
        4. Structured Output: Creates a strict JSON "Study Plan" and saves it to a file.
        5. Streaming: streams the advice so it feels like a real conversation.
"""

import os
import time
from typing import List

# --- LIBRARIES ---
# 1. Models & Schemas
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from pydantic import BaseModel, Field
from constant import GOOGLE_API_KEY

# 2. Setup API Key (Or use .env file)
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# --- CONFIGURATION ---
# We use a cheaper model for the chat and a smarter one for the JSON logic if needed.
# For simplicity, we use the same model here.
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.7)

# --- PART 1: MEMORY (The Chatbot) ---
# Global store for chat history
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# The Persona Prompt
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly, encouraging Career Coach named 'Atlas'. "
               "You help users refine their resumes and prepare for interviews."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# Wrap the chain with memory
coach_chain = RunnableWithMessageHistory(
    chat_prompt | llm,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# --- PART 2: CHAINS (Resume Polisher) ---
# This chain takes a messy input and makes it professional
rewrite_prompt = ChatPromptTemplate.from_template(
    """
    Act as a professional resume writer.
    Rewrite the following messy experience into a single, punchy bullet point
    using strong action verbs (e.g., 'Spearheaded', 'Optimized').
    
    Messy Input: {messy_text}
    
    Professional Output:
    """
)
rewrite_chain = rewrite_prompt | llm | StrOutputParser()

# --- PART 3: STRUCTURED OUTPUT (The Study Plan) ---
# Define the JSON Schema
class StudyPlan(BaseModel):
    weakness_identified: str = Field(description="The main skill gap found")
    recommended_topics: List[str] = Field(description="List of 3 specific topics to learn")
    estimated_hours: int = Field(description="Estimated hours to master these topics")

# Create the structured extractor
plan_generator = llm.with_structured_output(StudyPlan)

# --- MAIN APP LOGIC ---
def main():
    print("🤖 Atlas (Career Coach): Hi! I'm Atlas. Let's get you hired.")
    print("------------------------------------------------------------")
    
    session_id = "user_session_1"
    
    # 1. Gather Basic Info (Memory Test)
    name = input("You: What is your name? ")
    role = input("You: What role are you targeting? (e.g., Python Dev) ")
    
    # Send to Memory Chain
    response = coach_chain.invoke(
        {"input": f"My name is {name} and I want to be a {role}. Say hello briefly."},
        config={"configurable": {"session_id": session_id}}
    )
    print(f"\nAtlas: {response.content}\n")

    # 2. Resume Rewrite (Chain Test)
    print("Atlas: Tell me about your last job. Don't worry about formatting, just type it messily.")
    messy_exp = input("You: ")
    
    print("\n...Polishing your experience...\n")
    polished = rewrite_chain.invoke({"messy_text": messy_exp})
    print(f"✨ Better Bullet Point: {polished}\n")

    # 3. Study Plan (Structured Output Test)
    print(f"Atlas: Based on your target role ({role}), I'm generating a study plan...")
    
    # We ask the LLM to analyze the role vs the experience
    plan_prompt = f"""
    User wants to be a {role}.
    Their experience is: {polished}.
    Identify what key skill they might be missing for a Senior role 
    and create a study plan.
    """
    
    plan = plan_generator.invoke(plan_prompt)
    
    # 4. Display & Save JSON
    print("\n📋 OFFICIAL STUDY PLAN")
    print(f"   Gap Detected: {plan.weakness_identified}")
    print(f"   Study These: {', '.join(plan.recommended_topics)}")
    print(f"   Time Needed: {plan.estimated_hours} hours")
    
    # Save to file (Simulating a database save)
    with open("my_study_plan.json", "w") as f:
        f.write(plan.json())
    print("\n(Saved to my_study_plan.json)")

if __name__ == "__main__":
    main()