from datetime import datetime, timezone
from agent import graph, ClusterState

initial_state = ClusterState(
    timestamp=datetime.now(timezone.utc).isoformat(),
    collected_at="", collection_errors=[],
    nodes=[], operators=[], mcpools=[],
    etcd={}, pvcs=[], pods=[], certs=[],
    failures=[], resolutions=[],
    summary="", report_html="", email_sent=False
)

result = graph.invoke(initial_state)

# Save report to file so you can open it in browser
with open("test_report.html", "w", encoding="utf-8") as f:
    f.write(result["report_html"])

print("Report saved to test_report.html")
print("Open it in your browser to preview!")