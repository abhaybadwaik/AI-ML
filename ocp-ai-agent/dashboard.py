from flask import Flask, jsonify, render_template_string
from datetime import datetime, timezone
from threading import Thread

app = Flask(__name__)

# ─────────────────────────────────────────────
# In-memory store
# ─────────────────────────────────────────────
latest_result = {
    "timestamp": None,
    "nodes": [],
    "operators": [],
    "mcpools": [],
    "etcd": {},
    "pvcs": [],
    "pods": [],
    "failures": [],
    "resolutions": [],
    "summary": "Waiting for first monitoring cycle...",
    "email_sent": False,
    "collection_errors": []
}

cycle_history = []

DASHBOARD_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>OCP Health Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, sans-serif; font-size: 13px;
         background: #f0f2f5; color: #212121; }
  .topbar { background: #1a237e; color: white; padding: 14px 24px;
            display: flex; justify-content: space-between; align-items: center; }
  .topbar h1 { font-size: 18px; font-weight: 600; }
  .topbar p { font-size: 12px; opacity: 0.8; margin-top: 2px; }
  .status-pill { padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; }
  .healthy { background: #e8f5e9; color: #2e7d32; }
  .warning { background: #fff8e1; color: #f57f17; }
  .critical { background: #ffebee; color: #c62828; }
  .content { padding: 20px 24px; max-width: 1200px; margin: 0 auto; }
  .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr);
               gap: 12px; margin-bottom: 20px; }
  .stat-card { background: white; border-radius: 8px; padding: 16px;
               box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .stat-card .num { font-size: 32px; font-weight: 700; color: #1a237e; }
  .stat-card .label { font-size: 12px; color: #888; margin-top: 4px; }
  .grid-2 { display: grid; grid-template-columns: 1.5fr 1fr;
             gap: 12px; margin-bottom: 20px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr);
             gap: 12px; margin-bottom: 20px; }
  .card { background: white; border-radius: 8px; padding: 16px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .card h2 { font-size: 14px; font-weight: 600; color: #1a237e;
             margin-bottom: 12px; border-bottom: 1px solid #e8eaf6;
             padding-bottom: 8px; }
  .node-row { display: flex; justify-content: space-between; align-items: center;
              padding: 8px 10px; border-radius: 4px; margin-bottom: 4px;
              background: #f5f5f5; cursor: pointer; transition: background 0.2s; }
  .node-row:hover { background: #e8eaf6; }
  .node-name { font-size: 12px; font-weight: 500; }
  .node-role { font-size: 11px; color: #888; }
  .badge { padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
  .badge-green { background: #e8f5e9; color: #2e7d32; }
  .badge-red { background: #ffebee; color: #c62828; }
  .badge-orange { background: #fff8e1; color: #f57f17; }
  .badge-blue { background: #e8eaf6; color: #1a237e; }
  .alert-box { padding: 10px 12px; border-radius: 6px; margin-bottom: 8px;
               border-left: 4px solid; cursor: pointer; transition: opacity 0.2s; }
  .alert-box:hover { opacity: 0.85; }
  .alert-warning { background: #fff8e1; border-color: #f57f17; }
  .alert-critical { background: #ffebee; border-color: #c62828; }
  .alert-info { background: #e8eaf6; border-color: #1a237e; }
  .alert-title { font-size: 12px; font-weight: 600; margin-bottom: 4px; }
  .alert-msg { font-size: 12px; color: #555; }
  .summary-box { background: #e8eaf6; border-left: 4px solid #1a237e;
                 padding: 14px; border-radius: 4px; font-size: 13px; line-height: 1.7; }
  .history-row { display: flex; align-items: center; gap: 12px; padding: 6px 8px;
                 border-radius: 4px; background: #f5f5f5; margin-bottom: 4px; }
  .history-time { font-size: 12px; color: #888; min-width: 60px; }
  .stat-value { font-size: 22px; font-weight: 700; }
  .green { color: #2e7d32; }
  .red { color: #c62828; }
  .footer { text-align: center; padding: 16px; font-size: 11px;
            color: #aaa; margin-top: 8px; }
  .toolbar { display: flex; justify-content: space-between;
             align-items: center; margin-bottom: 12px; }
  .filter-btn { padding: 5px 12px; border-radius: 20px; font-size: 12px;
                cursor: pointer; border: 1px solid #ccc; background: white;
                transition: all 0.2s; margin-left: 6px; }
  .filter-btn.active { background: #1a237e; color: white; border-color: #1a237e; }
  .trigger-btn { padding: 8px 18px; background: #1a237e; color: white;
                 border: none; border-radius: 6px; font-size: 13px;
                 cursor: pointer; font-weight: 600; transition: background 0.2s; }
  .trigger-btn:hover { background: #283593; }
  .trigger-btn:disabled { background: #9fa8da; cursor: not-allowed; }
  .op-row { display: flex; justify-content: space-between; align-items: center;
            padding: 6px 8px; border-radius: 4px; margin-bottom: 3px;
            background: #f5f5f5; }
  .op-name { font-size: 12px; }
  .modal-overlay { display: none; position: fixed; top: 0; left: 0;
                   width: 100%; height: 100%; background: rgba(0,0,0,0.5);
                   z-index: 1000; justify-content: center; align-items: center; }
  .modal-overlay.open { display: flex; }
  .modal { background: white; border-radius: 10px; padding: 24px;
           max-width: 560px; width: 90%; max-height: 80vh;
           overflow-y: auto; position: relative; }
  .modal h3 { font-size: 16px; font-weight: 600; color: #1a237e; margin-bottom: 16px; }
  .modal-close { position: absolute; top: 14px; right: 16px; cursor: pointer;
                 font-size: 20px; color: #888; background: none; border: none; }
  .modal-section { margin-bottom: 14px; }
  .modal-section label { font-size: 12px; color: #888; display: block; margin-bottom: 4px; }
  .modal-section p { font-size: 13px; color: #212121; line-height: 1.6; }
  .cmd-block { background: #263238; color: #80cbc4; padding: 8px 12px;
               border-radius: 4px; font-family: monospace; font-size: 12px; margin: 3px 0; }
  .step-list { padding-left: 18px; font-size: 13px; line-height: 1.8; }
  .toast { position: fixed; bottom: 24px; right: 24px; background: #1a237e;
           color: white; padding: 12px 20px; border-radius: 8px; font-size: 13px;
           z-index: 2000; display: none; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
</style>
</head>
<body>

<div class="topbar">
  <div>
    <h1>🖥️ OCP Cluster Health Dashboard</h1>
    <p>ocp.eidikointernal.com — Live monitoring</p>
  </div>
  <div style="text-align: right;">
    <div class="status-pill {{ status_class }}">{{ overall_status }}</div>
    <p style="font-size: 11px; opacity: 0.7; margin-top: 6px;">
      Last cycle: {{ timestamp }}
    </p>
  </div>
</div>

<div class="content">

  <!-- Toolbar -->
  <div class="toolbar">
    <p style="font-size: 12px; color: #888;">Auto-refreshes every 60s</p>
    <button class="trigger-btn" onclick="triggerCycle(this)">
      ▶ Run Monitoring Cycle Now
    </button>
  </div>

  <!-- Stats -->
  <div class="stat-grid">
    <div class="stat-card">
      <div class="num">{{ total_nodes }}</div>
      <div class="label">Total Nodes</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:#2e7d32">{{ ready_nodes }}</div>
      <div class="label">Nodes Ready</div>
    </div>
    <div class="stat-card">
      <div class="num">{{ total_operators }}</div>
      <div class="label">Operators</div>
    </div>
    <div class="stat-card">
      <div class="num" style="color:{{ '#c62828' if total_failures > 0 else '#2e7d32' }}">
        {{ total_failures }}
      </div>
      <div class="label">Active Alerts</div>
    </div>
  </div>

  <!-- Nodes + Alerts -->
  <div class="grid-2">
    <div class="card">
      <h2>🖥️ Node Status
        <span style="font-size:11px;color:#888;font-weight:400">(click for details)</span>
      </h2>
      {% for node in nodes %}
      <div class="node-row" onclick="showNodeModal({{ loop.index0 }})">
        <div>
          <div class="node-name">{{ node.name.split('.')[0] }}</div>
          <div class="node-role">{{ node.roles | join(', ') }}</div>
        </div>
        <span class="badge {{ 'badge-green' if node.ready else 'badge-red' }}">
          {{ 'Ready' if node.ready else 'Not Ready' }}
        </span>
      </div>
      {% endfor %}
    </div>

    <div class="card">
      <h2>🚨 Active Alerts
        <span style="font-size:11px;color:#888;font-weight:400">(click for remediation)</span>
      </h2>
      {% if failures %}
        {% for f in failures %}
        <div class="alert-box alert-{{ f.severity | lower }}"
             onclick="showAlertModal({{ loop.index0 }})">
          <div class="alert-title">[{{ f.severity }}] {{ f.component }}</div>
          <div class="alert-msg">{{ f.message }}</div>
          <div style="font-size:11px;color:#888;margin-top:4px;">
            Click to see remediation →
          </div>
        </div>
        {% endfor %}
      {% else %}
        <div style="color:#2e7d32;font-size:13px;padding:8px;">
          ✅ No active alerts
        </div>
      {% endif %}
    </div>
  </div>

  <!-- Operators with filter -->
  <div class="card" style="margin-bottom:20px;">
    <div style="display:flex;justify-content:space-between;
                align-items:center;margin-bottom:12px;">
      <h2 style="margin:0;border:none;padding:0;">
        ⚙️ Cluster Operators ({{ total_operators }})
      </h2>
      <div>
        <button class="filter-btn active" onclick="filterOps('all', this)">All</button>
        <button class="filter-btn" onclick="filterOps('degraded', this)">Degraded</button>
        <button class="filter-btn" onclick="filterOps('available', this)">Available</button>
      </div>
    </div>
    <div id="ops-list">
      {% for op in operators %}
      <div class="op-row"
           data-degraded="{{ op.degraded }}"
           data-available="{{ op.available }}">
        <span class="op-name">{{ op.name }}</span>
        <div style="display:flex;gap:6px;">
          <span class="badge {{ 'badge-green' if op.available == 'True' else 'badge-red' }}">
            {{ 'Available' if op.available == 'True' else 'Unavailable' }}
          </span>
          <span class="badge {{ 'badge-red' if op.degraded == 'True' else 'badge-green' }}">
            {{ 'Degraded' if op.degraded == 'True' else 'OK' }}
          </span>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- etcd + PVC + Pods -->
  <div class="grid-3">
    <div class="card">
      <h2>🗄️ etcd Health</h2>
      <div class="stat-value {{ 'green' if etcd_healthy else 'red' }}">
        {{ '✓ Healthy' if etcd_healthy else '✗ Unhealthy' }}
      </div>
    </div>
    <div class="card">
      <h2>💾 PVC Issues</h2>
      <div class="stat-value {{ 'green' if pvc_count == 0 else 'red' }}">
        {{ '✓ None' if pvc_count == 0 else '✗ ' + pvc_count|string + ' issues' }}
      </div>
    </div>
    <div class="card">
      <h2>🐛 Failing Pods</h2>
      <div class="stat-value {{ 'green' if pod_count == 0 else 'red' }}">
        {{ '✓ None' if pod_count == 0 else '✗ ' + pod_count|string + ' pods' }}
      </div>
    </div>
  </div>

  <!-- AI Summary -->
  <div class="card" style="margin-bottom:20px;">
    <h2>🤖 AI Analysis Summary</h2>
    <div class="summary-box">{{ summary }}</div>
  </div>

  <!-- Cycle History -->
  <div class="card" style="margin-bottom:20px;">
    <h2>📈 Cycle History (last 10)</h2>
    {% if history %}
      {% for h in history %}
      <div class="history-row">
        <span class="history-time">{{ h.time }}</span>
        <span class="badge
          {{ 'badge-green' if h.status == 'HEALTHY'
             else 'badge-orange' if h.status == 'WARNING'
             else 'badge-red' }}">
          {{ h.status }}
        </span>
        <span style="font-size:12px;color:#666;">
          {{ h.failures }} failure(s) | {{ h.nodes }} nodes
        </span>
        <span style="font-size:11px;color:#aaa;margin-left:auto;">
          {{ '✅ Email sent' if h.email_sent else '❌ Email failed' }}
        </span>
      </div>
      {% endfor %}
    {% else %}
      <p style="color:#888;font-size:13px;">No cycles completed yet.</p>
    {% endif %}
  </div>

</div>

<div class="footer">
  OCP AI Monitoring Agent — LangGraph + LangChain + LlamaIndex + Groq
</div>

<!-- Node Modal -->
<div class="modal-overlay" id="node-modal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('node-modal')">✕</button>
    <h3 id="node-modal-title">Node Details</h3>
    <div class="modal-section">
      <label>Full Name</label>
      <p id="node-modal-name">—</p>
    </div>
    <div class="modal-section">
      <label>Roles</label>
      <p id="node-modal-roles">—</p>
    </div>
    <div class="modal-section">
      <label>Status</label>
      <p id="node-modal-status">—</p>
    </div>
    <div class="modal-section">
      <label>Disk Pressure</label>
      <p id="node-modal-disk">—</p>
    </div>
    <div class="modal-section">
      <label>Memory Pressure</label>
      <p id="node-modal-memory">—</p>
    </div>
    <div class="modal-section">
      <label>PID Pressure</label>
      <p id="node-modal-pid">—</p>
    </div>
    <div class="modal-section">
      <label>Quick Commands</label>
      <div class="cmd-block">oc describe node <span id="node-modal-cmd"></span></div>
      <div class="cmd-block">oc adm top node <span id="node-modal-cmd2"></span></div>
    </div>
  </div>
</div>

<!-- Alert Modal -->
<div class="modal-overlay" id="alert-modal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('alert-modal')">✕</button>
    <h3 id="alert-modal-title">Alert Details</h3>
    <div class="modal-section">
      <label>Issue</label>
      <p id="alert-modal-msg">—</p>
    </div>
    <div class="modal-section">
      <label>Root Cause</label>
      <p id="alert-modal-root">—</p>
    </div>
    <div class="modal-section">
      <label>Remediation Steps</label>
      <ol class="step-list" id="alert-modal-steps"></ol>
    </div>
    <div class="modal-section">
      <label>Commands to Run</label>
      <div id="alert-modal-cmds"></div>
    </div>
    <div class="modal-section">
      <label>Documentation</label>
      <p id="alert-modal-docs">—</p>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
const nodes = {{ nodes | tojson }};
const failures = {{ failures | tojson }};
const resolutions = {{ resolutions | tojson }};

function showNodeModal(idx) {
  const n = nodes[idx];
  document.getElementById('node-modal-title').textContent = n.name;
  document.getElementById('node-modal-name').textContent = n.name;
  document.getElementById('node-modal-roles').textContent = n.roles.join(', ');
  document.getElementById('node-modal-status').textContent = n.ready ? '✅ Ready' : '❌ Not Ready';
  document.getElementById('node-modal-disk').textContent = n.disk_pressure ? '⚠ Yes' : '✓ No';
  document.getElementById('node-modal-memory').textContent = n.memory_pressure ? '⚠ Yes' : '✓ No';
  document.getElementById('node-modal-pid').textContent = n.pid_pressure ? '⚠ Yes' : '✓ No';
  document.getElementById('node-modal-cmd').textContent = n.name;
  document.getElementById('node-modal-cmd2').textContent = n.name;
  document.getElementById('node-modal').classList.add('open');
}

function showAlertModal(idx) {
  const f = failures[idx];
  const res = resolutions[idx] || {};
  document.getElementById('alert-modal-title').textContent =
    '[' + f.severity + '] ' + f.component;
  document.getElementById('alert-modal-msg').textContent = f.message;
  document.getElementById('alert-modal-root').textContent =
    res.root_cause || 'Analyzing...';
  const steps = res.steps || [];
  document.getElementById('alert-modal-steps').innerHTML =
    steps.map(s => '<li>' + s + '</li>').join('');
  const cmds = res.commands || [];
  document.getElementById('alert-modal-cmds').innerHTML =
    cmds.map(c => '<div class="cmd-block">' + c + '</div>').join('');
  const docs = res.docs_ref || '';
  document.getElementById('alert-modal-docs').innerHTML =
    docs ? '<a href="' + docs + '" target="_blank">' + docs + '</a>' : 'N/A';
  document.getElementById('alert-modal').classList.add('open');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function filterOps(filter, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.op-row').forEach(row => {
    if (filter === 'all') {
      row.style.display = 'flex';
    } else if (filter === 'degraded') {
      row.style.display = row.dataset.degraded === 'True' ? 'flex' : 'none';
    } else if (filter === 'available') {
      row.style.display = row.dataset.available === 'True' ? 'flex' : 'none';
    }
  });
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 3000);
}

function triggerCycle(btn) {
  btn.disabled = true;
  btn.textContent = '⏳ Running...';
  showToast('Monitoring cycle triggered!');
  fetch('/trigger', {method: 'POST'})
    .then(r => r.json())
    .then(d => {
      showToast(d.message);
      setTimeout(() => location.reload(), 30000);
    })
    .catch(() => showToast('Cycle triggered — refreshing soon...'))
    .finally(() => {
      setTimeout(() => {
        btn.disabled = false;
        btn.textContent = '▶ Run Monitoring Cycle Now';
      }, 35000);
    });
}

document.querySelectorAll('.modal-overlay').forEach(el => {
  el.addEventListener('click', function(e) {
    if (e.target === this) this.classList.remove('open');
  });
});
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.route("/")
def dashboard():
    data = latest_result
    failures = data.get("failures", [])
    critical = [f for f in failures if f.get("severity") == "CRITICAL"]
    warnings = [f for f in failures if f.get("severity") == "WARNING"]

    if critical:
        overall_status = "🔴 CRITICAL"
        status_class = "critical"
    elif warnings:
        overall_status = "🟡 WARNING"
        status_class = "warning"
    else:
        overall_status = "🟢 HEALTHY"
        status_class = "healthy"

    nodes = data.get("nodes", [])

    return render_template_string(
        DASHBOARD_HTML,
        overall_status=overall_status,
        status_class=status_class,
        timestamp=data.get("timestamp") or "Not yet run",
        total_nodes=len(nodes),
        ready_nodes=len([n for n in nodes if n.get("ready")]),
        total_operators=len(data.get("operators", [])),
        total_failures=len(failures),
        nodes=nodes,
        operators=data.get("operators", []),
        failures=failures,
        resolutions=data.get("resolutions", []),
        etcd_healthy=data.get("etcd", {}).get("healthy", False),
        pvc_count=len(data.get("pvcs", [])),
        pod_count=len(data.get("pods", [])),
        summary=data.get("summary", "No data yet."),
        history=list(reversed(cycle_history[-10:])),
    )


@app.route("/api/status")
def api_status():
    return jsonify(latest_result)


@app.route("/trigger", methods=["POST"])
def trigger_cycle():
    from scheduler import run_monitoring_cycle
    thread = Thread(target=run_monitoring_cycle, daemon=True)
    thread.start()
    return jsonify({"message": "Cycle started! Refresh in ~30 seconds."})


# ─────────────────────────────────────────────
# Called by scheduler after every cycle
# ─────────────────────────────────────────────
def update_dashboard(result: dict):
    global latest_result
    latest_result = result

    failures = result.get("failures", [])
    critical = any(f.get("severity") == "CRITICAL" for f in failures)
    warnings = any(f.get("severity") == "WARNING" for f in failures)
    status = "CRITICAL" if critical else "WARNING" if warnings else "HEALTHY"

    cycle_history.append({
        "time": datetime.now().strftime("%H:%M"),
        "status": status,
        "failures": len(failures),
        "nodes": len(result.get("nodes", [])),
        "email_sent": result.get("email_sent", False),
    })

    if len(cycle_history) > 10:
        cycle_history.pop(0)

    print(f"  [Dashboard] Updated — status: {status}")


def run_dashboard():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)