from datetime import datetime, timezone
from agent import graph, ClusterState

print("Starting full pipeline with LLM analysis...\n")

initial_state = ClusterState(
    timestamp=datetime.now(timezone.utc).isoformat(),
    collected_at="",
    collection_errors=[],
    nodes=[], operators=[], mcpools=[],
    etcd={}, pvcs=[], pods=[], certs=[],
    failures=[], resolutions=[],
    summary="", report_html="", email_sent=False
)

result = graph.invoke(initial_state)

print("\n─── LLM Results ───")
print(f"Summary  : {result['summary']}")
print(f"Failures : {len(result['failures'])}")
for f in result['failures']:
    print(f"  [{f['severity']}] {f['component']}: {f['message']}")
print(f"Resolutions: {len(result['resolutions'])}")
print("\nLLM pipeline working!")