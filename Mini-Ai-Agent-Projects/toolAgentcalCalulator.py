# 🎯 What You Achieved

# 👉 Your agent now:

# ✅ Uses tools 🔧
# ✅ Makes decisions 🧠
# ✅ Combines logic + AI

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

# 🔧 TOOL → Calculator
def calculator(state):
    try:
        result = eval(state["input"])
        state["msg"] = f"Answer: {result}"
    except:
        state["msg"] = "Invalid math expression ❌"
    return state

# 🤖 Normal Chat
def chat(state):
    response = llm.invoke(state["input"])
    state["msg"] = response.content
    return state

# 🧠 Router (decide tool)
def router(state):
    text = state["input"]

    if any(char.isdigit() for char in text):
        return "calculator"
    else:
        return "chat"

# Build graph
builder = StateGraph(dict)

builder.add_node("router", lambda state: state)
builder.add_node("calculator", calculator)
builder.add_node("chat", chat)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    router,
    {
        "calculator": "calculator",
        "chat": "chat"
    }
)

graph = builder.compile()

# Loop
while True:
    user_input = input("You: ")

    if user_input.lower() == "bye":
        break

    result = graph.invoke({"input": user_input})

    print("AI:", result["msg"])