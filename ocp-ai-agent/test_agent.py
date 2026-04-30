from datetime import datetime, timezone
from agent import graph, ClusterState

print("Starting OCP monitoring pipeline...\n")

# Initial empty state
initial_state = ClusterState(
    timestamp=datetime.now(timezone.utc).isoformat(),
    collected_at="",
    collection_errors=[],
    nodes=[],
    operators=[],
    mcpools=[],
    etcd={},
    pvcs=[],
    pods=[],
    certs=[],
    failures=[],
    resolutions=[],
    summary="",
    report_html="",
    email_sent=False
)

# Run the graph
result = graph.invoke(initial_state)

print("\n─── Pipeline Results ───")
print(f"Nodes        : {len(result['nodes'])}")
print(f"Operators    : {len(result['operators'])}")
print(f"MCPools      : {len(result['mcpools'])}")
print(f"PVC Issues   : {len(result['pvcs'])}")
print(f"Failing Pods : {len(result['pods'])}")
print(f"Expiring Cert: {len(result['certs'])}")
print(f"Failures     : {len(result['failures'])}")
print(f"Collected at : {result['collected_at']}")
print(f"Errors       : {result['collection_errors']}")
print("\nAgent pipeline working!")