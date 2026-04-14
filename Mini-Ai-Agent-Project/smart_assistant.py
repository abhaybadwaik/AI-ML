# 👉 Smart Assistant 🤖 that can:

# Understand user input
# Decide what to do
# Respond accordingly
# Repeat (loop)
# 🎯 Features

# ✅ Decision making
# ✅ Loop (continuous interaction)
# ✅ Multiple actions
# ✅ Real workflow



from langgraph.graph import StateGraph

# Step 1 → Router (brain of agent)
def router(state):
    text = state["input"].lower()

    if "hello" in text:
        return "greet"
    elif "joke" in text:
        return "joke"
    elif "bye" in text:
        return "exit"
    elif "2+2" in text:
        return "calculator"
    else:
        return "unknown"

# Step 2 → Actions

def greet(state):
    state["msg"] = "Hello! How can I help you? 😊"
    return state

def joke(state):
    state["msg"] = "Why did the programmer quit? Because he didn't get arrays 😂"
    return state

def unknown(state):
    state["msg"] = "Sorry, I didn't understand 🤔"
    return state

def exit_node(state):
    state["msg"] = "Goodbye 👋"
    return state

def calculator(state):
    state["msg"] = "2 + 2 = 4"
    return state

# Build graph
builder = StateGraph(dict)

# Nodes
builder.add_node("router", lambda state: state)
builder.add_node("greet", greet)
builder.add_node("joke", joke)
builder.add_node("unknown", unknown)
builder.add_node("exit", exit_node)
builder.add_node("calculator", calculator)

# Entry
builder.set_entry_point("router")

# Decision logic
builder.add_conditional_edges(
    "router",
    router,
    {
        "greet": "greet",
        "joke": "joke",
        "unknown": "unknown",
        "calculator": "calculator",
        "exit": "exit"
    }
)

# Compile graph
graph = builder.compile()

# Loop (agent keeps running)
while True:
    user_input = input("You: ")

    result = graph.invoke({"input": user_input})

    print("AI:", result["msg"])

    if user_input.lower() == "bye":
        break