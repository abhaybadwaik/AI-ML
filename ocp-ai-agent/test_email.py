from datetime import datetime, timezone
from agent import graph, ClusterState

print("Starting full pipeline with email...\n")

initial_state = ClusterState(
    timestamp=datetime.now(timezone.utc).isoformat(),
    collected_at="", collection_errors=[],
    nodes=[], operators=[], mcpools=[],
    etcd={}, pvcs=[], pods=[], certs=[],
    failures=[], resolutions=[],
    summary="", report_html="", email_sent=False
)

result = graph.invoke(initial_state)

print("\n─── Final Results ───")
print(f"Failures   : {len(result['failures'])}")
print(f"Summary    : {result['summary'][:80]}...")
print(f"Email Sent : {result['email_sent']}")