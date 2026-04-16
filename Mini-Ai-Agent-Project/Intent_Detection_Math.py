import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq

# 🔑 Load API key from .env
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# 🧠 AI Router (INTELLIGENT)
def router(state):
    question = state["input"]

    response = llm.invoke(
        f"""
        Classify the user input into one word only:
        - math
        - chat

        Input: {question}
        """
    )

    decision = response.content.lower()

    if "math" in decision:
        return "calculator"
    else:
        return "chat"

# 🔧 Calculator Tool (clean input)
def calculator(state):
    try:
        text = state["input"]

        allowed_chars = "0123456789+-*/.()"
        expression = ""

        for char in text:
            if char in allowed_chars:
                expression += char

        if not expression:
            state["msg"] = "No math found ❌"
            return state

        result = eval(expression)
        state["msg"] = f"Answer: {result}"

    except:
        state["msg"] = "Invalid math ❌"

    return state

# 🤖 Chat with Memory
def chat(state):
    history = state.get("history", [])

    history.append(("user", state["input"]))

    response = llm.invoke(history)

    history.append(("ai", response.content))

    state["history"] = history
    state["msg"] = response.content

    return state

# 🔧 Build Graph
builder = StateGraph(dict)

builder.add_node("router", lambda state: state)
builder.add_node("calculator", calculator)
builder.add_node("chat", chat)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    router,
    {
        "calculator": "calculator",
        "chat": "chat"
    }
)

graph = builder.compile()

# 🔁 Run Assistant
state = {"history": []}

print("🤖 Smart AI Assistant Started (type 'bye' to exit)")

while True:
    user_input = input("You: ")

    if user_input.lower() == "bye":
        print("AI: Goodbye 👋")
        break

    state["input"] = user_input

    result = graph.invoke(state)

    print("AI:", result["msg"])