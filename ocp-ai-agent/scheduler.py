from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timezone
from threading import Thread
from agent import graph, ClusterState
from config import settings
from dashboard import update_dashboard, run_dashboard


def run_monitoring_cycle():
    """Single monitoring cycle — collect, analyze, report, email."""
    print("\n" + "="*60)
    print(f"  OCP MONITORING CYCLE STARTED")
    print(f"  Time: {datetime.now(timezone.utc).isoformat()}")
    print("="*60)

    initial_state = ClusterState(
        timestamp=datetime.now(timezone.utc).isoformat(),
        collected_at="",
        collection_errors=[],
        nodes=[], operators=[], mcpools=[],
        etcd={}, pvcs=[], pods=[], certs=[],
        failures=[], resolutions=[],
        summary="", report_html="", email_sent=False
    )

    try:
        result = graph.invoke(initial_state)

        # Update dashboard with latest result
        update_dashboard(result)

        print("\n" + "="*60)
        print("  CYCLE COMPLETE")
        print(f"  Nodes        : {len(result['nodes'])}")
        print(f"  Operators    : {len(result['operators'])}")
        print(f"  Failures     : {len(result['failures'])}")
        print(f"  Email Sent   : {result['email_sent']}")
        print(f"  Errors       : {result['collection_errors']}")
        print("="*60)

    except Exception as e:
        print(f"\n  ❌ Cycle failed: {e}")


if __name__ == "__main__":
    # Start dashboard in background thread
    print("="*60)
    print("  Starting dashboard on http://localhost:5000")
    dashboard_thread = Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()

    # Start scheduler
    scheduler = BlockingScheduler(timezone=settings.timezone)
    scheduler.add_job(
        run_monitoring_cycle,
        trigger="interval",
        minutes=settings.interval_minutes,
        id="ocp_monitor",
        next_run_time=datetime.now()
    )

    print("  OCP AI MONITORING AGENT STARTED")
    print(f"  Interval  : every {settings.interval_minutes} minutes")
    print(f"  Dashboard : http://localhost:5000")
    print(f"  Press Ctrl+C to stop")
    print("="*60)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n  Agent stopped.")
        scheduler.shutdown()