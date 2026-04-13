from langgraph.graph import StateGraph

# Step 1
def step1(state):
    state["msg"] += " Hello"
    return state

# Step 2
def step2(state):
    state["msg"] += " World"
    return state

# Create graph
builder = StateGraph(dict)

builder.add_node("step1", step1)
builder.add_node("step2", step2)

builder.set_entry_point("step1")
builder.add_edge("step1", "step2")

graph = builder.compile()

result = graph.invoke({"msg": ""})

print(result)