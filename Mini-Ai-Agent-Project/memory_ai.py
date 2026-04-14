from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# 🔑 LLM setup
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# Router
def router(state):
    return "chat"

# Chat with memory
def chat(state):
    history = state.get("history", [])
    
    # Add new user input
    history.append(("user", state["input"]))

    # Send full history to AI
    response = llm.invoke(history)

    # Store AI response
    history.append(("ai", response.content))

    state["history"] = history
    state["msg"] = response.content

    return state

# Build graph
builder = StateGraph(dict)

builder.add_node("router", lambda state: state)
builder.add_node("chat", chat)

builder.set_entry_point("router")

builder.add_edge("router", "chat")

graph = builder.compile()

# Loop
state = {"history": []}

while True:
    user_input = input("You: ")

    if user_input.lower() == "bye":
        break

    state["input"] = user_input

    result = graph.invoke(state)

    print("AI:", result["msg"])