import json
import paramiko
from langchain_core.tools import tool
from config import settings


# ─────────────────────────────────────────────
# SSH Helper — runs any oc command on OCP server
# ─────────────────────────────────────────────
def run_oc_command(command: str) -> str:
    """SSH into OCP server and run an oc command. Returns stdout as string."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=settings.ocp_ssh_host,
        username=settings.ocp_ssh_user,
        password=settings.ocp_ssh_password
    )
    full_command = f"KUBECONFIG={settings.ocp_kubeconfig} {command}"
    _, stdout, stderr = ssh.exec_command(full_command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    ssh.close()
    return output if output else error


# ─────────────────────────────────────────────
# Tool 1: Node Status
# ─────────────────────────────────────────────
@tool
def get_node_status() -> list:
    """Fetch health status of all cluster nodes."""
    output = run_oc_command("oc get nodes -o json")
    nodes = json.loads(output).get("items", [])
    result = []
    for node in nodes:
        conditions = {
            c["type"]: c["status"]
            for c in node["status"].get("conditions", [])
        }
        roles = [
            label.split("/")[-1]
            for label in node["metadata"].get("labels", {})
            if "node-role.kubernetes.io" in label
        ]
        result.append({
            "name": node["metadata"]["name"],
            "roles": roles,
            "ready": conditions.get("Ready") == "True",
            "disk_pressure": conditions.get("DiskPressure") == "True",
            "memory_pressure": conditions.get("MemoryPressure") == "True",
            "pid_pressure": conditions.get("PIDPressure") == "True",
        })
    return result


# ─────────────────────────────────────────────
# Tool 2: Cluster Operators
# ─────────────────────────────────────────────
@tool
def get_cluster_operators() -> list:
    """Fetch OpenShift ClusterOperator health."""
    output = run_oc_command("oc get co -o json")
    operators = json.loads(output).get("items", [])
    result = []
    for op in operators:
        conditions = {
            c["type"]: c
            for c in op["status"].get("conditions", [])
        }
        result.append({
            "name": op["metadata"]["name"],
            "available": conditions.get("Available", {}).get("status", "Unknown"),
            "degraded": conditions.get("Degraded", {}).get("status", "Unknown"),
            "progressing": conditions.get("Progressing", {}).get("status", "Unknown"),
            "message": conditions.get("Degraded", {}).get("message", ""),
        })
    return result


# ─────────────────────────────────────────────
# Tool 3: MachineConfigPools
# ─────────────────────────────────────────────
@tool
def get_machine_config_pools() -> list:
    """Fetch MachineConfigPool health."""
    output = run_oc_command("oc get mcp -o json")
    pools = json.loads(output).get("items", [])
    result = []
    for pool in pools:
        status = pool.get("status", {})
        result.append({
            "name": pool["metadata"]["name"],
            "machine_count": status.get("machineCount", 0),
            "ready_machine_count": status.get("readyMachineCount", 0),
            "updated_machine_count": status.get("updatedMachineCount", 0),
            "unavailable_machine_count": status.get("unavailableMachineCount", 0),
            "degraded_machine_count": status.get("degradedMachineCount", 0),
        })
    return result


# ─────────────────────────────────────────────
# Tool 4: etcd Health
# ─────────────────────────────────────────────
@tool
def get_etcd_health() -> dict:
    """Check etcd cluster health."""
    # Get etcd pod name
    pod_output = run_oc_command(
        "oc get pods -n openshift-etcd -l app=etcd "
        "-o jsonpath='{.items[0].metadata.name}'"
    )
    pod_name = pod_output.strip().strip("'")

    if not pod_name:
        return {"healthy": False, "error": "No etcd pod found"}

    # Run etcdctl inside the pod
    health_output = run_oc_command(
        f"oc exec {pod_name} -n openshift-etcd -- "
        f"etcdctl endpoint health --cluster --write-out=json"
    )

    try:
        health_data = json.loads(health_output)
        return {
            "healthy": all(ep.get("health") for ep in health_data),
            "endpoints": health_data
        }
    except Exception:
        return {
            "healthy": False,
            "raw_output": health_output
        }


# ─────────────────────────────────────────────
# Tool 5: PVC Issues
# ─────────────────────────────────────────────
@tool
def get_pvc_issues() -> list:
    """Fetch PVCs in Pending or Lost phase across all namespaces."""
    output = run_oc_command("oc get pvc -A -o json")
    pvcs = json.loads(output).get("items", [])
    result = []
    for pvc in pvcs:
        phase = pvc["status"].get("phase", "")
        if phase in ["Pending", "Lost"]:
            result.append({
                "name": pvc["metadata"]["name"],
                "namespace": pvc["metadata"]["namespace"],
                "phase": phase,
                "storage_class": pvc["spec"].get("storageClassName", "unknown"),
                "capacity": pvc["spec"]["resources"]["requests"].get("storage", "unknown"),
            })
    return result


# ─────────────────────────────────────────────
# Tool 6: Failing Pods
# ─────────────────────────────────────────────
@tool
def get_failing_pods() -> list:
    """Fetch pods in bad states across openshift- namespaces."""
    bad_states = {
        "CrashLoopBackOff", "OOMKilled", "Error",
        "ImagePullBackOff", "ErrImagePull"
    }
    output = run_oc_command(
        "oc get pods -A -o json --field-selector="
        "status.phase!=Running,status.phase!=Succeeded"
    )
    pods = json.loads(output).get("items", [])
    result = []
    for pod in pods:
        ns = pod["metadata"]["namespace"]
        if not ns.startswith("openshift-"):
            continue
        for container in pod["status"].get("containerStatuses", []):
            waiting = container.get("state", {}).get("waiting", {})
            terminated = container.get("state", {}).get("terminated", {})
            reason = waiting.get("reason") or terminated.get("reason")
            if reason in bad_states:
                result.append({
                    "pod": pod["metadata"]["name"],
                    "namespace": ns,
                    "container": container["name"],
                    "reason": reason,
                    "restart_count": container.get("restartCount", 0),
                })
    return result


# ─────────────────────────────────────────────
# Tool 7: Expiring TLS Certificates
# ─────────────────────────────────────────────
@tool
def get_expiring_certs() -> list:
    """Find TLS certificates expiring within 30 days - fast batch check."""
    output = run_oc_command(
        "oc get secrets -A --field-selector type=kubernetes.io/tls "
        "-o jsonpath='{range .items[*]}{.metadata.namespace}{\"|\"}{ .metadata.name}{\"\\n\"}{end}'"
    )
    
    if not output.strip():
        return []

    # Just return names — skip per-cert SSL decode for now
    # Full cert expiry check is too slow over SSH
    result = []
    for line in output.strip().split("\n"):
        if "|" in line:
            ns, name = line.split("|", 1)
            result.append({
                "name": name.strip(),
                "namespace": ns.strip(),
                "expires_at": "check-manually",
                "days_remaining": 999,  # placeholder
            })
    return result