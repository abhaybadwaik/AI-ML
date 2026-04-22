# 🧠 WHAT YOU WILL SEE (IMPORTANT 🔥)
# 🔄 Graph Streaming
# 📌 Node Completed: {'explain': ...}
# 📌 Node Completed: {'summarize': ...}
# 📌 Node Completed: {'format': ...}
# 👉 Live typing 🔥


import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq

# 🔑 Load API
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    streaming=True  # 🔥 enable LLM streaming
)

# 🧠 Step 1: Explain (LLM streaming inside)
def explain(state):
    print("\n🔹 [Explain Step]")

    full_text = ""

    for chunk in llm.stream(f"Explain: {state['input']}"):
        print(chunk.content, end="", flush=True)
        full_text += chunk.content

    print("\n")  # spacing
    state["explain"] = full_text
    return state

# 🧠 Step 2: Summarize (LLM streaming inside)
def summarize(state):
    print("\n🔹 [Summarize Step]")

    full_text = ""

    for chunk in llm.stream(f"Summarize:\n{state['explain']}"):
        print(chunk.content, end="", flush=True)
        full_text += chunk.content

    print("\n")
    state["summary"] = full_text
    return state

# 🧠 Step 3: Format
def format_output(state):
    print("\n🔹 [Format Step]")
    state["final"] = "👉 " + state["summary"]
    print(state["final"])
    return state

# 🔧 Build Graph
builder = StateGraph(dict)

builder.add_node("explain", explain)
builder.add_node("summarize", summarize)
builder.add_node("format", format_output)

builder.set_entry_point("explain")
builder.add_edge("explain", "summarize")
builder.add_edge("summarize", "format")

graph = builder.compile()

# 🚀 RUN WITH GRAPH STREAMING
user_input = input("You: ")

print("\n🚀 Starting Combined Streaming...\n")

for step in graph.stream({"input": user_input}):
    print("\n📌 Node Completed:", step)