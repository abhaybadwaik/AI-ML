# from langgraph.graph import StateGraph

# # Step 1
# def step1(state):
#     state["msg"] += " Hello"
#     return state

# # Step 2
# def step2(state):
#     state["msg"] += " World"
#     return state

# # Create graph
# builder = StateGraph(dict)

# builder.add_node("step1", step1)
# builder.add_node("step2", step2)

# builder.set_entry_point("step1")
# builder.add_edge("step1", "step2")

# graph = builder.compile()

# result = graph.invoke({"msg": ""})

# print(result)

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq

# 🔑 Load API
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# Step 1 → Generate explanation
def explain(state):
    response = llm.invoke(f"Explain: {state['input']}")
    state["step1"] = response.content
    return state

# Step 2 → Summarize
def summarize(state):
    response = llm.invoke(f"Summarize this:\n{state['step1']}")
    state["step2"] = response.content
    return state

# Step 3 → Format
def format_output(state):
    state["final"] = "👉 " + state["step2"]
    return state

# Build graph
builder = StateGraph(dict)

builder.add_node("explain", explain)
builder.add_node("summarize", summarize)
builder.add_node("format", format_output)

builder.set_entry_point("explain")
builder.add_edge("explain", "summarize")
builder.add_edge("summarize", "format")

graph = builder.compile()

# 🔥 STREAMING EXECUTION
user_input = input("You: ")

print("\n🔄 Streaming...\n")

for step in graph.stream({"input": user_input}):
    print(step)