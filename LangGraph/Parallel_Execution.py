import os
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from operator import add
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq

# 🔑 Load API
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# 🧠 State
class State(TypedDict):
    input: str
    results: Annotated[list, add]

# 🔹 Explain
def explain(state):
    res = llm.invoke(f"Explain: {state['input']}")
    return {"results": [f"Explain: {res.content}"]}

# 🔹 Summarize
def summarize(state):
    res = llm.invoke(f"Summarize: {state['input']}")
    return {"results": [f"Summary: {res.content}"]}

# 🔹 Translate
def translate(state):
    res = llm.invoke(f"Translate to Hindi: {state['input']}")
    return {"results": [f"Hindi: {res.content}"]}

# 🔹 Final merge
def final(state):
    combined = "\n\n".join(state["results"])
    return {"results": [combined]}

# 🔧 Build graph
builder = StateGraph(State)

builder.add_node("start", lambda x: x)
builder.add_node("explain", explain)
builder.add_node("summarize", summarize)
builder.add_node("translate", translate)
builder.add_node("final", final)

builder.set_entry_point("start")

# 🔥 Fan-out
builder.add_edge("start", "explain")
builder.add_edge("start", "summarize")
builder.add_edge("start", "translate")

# 🔥 Merge pattern
builder.add_edge("explain", "final")
builder.add_edge("summarize", "final")
builder.add_edge("translate", "final")

graph = builder.compile()

# 🚀 Run
user_input = input("You: ")

result = graph.invoke({"input": user_input})

print("\n📊 Final Output:\n")
print(result["results"][0])