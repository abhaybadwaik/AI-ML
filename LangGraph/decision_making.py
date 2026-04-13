from langgraph.graph import StateGraph

# Router logic (only decides path)
def router_logic(state):
    if "hello" in state["input"]:
        return "greet"
    elif "bye" in state["input"]:
        return "exit"
    else:
        return "other"

# Nodes
def greet(state):
    state["msg"] = "Hello 👋"
    return state

def other(state):
    state["msg"] = "I don't understand 🤔"
    return state

def exit_node(state):
    state["msg"] = "Goodbye 👋"
    return state

# Build graph
builder = StateGraph(dict)

# Dummy router node (just passes state)
builder.add_node("router", lambda state: state)
builder.add_node("greet", greet)
builder.add_node("other", other)
builder.add_node("exit", exit_node)

# Entry point
builder.set_entry_point("router")

# Conditional routing
builder.add_conditional_edges(
    "router",
    router_logic,
    {
        "greet": "greet",
        "other": "other",
        "exit": "exit"
    }
)

# Compile
graph = builder.compile()

# Run
while True:
    user_input = input("You: ")

    if user_input.lower() == "stop":
        break

    result = graph.invoke({"input": user_input})

    print("AI:", result["msg"])