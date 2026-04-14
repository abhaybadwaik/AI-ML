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

# 🔧 Calculator Tool
def calculator(state):
    try:
        result = eval(state["input"])
        state["msg"] = f"Answer: {result}"
    except:
        state["msg"] = "Invalid math ❌"
    return state

# 🌐 Search Tool (AI-powered search)
def search(state):
    query = state["input"]
    response = llm.invoke(f"Search and give short answer: {query}")
    state["msg"] = response.content
    return state

# 🤖 Chat Tool
def chat(state):
    response = llm.invoke(state["input"])
    state["msg"] = response.content
    return state

# 🧠 Router
def router(state):
    text = state["input"].lower()

    if any(char.isdigit() for char in text):
        return "calculator"
    elif "search" in text or "who is" in text or "what is" in text:
        return "search"
    else:
        return "chat"

# Build graph
builder = StateGraph(dict)

builder.add_node("router", lambda state: state)
builder.add_node("calculator", calculator)
builder.add_node("search", search)
builder.add_node("chat", chat)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    router,
    {
        "calculator": "calculator",
        "search": "search",
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