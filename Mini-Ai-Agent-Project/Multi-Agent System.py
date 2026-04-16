from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv


# 🔑 Load API
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# 🤖 Agent 1 → Researcher
def researcher(state):
    topic = state["input"]

    response = llm.invoke(f"Explain this topic clearly: {topic}")

    state["research"] = response.content
    return state

# 🤖 Agent 2 → Summarizer
def summarizer(state):
    research = state["research"]

    response = llm.invoke(f"Convert to bullet points: {research}")

    state["final"] = response.content
    return state

# 🔧 Build Graph
builder = StateGraph(dict)

builder.add_node("researcher", researcher)
builder.add_node("summarizer", summarizer)

builder.set_entry_point("researcher")

builder.add_edge("researcher", "summarizer")

graph = builder.compile()

# 🚀 Run
user_input = input("Enter topic: ")

result = graph.invoke({"input": user_input})

print("\n📌 Final Output:")
print(result["final"])



# 🧠 What’s Happening?

# 👉 Agent 1:

# Understands topic
# Generates detailed explanation

# 👉 Agent 2:

# Takes that explanation
# Converts into short summary