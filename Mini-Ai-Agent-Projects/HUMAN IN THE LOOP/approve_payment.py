import psycopg
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import TypedDict, Literal

DB_URI = "postgresql://postgres:secret@localhost:5432/langgraph"

class PaymentState(TypedDict):
    transaction_id: str
    amount: float
    risk_score: float | None
    human_decision: Literal["approved", "rejected"] | None
    status: str

def risk_analysis(state: PaymentState):
    score = 0.9 if state["amount"] > 100000 else 0.2
    return {"risk_score": score}

def route_by_risk(state: PaymentState):
    if state["risk_score"] > 0.7:
        return "human_review"
    return "auto_approve"

def human_review(state: PaymentState):
    print(f"[Node] Human decision received: {state['human_decision']}")
    if state["human_decision"] == "approved":
        return {"status": "compliance_approved"}
    return {"status": "compliance_rejected"}

def execute_transfer(state: PaymentState):
    print(f"✅ Transfer EXECUTED for {state['transaction_id']}")
    return {"status": "completed"}

def decline_transfer(state: PaymentState):
    print(f"❌ Transfer DECLINED for {state['transaction_id']}")
    return {"status": "declined"}

# Show pending transactions
print("\n=== Pending Transactions ===\n")
pending = []

with psycopg.connect(DB_URI) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT thread_id, checkpoint FROM checkpoints ORDER BY checkpoint->>'ts' DESC")
        rows = cur.fetchall()

        seen = {}
        for row in rows:
            thread_id = row[0]
            checkpoint = row[1]
            channel_values = checkpoint.get("channel_values", {})

            if channel_values.get("amount") and thread_id not in seen:
                seen[thread_id] = {
                    "amount": channel_values.get("amount"),
                    "risk_score": channel_values.get("risk_score"),
                    "status": channel_values.get("status"),
                    "human_decision": channel_values.get("human_decision")
                }

        for thread_id, data in seen.items():
            if data["human_decision"] is None and data["status"] == "pending":
                pending.append(thread_id)
                print(f"  [{len(pending)}] {thread_id} — ₹{data['amount']} — Risk: {data['risk_score']}")

if not pending:
    print("No pending transactions found.")
    exit()

# Ask compliance officer which one to act on
print()
choice = int(input("Enter number of transaction to review: ").strip()) - 1
thread_id = pending[choice]

decision = input(f"Enter decision for {thread_id} (approved/rejected): ").strip()

# Resume the graph
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    builder = StateGraph(PaymentState)
    builder.add_node("risk_analysis", risk_analysis)
    builder.add_node("human_review", human_review)
    builder.add_node("execute_transfer", execute_transfer)
    builder.add_node("decline_transfer", decline_transfer)

    builder.set_entry_point("risk_analysis")
    builder.add_conditional_edges("risk_analysis", route_by_risk, {
        "human_review": "human_review",
        "auto_approve": "execute_transfer"
    })
    builder.add_conditional_edges("human_review", lambda s: s["status"], {
        "compliance_approved": "execute_transfer",
        "compliance_rejected": "decline_transfer"
    })
    builder.add_edge("execute_transfer", END)
    builder.add_edge("decline_transfer", END)

    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]
    )

    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n=== Resuming {thread_id} with decision: {decision} ===")
    graph.update_state(config, {"human_decision": decision})
    graph.invoke(None, config)

    print("\n=== Done. Run check_status.py to verify ===")