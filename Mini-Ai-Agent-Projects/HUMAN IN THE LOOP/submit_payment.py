import uuid
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
    print(f"[1] Running risk analysis for ₹{state['amount']}")
    score = 0.9 if state["amount"] > 100000 else 0.2
    print(f"[1] Risk score: {score}")
    return {"risk_score": score}

def route_by_risk(state: PaymentState):
    if state["risk_score"] > 0.7:
        print("[2] HIGH RISK — graph will pause for human review")
        return "human_review"
    print("[2] Low risk — auto approving")
    return "auto_approve"

def human_review(state: PaymentState):
    print(f"[3] Human decision received: {state['human_decision']}")
    if state["human_decision"] == "approved":
        return {"status": "compliance_approved"}
    return {"status": "compliance_rejected"}

def execute_transfer(state: PaymentState):
    print(f"✅ Transfer EXECUTED for {state['transaction_id']}")
    return {"status": "completed"}

def decline_transfer(state: PaymentState):
    print(f"❌ Transfer DECLINED for {state['transaction_id']}")
    return {"status": "declined"}

# User input
amount = float(input("Enter transfer amount (₹): ").strip())
transaction_id = f"txn-{uuid.uuid4().hex[:6]}"
print(f"Generated Transaction ID: {transaction_id}")

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()

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

    config = {"configurable": {"thread_id": transaction_id}}

    print("\n=== Submitting payment ===")
    graph.invoke({
        "transaction_id": transaction_id,
        "amount": amount,
        "risk_score": None,
        "human_decision": None,
        "status": "pending"
    }, config)

    print(f"\n=== Graph paused. Transaction ID: {transaction_id} ===")
    print("=== Run check_status.py to see pending transactions ===")