import os
from typing import List

# --- LIBRARIES ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableBranch  # <--- NEW IMPORT
from pydantic import BaseModel, Field
from constant import GOOGLE_API_KEY

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# --- CONFIGURATION ---
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.7)  
# --- PART 1: MEMORY (Unchanged) ---
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly Career Coach named 'Atlas'."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

coach_chain = RunnableWithMessageHistory(
    chat_prompt | llm,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# --- PART 2: ROUTER CHAINS (The Resume Polisher) ---

### --- NEW: Define 3 Distinct Prompts ---
# 1. Technical Prompt (For Engineers)
tech_prompt = ChatPromptTemplate.from_template(
    """Act as a Technical Resume Writer. Rewrite the text using precise metrics, 
    stack details, and engineering terminology.
    Input: {messy_text}
    Output:"""
)

# 2. Creative Prompt (For Designers)
creative_prompt = ChatPromptTemplate.from_template(
    """Act as a Creative Copywriter. Rewrite the text using expressive, 
    visionary language that highlights aesthetics and brand impact.
    Input: {messy_text}
    Output:"""
)

# 3. Standard Prompt (For Everyone Else)
std_prompt = ChatPromptTemplate.from_template(
    """Act as a Professional Resume Writer. Rewrite the text to be punchy and professional.
    Input: {messy_text}
    Output:"""
)

### --- NEW: Build the Branch Logic ---
# We define the conditions (Lambda functions) to choose the path
branch = RunnableBranch(
    (lambda x: "designer" in x["role"].lower() or "artist" in x["role"].lower(), creative_prompt | llm | StrOutputParser()),
    (lambda x: "engineer" in x["role"].lower() or "developer" in x["role"].lower(), tech_prompt | llm | StrOutputParser()),
    std_prompt | llm | StrOutputParser() # Fallback
)

# Note: The branch expects a dictionary input with "role" and "messy_text"
rewrite_chain = branch 

# --- PART 3: STRUCTURED OUTPUT (Unchanged) ---
class StudyPlan(BaseModel):
    weakness_identified: str = Field(description="The main skill gap found")
    recommended_topics: List[str] = Field(description="List of 3 specific topics")
    estimated_hours: int = Field(description="Estimated hours to master")

plan_generator = llm.with_structured_output(StudyPlan)

# --- MAIN APP LOGIC ---
def main():
    print("🤖 Atlas (Smart Router Edition): Hi! Let's optimize your resume.")
    session_id = "user_session_1"
    
    # 1. Gather Info
    name = input("You: Name? ")
    role = input("You: Target Role? (Try 'Software Engineer' or 'Graphic Designer') ") 
    
    # 2. Router Test
    print(f"\nAtlas: Okay, I will use my specific '{role}' strategy for you.")
    print("Atlas: Tell me about your last job messily.")
    messy_exp = input("You: ")
    
    print("\n...Routing to the correct Expert...\n")
    
    ### --- NEW: passing 'role' to the chain so the Router can decide ---
    polished = rewrite_chain.invoke({"role": role, "messy_text": messy_exp})
    
    print(f"✨ Custom Polish: {polished}\n")

    # 3. Study Plan (Unchanged)
    print(f"Atlas: Generating plan for {role}...")
    plan_prompt = f"User wants to be a {role}. Experience: {polished}. Create study plan."
    plan = plan_generator.invoke(plan_prompt)
    
    print("\n📋 OFFICIAL STUDY PLAN")
    print(f"   Gap: {plan.weakness_identified}")
    print(f"   Topics: {', '.join(plan.recommended_topics)}")

if __name__ == "__main__":
    main()