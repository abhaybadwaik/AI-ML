from datetime import datetime, timezone


def build_report(state: dict) -> str:
    """Build a professional HTML health check report from cluster state."""

    timestamp = state.get("collected_at", datetime.now(timezone.utc).isoformat())
    summary = state.get("summary", "No summary available.")
    failures = state.get("failures", [])
    resolutions = state.get("resolutions", [])
    nodes = state.get("nodes", [])
    operators = state.get("operators", [])
    mcpools = state.get("mcpools", [])
    etcd = state.get("etcd", {})
    pvcs = state.get("pvcs", [])
    pods = state.get("pods", [])
    certs = state.get("certs", [])
    errors = state.get("collection_errors", [])

    # Overall status
    critical = [f for f in failures if f.get("severity") == "CRITICAL"]
    warnings = [f for f in failures if f.get("severity") == "WARNING"]
    overall_color = "#d32f2f" if critical else "#f57c00" if warnings else "#388e3c"
    overall_text = "CRITICAL" if critical else "WARNING" if warnings else "HEALTHY"

    # ── Nodes table rows ──
    node_rows = ""
    for n in nodes:
        ready_color = "#388e3c" if n.get("ready") else "#d32f2f"
        ready_text = "Ready" if n.get("ready") else "Not Ready"
        issues = []
        if n.get("disk_pressure"): issues.append("DiskPressure")
        if n.get("memory_pressure"): issues.append("MemoryPressure")
        if n.get("pid_pressure"): issues.append("PIDPressure")
        issues_text = ", ".join(issues) if issues else "None"
        node_rows += f"""
        <tr>
            <td>{n.get('name', '')}</td>
            <td>{', '.join(n.get('roles', []))}</td>
            <td style="color:{ready_color};font-weight:bold">{ready_text}</td>
            <td>{issues_text}</td>
        </tr>"""

    # ── Operators table rows ──
    op_rows = ""
    degraded_ops = [o for o in operators if o.get("degraded") == "True"]
    for o in operators:
        avail_color = "#388e3c" if o.get("available") == "True" else "#d32f2f"
        deg_color = "#d32f2f" if o.get("degraded") == "True" else "#388e3c"
        op_rows += f"""
        <tr>
            <td>{o.get('name', '')}</td>
            <td style="color:{avail_color};font-weight:bold">{o.get('available', '')}</td>
            <td style="color:{deg_color};font-weight:bold">{o.get('degraded', '')}</td>
            <td style="font-size:11px">{o.get('message', '')[:80]}</td>
        </tr>"""

    # ── Failures + Resolutions ──
    failures_html = ""
    if not failures:
        failures_html = """
        <div style="background:#e8f5e9;border-left:4px solid #388e3c;padding:15px;border-radius:4px">
            ✅ No failures detected. All systems are operating normally.
        </div>"""
    else:
        res_map = {r.get("failure_id"): r for r in resolutions}
        for f in failures:
            sev = f.get("severity", "INFO")
            sev_color = "#d32f2f" if sev == "CRITICAL" else "#f57c00" if sev == "WARNING" else "#1976d2"
            res = res_map.get(f.get("id"), {})
            steps_html = "".join(
                f"<li>{s}</li>" for s in res.get("steps", [])
            )
            commands_html = "".join(
                f"<code style='display:block;background:#263238;color:#80cbc4;"
                f"padding:4px 8px;margin:2px 0;border-radius:3px;font-size:12px'>{c}</code>"
                for c in res.get("commands", [])
            )
            failures_html += f"""
            <div style="border:1px solid {sev_color};border-radius:6px;
                        margin-bottom:15px;overflow:hidden">
                <div style="background:{sev_color};color:white;padding:10px 15px">
                    <strong>[{sev}]</strong> {f.get('component', '')}
                </div>
                <div style="padding:15px">
                    <p><strong>Issue:</strong> {f.get('message', '')}</p>
                    {"<p><strong>Root Cause:</strong> " + res.get('root_cause','') + "</p>" if res.get('root_cause') else ""}
                    {"<p><strong>Steps:</strong></p><ol>" + steps_html + "</ol>" if steps_html else ""}
                    {"<p><strong>Commands:</strong></p>" + commands_html if commands_html else ""}
                    {"<p><strong>Docs:</strong> <a href='" + res.get('docs_ref','') + "'>" + res.get('docs_ref','') + "</a></p>" if res.get('docs_ref') else ""}
                </div>
            </div>"""

    # ── MCP rows ──
    mcp_rows = ""
    for m in mcpools:
        deg = m.get("degraded_machine_count", 0)
        deg_color = "#d32f2f" if deg > 0 else "#388e3c"
        mcp_rows += f"""
        <tr>
            <td>{m.get('name','')}</td>
            <td>{m.get('machine_count',0)}</td>
            <td>{m.get('ready_machine_count',0)}</td>
            <td style="color:{deg_color};font-weight:bold">{deg}</td>
        </tr>"""

    # ── etcd status ──
    etcd_healthy = etcd.get("healthy", False)
    etcd_color = "#388e3c" if etcd_healthy else "#d32f2f"
    etcd_text = "Healthy" if etcd_healthy else "Unhealthy"

    # ── PVC rows ──
    pvc_rows = ""
    if not pvcs:
        pvc_rows = "<tr><td colspan='4' style='color:#388e3c'>No PVC issues found</td></tr>"
    for p in pvcs:
        pvc_rows += f"""
        <tr>
            <td>{p.get('name','')}</td>
            <td>{p.get('namespace','')}</td>
            <td style="color:#d32f2f;font-weight:bold">{p.get('phase','')}</td>
            <td>{p.get('capacity','')}</td>
        </tr>"""

    # ── Pod rows ──
    pod_rows = ""
    if not pods:
        pod_rows = "<tr><td colspan='4' style='color:#388e3c'>No failing pods found</td></tr>"
    for p in pods:
        pod_rows += f"""
        <tr>
            <td>{p.get('pod','')}</td>
            <td>{p.get('namespace','')}</td>
            <td style="color:#d32f2f;font-weight:bold">{p.get('reason','')}</td>
            <td>{p.get('restart_count',0)}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 13px;
          color: #212121; margin: 0; padding: 20px; background: #f5f5f5; }}
  .container {{ max-width: 900px; margin: 0 auto; background: white;
                border-radius: 8px; overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .header {{ background: #1a237e; color: white; padding: 25px 30px; }}
  .header h1 {{ margin: 0; font-size: 22px; }}
  .header p {{ margin: 5px 0 0; opacity: 0.8; font-size: 13px; }}
  .status-banner {{ background: {overall_color}; color: white;
                    padding: 12px 30px; font-size: 16px; font-weight: bold; }}
  .content {{ padding: 25px 30px; }}
  .section {{ margin-bottom: 30px; }}
  .section h2 {{ font-size: 15px; color: #1a237e; border-bottom: 2px solid #e8eaf6;
                 padding-bottom: 8px; margin-bottom: 15px; }}
  .summary-box {{ background: #e8eaf6; border-left: 4px solid #1a237e;
                  padding: 15px; border-radius: 4px; line-height: 1.6; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ background: #1a237e; color: white; padding: 8px 10px; text-align: left; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #e0e0e0; }}
  tr:nth-child(even) {{ background: #f5f5f5; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;
                margin-bottom: 20px; }}
  .stat-card {{ background: #e8eaf6; border-radius: 6px; padding: 15px;
                text-align: center; }}
  .stat-card .num {{ font-size: 28px; font-weight: bold; color: #1a237e; }}
  .stat-card .label {{ font-size: 11px; color: #666; margin-top: 4px; }}
  .footer {{ background: #f5f5f5; padding: 15px 30px; font-size: 11px;
             color: #888; border-top: 1px solid #e0e0e0; }}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>🖥️ OCP Platform Health Check Report</h1>
    <p>Generated: {timestamp} | Cluster: ocp.eidikointernal.com</p>
  </div>

  <!-- Status Banner -->
  <div class="status-banner">
    Overall Status: {overall_text}
    &nbsp;|&nbsp; Failures: {len(failures)}
    &nbsp;|&nbsp; Warnings: {len(warnings)}
    &nbsp;|&nbsp; Critical: {len(critical)}
  </div>

  <div class="content">

    <!-- Stats -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="num">{len(nodes)}</div>
        <div class="label">Total Nodes</div>
      </div>
      <div class="stat-card">
        <div class="num">{len([n for n in nodes if n.get('ready')])}</div>
        <div class="label">Nodes Ready</div>
      </div>
      <div class="stat-card">
        <div class="num">{len(operators)}</div>
        <div class="label">Operators</div>
      </div>
      <div class="stat-card">
        <div class="num" style="color:{'#d32f2f' if degraded_ops else '#388e3c'}">{len(degraded_ops)}</div>
        <div class="label">Degraded Ops</div>
      </div>
    </div>

    <!-- Summary -->
    <div class="section">
      <h2>📋 AI Analysis Summary</h2>
      <div class="summary-box">{summary}</div>
    </div>

    <!-- Failures -->
    <div class="section">
      <h2>🚨 Failures & Remediation</h2>
      {failures_html}
    </div>

    <!-- Nodes -->
    <div class="section">
      <h2>🖥️ Node Status</h2>
      <table>
        <tr><th>Node</th><th>Role</th><th>Status</th><th>Issues</th></tr>
        {node_rows}
      </table>
    </div>

    <!-- Operators -->
    <div class="section">
      <h2>⚙️ Cluster Operators ({len(operators)})</h2>
      <table>
        <tr><th>Operator</th><th>Available</th><th>Degraded</th><th>Message</th></tr>
        {op_rows}
      </table>
    </div>

    <!-- MCP -->
    <div class="section">
      <h2>🔧 MachineConfigPools</h2>
      <table>
        <tr><th>Pool</th><th>Total</th><th>Ready</th><th>Degraded</th></tr>
        {mcp_rows}
      </table>
    </div>

    <!-- etcd -->
    <div class="section">
      <h2>🗄️ etcd Health</h2>
      <div style="background:#f5f5f5;padding:12px;border-radius:4px">
        Status: <strong style="color:{etcd_color}">{etcd_text}</strong>
      </div>
    </div>

    <!-- PVCs -->
    <div class="section">
      <h2>💾 PVC Issues</h2>
      <table>
        <tr><th>Name</th><th>Namespace</th><th>Phase</th><th>Capacity</th></tr>
        {pvc_rows}
      </table>
    </div>

    <!-- Failing Pods -->
    <div class="section">
      <h2>🐛 Failing Pods</h2>
      <table>
        <tr><th>Pod</th><th>Namespace</th><th>Reason</th><th>Restarts</th></tr>
        {pod_rows}
      </table>
    </div>

  </div>

  <!-- Footer -->
  <div class="footer">
    Auto-generated by OCP AI Monitoring Agent &nbsp;|&nbsp;
    Powered by LangGraph + LangChain + Groq LLaMA &nbsp;|&nbsp;
    Eidiko Systems
  </div>

</div>
</body>
</html>"""

    return html