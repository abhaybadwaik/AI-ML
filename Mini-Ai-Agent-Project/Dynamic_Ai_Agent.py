from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from dotenv import load_dotenv

# 🔑 LLM setup
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# Router (brain)
def router(state):
    text = state["input"].lower()

    if "joke" in text:
        return "joke"
    elif "explain" in text:
        return "explain"
    elif "bye" in text:
        return "exit"
    else:
        return "chat"

# Nodes (actions)

def joke(state):
    response = llm.invoke("Tell a funny programming joke")
    state["msg"] = response.content
    return state

def explain(state):
    response = llm.invoke(f"Explain clearly: {state['input']}")
    state["msg"] = response.content
    return state

def chat(state):
    response = llm.invoke(state["input"])
    state["msg"] = response.content
    return state

def exit_node(state):
    state["msg"] = "Goodbye 👋"
    return state

# Build graph
builder = StateGraph(dict)

builder.add_node("router", lambda state: state)
builder.add_node("joke", joke)
builder.add_node("explain", explain)
builder.add_node("chat", chat)
builder.add_node("exit", exit_node)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    router,
    {
        "joke": "joke",
        "explain": "explain",
        "chat": "chat",
        "exit": "exit"
    }
)

graph = builder.compile()

# Loop
while True:
    user_input = input("You: ")

    result = graph.invoke({"input": user_input})

    print("AI:", result["msg"])

    if user_input.lower() == "bye":
        break