from tools import get_node_status, get_cluster_operators

print("Testing node status...")
nodes = get_node_status.invoke({})
for n in nodes:
    print(f"  {n['name']} | Ready: {n['ready']} | Roles: {n['roles']}")

print("\nTesting cluster operators...")
ops = get_cluster_operators.invoke({})
for op in ops[:3]:
    print(f"  {op['name']} | Available: {op['available']} | Degraded: {op['degraded']}")