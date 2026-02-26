import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from constant import GOOGLE_API_KEY

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 1. Initialize Model
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")



prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    
    # This is where the memory will be injected automatically
    MessagesPlaceholder(variable_name="history"),
    
    ("human", "{question}"),
])

chain = prompt | llm

# A dictionary to store history for different users/sessions
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversation_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,  # The function from Step 3
    input_messages_key="question",
    history_messages_key="history",  # Must match the variable_name in Step 2
)


# 1. Tell the bot my name
response1 = conversation_chain.invoke(
    {"question": "Hi, my name is GeminiUser."},
    config={"configurable": {"session_id": "user_123"}}
)
print(f"Bot: {response1.content}")

# 2. Ask for the name (It should remember!)
response2 = conversation_chain.invoke(
    {"question": "Do you remember my name?"},
    config={"configurable": {"session_id": "user_123"}}
)
print(f"Bot: {response2.content}")

# 3. Test a different session (Should NOT know the name)
response3 = conversation_chain.invoke(
    {"question": "Do you remember my name?"},
    config={"configurable": {"session_id": "new_user_999"}}
)
print(f"New Session Bot: {response3.content}")