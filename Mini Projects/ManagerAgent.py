from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# 👑 Manager Agent
def manager(state):
    question = state["input"]

    response = llm.invoke(
        f"""
        Decide the task:
        - 'research' for explanation
        - 'summarize' for short summary

        Input: {question}
        """
    )

    decision = response.content.lower()

    if "summarize" in decision:
        return "summarizer"
    else:
        return "researcher"

# 🤖 Research Agent
def researcher(state):
    topic = state["input"]

    response = llm.invoke(f"Explain clearly: {topic}")

    state["result"] = response.content
    return state

# 🤖 Summarizer Agent
def summarizer(state):
    topic = state["input"]

    response = llm.invoke(f"Summarize in 2 lines: {topic}")

    state["result"] = response.content
    return state

# 🔧 Build Graph
builder = StateGraph(dict)

builder.add_node("manager", lambda state: state)
builder.add_node("researcher", researcher)
builder.add_node("summarizer", summarizer)

builder.set_entry_point("manager")

builder.add_conditional_edges(
    "manager",
    manager,
    {
        "researcher": "researcher",
        "summarizer": "summarizer"
    }
)

graph = builder.compile()

# 🚀 Run
while True:
    user_input = input("You: ")

    if user_input.lower() == "bye":
        break

    result = graph.invoke({"input": user_input})

    print("AI:", result["result"])