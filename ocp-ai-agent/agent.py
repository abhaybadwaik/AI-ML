from typing import TypedDict, List
from nodes import analyze_node, resolve_node
from nodes import build_report_node
from nodes import send_email_node
from langgraph.graph import StateGraph, END
from nodes import (
    collect_nodes_node,
    collect_operators_node,
    collect_mcp_node,
    collect_etcd_node,
    collect_pvcs_node,
    collect_pods_node,
    collect_certs_node,
    aggregate_node,
    resolve_node,
    build_report_node
)


# ─────────────────────────────────────────────
# ClusterState — shared memory of the pipeline
# Every node reads from and writes to this
# ─────────────────────────────────────────────
class ClusterState(TypedDict):
    # Timestamp
    timestamp: str
    collected_at: str
    collection_errors: List[str]

    # Raw collected data
    nodes: List[dict]
    operators: List[dict]
    mcpools: List[dict]
    etcd: dict
    pvcs: List[dict]
    pods: List[dict]
    certs: List[dict]

    # LLM outputs
    failures: List[dict]
    resolutions: List[dict]
    summary: str

    # Report + email
    report_html: str
    email_sent: bool


# ─────────────────────────────────────────────
# Conditional routing — the intelligence gate
# Only call resolution LLM if failures exist
# ─────────────────────────────────────────────
def route_after_analysis(state: ClusterState) -> str:
    if state.get("failures"):
        print(f"\n  ⚠ {len(state['failures'])} failure(s) found → running resolution...")
        return "resolve"
    print("\n  ✓ No failures found → skipping resolution...")
    return "build_report"


# ─────────────────────────────────────────────
# Build the LangGraph StateGraph
# ─────────────────────────────────────────────
def build_graph():
    builder = StateGraph(ClusterState)

    # ── Add all nodes ──
    builder.add_node("collect_nodes", collect_nodes_node)
    builder.add_node("collect_operators", collect_operators_node)
    builder.add_node("collect_mcp", collect_mcp_node)
    builder.add_node("collect_etcd", collect_etcd_node)
    builder.add_node("collect_pvcs", collect_pvcs_node)
    builder.add_node("collect_pods", collect_pods_node)
    builder.add_node("collect_certs", collect_certs_node)
    builder.add_node("aggregate", aggregate_node)

    # Placeholder nodes — we build these next
    builder.add_node("analyze", analyze_node)
    builder.add_node("resolve", resolve_node)
    builder.add_node("build_report", build_report_node)
    builder.add_node("send_email", send_email_node)

    # ── Wire the collection chain ──
    builder.set_entry_point("collect_nodes")
    builder.add_edge("collect_nodes", "collect_operators")
    builder.add_edge("collect_operators", "collect_mcp")
    builder.add_edge("collect_mcp", "collect_etcd")
    builder.add_edge("collect_etcd", "collect_pvcs")
    builder.add_edge("collect_pvcs", "collect_pods")
    builder.add_edge("collect_pods", "collect_certs")
    builder.add_edge("collect_certs", "aggregate")

    # ── After aggregate → analyze ──
    builder.add_edge("aggregate", "analyze")

    # ── Conditional routing after analysis ──
    builder.add_conditional_edges(
        "analyze",
        route_after_analysis,
        {
            "resolve": "resolve",
            "build_report": "build_report"
        }
    )

    # ── Final chain ──
    builder.add_edge("resolve", "build_report")
    builder.add_edge("build_report", "send_email")
    builder.add_edge("send_email", END)

    return builder.compile()


# Compile the graph once at import time
graph = build_graph()