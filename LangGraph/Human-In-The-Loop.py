from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from typing import TypedDict

# --- State ---
class State(TypedDict):
    topic: str
    draft: str
    approved: bool
    feedback: str

# --- Node 1: Agent drafts an email based on YOUR topic ---
def draft_email(state: State):
    topic = state["topic"]
    draft = f"Subject: {topic}\n\nHi team,\n\nThis is a reminder about: {topic}.\nPlease take necessary action.\n\nRegards,\nAI Assistant"
    print(f"\n📝 Agent drafted this email:\n")
    print("─" * 40)
    print(draft)
    print("─" * 40)
    return {"draft": draft}

# --- Node 2: Human reviews ---
def human_review(state: State):
    decision = interrupt("waiting_for_human")
    return {"approved": decision["approved"], "feedback": decision["feedback"]}

# --- Node 3: Final action ---
def send_or_cancel(state: State):
    if state["approved"]:
        print(f"\n✅ Email SENT successfully!")
        print(f"📨 Final email:\n{state['draft']}")
    else:
        print(f"\n❌ Email CANCELLED.")
        print(f"💬 Your feedback was: {state['feedback']}")
        print("🔁 In a real system, the agent would redraft based on your feedback.")
    return {}

# --- Build graph ---
builder = StateGraph(State)
builder.add_node("draft_email", draft_email)
builder.add_node("human_review", human_review)
builder.add_node("send_or_cancel", send_or_cancel)

builder.add_edge(START, "draft_email")
builder.add_edge("draft_email", "human_review")
builder.add_edge("human_review", "send_or_cancel")
builder.add_edge("send_or_cancel", END)

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# --- MAIN INTERACTIVE FLOW ---
print("=" * 50)
print("   HUMAN-IN-THE-LOOP EMAIL AGENT")
print("=" * 50)

# Step 1: Take topic from user
topic = input("\n📌 Enter email topic (e.g. 'Team meeting tomorrow at 3pm'): ").strip()

config = {"configurable": {"thread_id": "hitl-test-1"}}

# Step 2: Run graph — it will pause at interrupt()
print("\n🤖 Agent is drafting your email...\n")
for event in graph.stream({"topic": topic, "draft": "", "approved": False, "feedback": ""}, config):
    if "__interrupt__" in event:
        print("\n⏸️  Graph PAUSED — waiting for your review.")

# Step 3: Human reviews and decides
print("\n👀 What do you want to do?")
print("   Type 'yes' to APPROVE and send")
print("   Type 'no'  to REJECT and cancel")
choice = input("\nYour decision: ").strip().lower()

if choice == "yes":
    resume_value = {"approved": True, "feedback": ""}
else:
    feedback = input("💬 Enter your feedback (why rejected?): ").strip()
    resume_value = {"approved": False, "feedback": feedback}

# Step 4: Resume the graph with human's decision
print("\n▶️  Resuming graph with your decision...\n")
for event in graph.stream(Command(resume=resume_value), config):
    if "__interrupt__" not in event:
        pass

print("\n" + "=" * 50)
print("   GRAPH COMPLETED")
print("=" * 50)