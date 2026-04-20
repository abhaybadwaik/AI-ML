import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# 🔑 Load API
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)


# 🤖 Step 1: Generate Email Draft
def generate_draft(state):
    prompt = f"Write a professional email for: {state['input']}"
    response = llm.invoke(prompt)

    state["draft"] = response.content
    return state

# 👨 Step 2: Human Review
def human_review(state):
    print("\n📧 AI Draft:\n", state["draft"])
    
    approval = input("\nApprove this email? (yes/no): ")
    feedback = ""

    if approval == "no":
        feedback = input("What should be improved?: ")

    state["approved"] = approval
    state["feedback"] = feedback
    return state

# 🧠 Step 3: Decision
def decision(state):
    if state["approved"] == "yes":
        return "final"
    else:
        return "improve"

# 🔁 Step 4: Improve Draft using feedback
def improve_draft(state):
    prompt = f"""
    Improve this email based on feedback:
    
    Email:
    {state['draft']}
    
    Feedback:
    {state['feedback']}
    """

    response = llm.invoke(prompt)

    state["draft"] = response.content
    return state

# ✅ Final Step
def final(state):
    state["result"] = state["draft"]
    return state

# 🔧 Build Graph
builder = StateGraph(dict)

builder.add_node("generate_draft", generate_draft)
builder.add_node("human_review", human_review)
builder.add_node("improve", improve_draft)
builder.add_node("final", final)

builder.set_entry_point("generate_draft")

builder.add_edge("generate_draft", "human_review")

builder.add_conditional_edges(
    "human_review",
    decision,
    {
        "final": "final",
        "improve": "improve"
    }
)

builder.add_edge("improve", "human_review")

graph = builder.compile()

# 🚀 Run
user_input = input("Enter email topic: ")

result = graph.invoke({"input": user_input})

print("\n✅ Final Approved Email:\n")
print(result["result"])