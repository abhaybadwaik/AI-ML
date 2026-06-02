from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# 🤖 Agent 1 → Writer
def writer(state):
    topic = state["input"]

    response = llm.invoke(f"Write a clear explanation on: {topic}")

    state["draft"] = response.content
    return state

# 🤖 Agent 2 → Reviewer
def reviewer(state):
    draft = state["draft"]

    response = llm.invoke(f"Improve this explanation:\n{draft}")

    state["improved"] = response.content
    return state

# 🤖 Agent 1 again → Refiner
def refiner(state):
    improved = state["improved"]

    response = llm.invoke(f"Make this more simple and clear:\n{improved}")

    state["final"] = response.content
    return state

# 🔧 Build Graph
builder = StateGraph(dict)

builder.add_node("writer", writer)
builder.add_node("reviewer", reviewer)
builder.add_node("refiner", refiner)

builder.set_entry_point("writer")

builder.add_edge("writer", "reviewer")
builder.add_edge("reviewer", "refiner")

graph = builder.compile()

# 🚀 Run
user_input = input("Enter topic: ")

result = graph.invoke({"input": user_input})

print("\n📌 Final Output:")
print(result["final"])