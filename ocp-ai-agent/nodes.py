from datetime import datetime, timezone
from tools import (
    get_node_status,
    get_cluster_operators,
    get_machine_config_pools,
    get_etcd_health,
    get_pvc_issues,
    get_failing_pods,
    get_expiring_certs,
)


# ─────────────────────────────────────────────
# Node 1: Collect Node Status
# ─────────────────────────────────────────────
def collect_nodes_node(state: dict) -> dict:
    print("  [1/7] Collecting node status...")
    try:
        data = get_node_status.invoke({})
        return {"nodes": data}
    except Exception as e:
        print(f"  ERROR in collect_nodes: {e}")
        return {"nodes": [], "collection_errors": state.get("collection_errors", []) + [str(e)]}


# ─────────────────────────────────────────────
# Node 2: Collect Cluster Operators
# ─────────────────────────────────────────────
def collect_operators_node(state: dict) -> dict:
    print("  [2/7] Collecting cluster operators...")
    try:
        data = get_cluster_operators.invoke({})
        return {"operators": data}
    except Exception as e:
        print(f"  ERROR in collect_operators: {e}")
        return {"operators": [], "collection_errors": state.get("collection_errors", []) + [str(e)]}


# ─────────────────────────────────────────────
# Node 3: Collect MachineConfigPools
# ─────────────────────────────────────────────
def collect_mcp_node(state: dict) -> dict:
    print("  [3/7] Collecting MachineConfigPools...")
    try:
        data = get_machine_config_pools.invoke({})
        return {"mcpools": data}
    except Exception as e:
        print(f"  ERROR in collect_mcp: {e}")
        return {"mcpools": [], "collection_errors": state.get("collection_errors", []) + [str(e)]}


# ─────────────────────────────────────────────
# Node 4: Collect etcd Health
# ─────────────────────────────────────────────
def collect_etcd_node(state: dict) -> dict:
    print("  [4/7] Collecting etcd health...")
    try:
        data = get_etcd_health.invoke({})
        return {"etcd": data}
    except Exception as e:
        print(f"  ERROR in collect_etcd: {e}")
        return {"etcd": {}, "collection_errors": state.get("collection_errors", []) + [str(e)]}


# ─────────────────────────────────────────────
# Node 5: Collect PVC Issues
# ─────────────────────────────────────────────
def collect_pvcs_node(state: dict) -> dict:
    print("  [5/7] Collecting PVC issues...")
    try:
        data = get_pvc_issues.invoke({})
        return {"pvcs": data}
    except Exception as e:
        print(f"  ERROR in collect_pvcs: {e}")
        return {"pvcs": [], "collection_errors": state.get("collection_errors", []) + [str(e)]}


# ─────────────────────────────────────────────
# Node 6: Collect Failing Pods
# ─────────────────────────────────────────────
def collect_pods_node(state: dict) -> dict:
    print("  [6/7] Collecting failing pods...")
    try:
        data = get_failing_pods.invoke({})
        return {"pods": data}
    except Exception as e:
        print(f"  ERROR in collect_pods: {e}")
        return {"pods": [], "collection_errors": state.get("collection_errors", []) + [str(e)]}


# ─────────────────────────────────────────────
# Node 7: Collect Expiring Certificates
# ─────────────────────────────────────────────
def collect_certs_node(state: dict) -> dict:
    print("  [7/7] Collecting expiring certificates...")
    try:
        data = get_expiring_certs.invoke({})
        return {"certs": data}
    except Exception as e:
        print(f"  ERROR in collect_certs: {e}")
        return {"certs": [], "collection_errors": state.get("collection_errors", []) + [str(e)]}


# ─────────────────────────────────────────────
# Node 8: Aggregate — validate + timestamp
# ─────────────────────────────────────────────
def aggregate_node(state: dict) -> dict:
    print("\n  [Aggregating collected data...]")
    errors = state.get("collection_errors", [])
    if errors:
        print(f"  WARNING: {len(errors)} collection error(s): {errors}")
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collection_errors": errors
    }

# ─────────────────────────────────────────────
# Node 9: Analyze — LLM analysis
# ─────────────────────────────────────────────
def analyze_node(state: dict) -> dict:
    from llm_chains import run_analysis
    failures, summary = run_analysis(state)
    return {"failures": failures, "summary": summary}


# ─────────────────────────────────────────────
# Node 10: Resolve — LLM resolution
# ─────────────────────────────────────────────
def resolve_node(state: dict) -> dict:
    from llm_chains import run_resolution
    resolutions = run_resolution(state.get("failures", []))
    return {"resolutions": resolutions}

# ─────────────────────────────────────────────
# Node 11: Build Report
# ─────────────────────────────────────────────
def build_report_node(state: dict) -> dict:
    from reporter import build_report
    print("\n  [Report] Building HTML report...")
    html = build_report(state)
    return {"report_html": html}

# ─────────────────────────────────────────────
# Node 12: Send Email
# ─────────────────────────────────────────────
def send_email_node(state: dict) -> dict:
    from emailer import send_report
    print("\n  [Email] Sending report...")
    success = send_report(state)
    return {"email_sent": success}