import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from constant import huggingface_api_key, GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_api_key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

############################################################################
## Load data

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_PATH = "D:/Study/Git_repo/agentic_ai_tutorials/codes/docs/"

loader = DirectoryLoader(
    DATA_PATH,
    glob="*.txt",
    loader_cls=TextLoader
)

docs = loader.load()

print(len(docs))

############################################################################
# create chunks

splitter = RecursiveCharacterTextSplitter(chunk_size=500)

chunks = splitter.split_documents(docs)

############################################################################
## create embeddings

from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

############################################################################
## vector database

from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(chunks, embeddings)

retriever = vectorstore.as_retriever()

############################################################################
## RAG query

query = "Compare Tesla and BYD revenue"

docs = retriever.invoke(query)

context = "\n".join([d.page_content for d in docs])

############################################################################
## generate answer

# from langchain_google_genai import ChatGoogleGenerativeAI

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0
# )

from langchain_community.llms import Ollama
llm = Ollama(model="mistral")

prompt = f"""
Answer the question using the context below. Do not provide extra information
Context:
{context}

Question:
{query}
"""

response = llm.invoke(prompt)

print(response)

############################################################################
## Tool creation
"""
Agent needs tools.
    Tool 1 → Retriever
    Tool 2 → Calculator
    Tool 3 → Web Search
"""

## Retriever tool

from langchain_core.tools import tool

@tool
def retrieve_docs(query):
    """Retrieve EV related documents."""
    docs = retriever.invoke(query)
    return "\n".join([d.page_content for d in docs])


## Calculator Tool

@tool
def calculator(expr):
    """Evaluate mathematical expressions."""
    return eval(expr)


## Web search tool

from duckduckgo_search import DDGS

@tool
def web_search(query):
    """Search internet for latest information."""
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            results.append(r["body"])

    return "\n".join(results)


## Tool List

tools = [
    retrieve_docs,
    calculator,
    web_search
]

############################################################################
# Simple Agentic RAG
"""Agent will decide when to use RAG"""

# def agent(query):

#     decision = llm.invoke(
#         f"Does this require document retrieval?\n{query}"
#     )

#     if "yes" in decision.lower():#.content.lower():

#         context =  retrieve_docs.invoke(query)

#         answer = llm.invoke(
#             f"Context:\n{context}\nQuestion:{query}"
#         )

#         return answer#.content

#     return llm.invoke(query)#.content

def agent(query):

    decision = llm.invoke(
        f"""
Answer ONLY yes or no.

Does this question require retrieving documents from the EV research database?

Question: {query}
"""
    )

    decision = str(decision).lower()

    if "yes" in decision:

        context = retrieve_docs.invoke(query)

        answer = llm.invoke(
            f"""
Use the following context to answer the question.

Context:
{context}

Question:
{query}
"""
        )

        return str(answer)

    return str(llm.invoke(query))


# test agent function

print(agent("Compare Tesla and BYD revenue"))

## ReAct Agentic RAG

MAX_STEPS = 3
step = 0

query = "Compare Tesla and BYD revenue"

while step < MAX_STEPS:
    print("\nStep:", step)

    response = agent(query)

    print("Agent response:\n", response)

    # Stop if answer looks complete
    if len(response) > 20:
        print("\nFinal Answer Generated.")
        break

    step += 1
    
############################################################################
# Memory

# Short-Term Memory

memory = []

def save_memory(msg):
    memory.append(msg)
    
save_memory(response)

# Long-Term Memory

memory_vectorstore = FAISS.from_texts([], embeddings)

############################################################################

# Planning Agent

plan = llm.invoke(
"Break task into steps:\nCompare Tesla vs BYD revenue"
)

tasks = plan.split("\n")

############################################################################

# Reflection

def reflective_agent(query):

    # Step 1: get initial answer from agent
    answer = agent(query)

    # Step 2: ask LLM to critique answer
    critique = llm.invoke(
        f"""
You are a reviewer.

Check if the answer correctly answers the question.

Question:
{query}

Answer:
{answer}

Respond with:
GOOD if correct
BAD if incorrect
"""
    )

    critique = str(critique).lower()

    print("\nInitial Answer:\n", answer)
    print("\nCritique:", critique)

    # Step 3: if bad, regenerate
    if "bad" in critique:

        improved_answer = llm.invoke(
            f"""
The previous answer was incorrect.

Question:
{query}

Previous Answer:
{answer}

Generate a better answer.
"""
        )

        return str(improved_answer)

    return answer

result = reflective_agent("Compare Tesla and BYD revenue")

print("\nFinal Answer:\n", result)

############################################################################

# LangGraph Agentic RAG : Minimal

from langgraph.graph import StateGraph

def agent_node(state):

    query = state["query"]

    decision = llm.invoke(
        f"Does this question require document retrieval?\n{query}"
    )

    if "yes" in str(decision).lower():
        return {
            "query": query,
            "route": "retrieve"
        }

    return {
        "query": query,
        "route": "answer"
    }


def retrieve_node(state):

    query = state["query"]

    context = retrieve_docs.invoke(query)

    return {
        "context": context
    }
    

def answer_node(state):

    query = state["query"]
    context = state.get("context", "")

    answer = llm.invoke(
        f"""
Context:
{context}

Question:
{query}
"""
    )

    return {
        "answer": str(answer)
    }

from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from typing import TypedDict, Optional

class State(TypedDict, total=False):
    query: str
    context: str
    answer: str
    route: str


graph = StateGraph(State)

graph.add_node("agent", agent_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("answer", answer_node)


# ENTRY POINT
graph.add_edge(START, "agent")

# Conditional Routing (Core Agent Logic)

graph.add_conditional_edges(
    "agent",
    lambda state: state["route"],
    {
        "retrieve": "retrieve",
        "answer": "answer"
    }
)
# FLOW
graph.add_edge("retrieve", "answer")

# end point
graph.add_edge("answer", END)


app = graph.compile()


result = app.invoke({
    "query": "Compare Tesla and BYD revenue"
})

print(result["answer"])


"""
Internal Execution Flow: LangGraph internally runs:

START
 ↓
agent_node()
 ↓
retrieve_node()
 ↓
answer_node()
 ↓
END

"""