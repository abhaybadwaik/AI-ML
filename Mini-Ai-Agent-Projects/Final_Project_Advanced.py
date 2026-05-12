# 🧠 What we are building

# 👉 A Smart AI Team 🤖🤖🤖

# 👑 Manager (decides)
# 🔍 Researcher (explains)
# ✍️ Writer (creates content)
# 📌 Formatter (bullet points)

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

# 👑 Manager Agent
def manager(state):
    query = state["input"]

    response = llm.invoke(
        f"""
        Decide task type:
        - 'simple' → direct answer
        - 'detailed' → full explanation pipeline

        Input: {query}
        """
    )

    decision = response.content.lower()

    if "simple" in decision:
        return "chat"
    else:
        return "researcher"

# 🤖 Chat Agent (simple)
def chat(state):
    response = llm.invoke(state["input"])
    state["final"] = response.content
    return state

# 🔍 Researcher Agent
def researcher(state):
    topic = state["input"]

    response = llm.invoke(f"Explain in detail: {topic}")

    state["research"] = response.content
    return state

# ✍️ Writer Agent
def writer(state):
    research = state["research"]

    response = llm.invoke(f"Convert this into structured content:\n{research}")

    state["content"] = response.content
    return state

# 📌 Formatter Agent
def formatter(state):
    content = state["content"]

    response = llm.invoke(f"Convert into bullet points:\n{content}")

    state["final"] = response.content
    return state

# 🔧 Build Graph
builder = StateGraph(dict)

builder.add_node("manager", lambda state: state)
builder.add_node("chat", chat)
builder.add_node("researcher", researcher)
builder.add_node("writer", writer)
builder.add_node("formatter", formatter)

builder.set_entry_point("manager")

# Manager decisions
builder.add_conditional_edges(
    "manager",
    manager,
    {
        "chat": "chat",
        "researcher": "researcher"
    }
)

# Multi-agent pipeline
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "formatter")

graph = builder.compile()

# 🚀 Run
print("🤖 Advanced Multi-Agent System Started (type 'bye' to exit)")

while True:
    user_input = input("You: ")

    if user_input.lower() == "bye":
        print("AI: Goodbye 👋")
        break

    result = graph.invoke({"input": user_input})

    print("\n📌 Final Output:")
    print(result["final"])