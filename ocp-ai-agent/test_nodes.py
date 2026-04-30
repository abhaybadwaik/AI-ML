from nodes import (
    collect_nodes_node,
    collect_operators_node,
    aggregate_node
)

# Simulate empty state
state = {
    "nodes": [], "operators": [], "mcpools": [],
    "etcd": {}, "pvcs": [], "pods": [], "certs": [],
    "collection_errors": []
}

# Test node 1
state.update(collect_nodes_node(state))
print(f"\nNodes collected: {len(state['nodes'])}")

# Test node 2
state.update(collect_operators_node(state))
print(f"Operators collected: {len(state['operators'])}")

# Test aggregate
state.update(aggregate_node(state))
print(f"Collected at: {state['collected_at']}")
print(f"Errors: {state['collection_errors']}")
print("\nNodes.py working!")