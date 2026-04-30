from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timezone
from agent import graph, ClusterState
from config import settings

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

    try:
        result = graph.invoke(initial_state)

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


# ─────────────────────────────────────────────
# Scheduler setup
# ─────────────────────────────────────────────
if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone=settings.timezone)

    # Add monitoring job
    scheduler.add_job(
        run_monitoring_cycle,
        trigger="interval",
        minutes=settings.interval_minutes,
        id="ocp_monitor",
        next_run_time=datetime.now()  # Run immediately on start
    )

    print("="*60)
    print("  OCP AI MONITORING AGENT STARTED")
    print(f"  Interval : every {settings.interval_minutes} minutes")
    print(f"  Timezone : {settings.timezone}")
    print(f"  Press Ctrl+C to stop")
    print("="*60)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n  Agent stopped by user.")
        scheduler.shutdown()