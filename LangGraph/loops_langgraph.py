# from langgraph.graph import StateGraph

# # Step 1 → Ask user
# def ask(state):
#     answer = input("Are you satisfied? (yes/no): ")
#     state["answer"] = answer
#     return state

# # Step 2 → Decide
# def check(state):
#     if state["answer"] == "yes":
#         return "end"
#     else:
#         return "ask"

# # Build graph
# builder = StateGraph(dict)

# builder.add_node("ask", ask)
# builder.add_node("end", lambda state: state)

# builder.set_entry_point("ask")

# # Loop logic
# builder.add_conditional_edges(
#     "ask",
#     check,
#     {
#         "ask": "ask",   # loop 🔁
#         "end": "end"    # exit 🚪
#     }
# )

# graph = builder.compile()

# # Run
# graph.invoke({})



# Example Password👇🏾👇🏾👇🏾👇🏾

from langgraph.graph import StateGraph

# Step 1 → Ask password
def ask_password(state):
    pwd = input("Enter password: ")
    state["pwd"] = pwd
    return state

# Step 2 → Check password
def check_password(state):
    if state["pwd"] == "1234":
        return "success"
    else:
        return "retry"

# Success node
def success(state):
    print("Login Successful ✅")
    return state

# Retry node
def retry(state):
    print("Wrong password ❌ Try again")
    return state

# Build graph
builder = StateGraph(dict)

builder.add_node("ask", ask_password)
builder.add_node("success", success)
builder.add_node("retry", retry)

builder.set_entry_point("ask")

# Loop logic
builder.add_conditional_edges(
    "ask",
    check_password,
    {
        "success": "success",
        "retry": "retry"
    }
)

# Loop back from retry → ask again
builder.add_edge("retry", "ask")

graph = builder.compile()

# Run
graph.invoke({})