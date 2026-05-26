"""
Phase 4 · Lesson 2 — ReAct Agent Pattern
Reasoning + Acting loop for multi-step problem solving

WHAT WE ARE TRYING TO ACHIEVE:
Lesson 1 → LLM calls tools but no reasoning loop
ReAct    → LLM thinks, acts, observes, thinks again until it has final answer

Thought → Action → Observation → Thought → Action → ... → Final Answer
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=500)


# ── Tools ─────────────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city. Returns temperature in celsius as a number."""
    data = {
        "Mumbai": "Temperature: 28, Condition: Humid Partly Cloudy",
        "Delhi": "Temperature: 35, Condition: Hot Clear Sky",
        "Pune": "Temperature: 26, Condition: Pleasant Light Breeze",
    }
    return data.get(city, f"No data for {city}")


@tool
def calculate(expression: str) -> str:
    """Perform mathematical calculations. Example: '28 * 9/5 + 32' or '83 / 50'
    Pass ONLY the math expression as a plain string. No curly braces."""
    try:
        # clean up any curly braces LLM might add
        expression = expression.strip().strip("{}")
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def get_upi_stats(metric: str) -> str:
    """Get UPI statistics. Returns numeric values where possible."""
    stats = {
        "growth": "UPI grew from 92 crore in 2018 to 17221 crore in 2024",
        "market_share": "Market share: 83 percent",
        "users": "India processes 48.5 percent of global real-time payments",
        "value": "Total value: Rs 246.83 lakh crore in 2024",
    }
    return stats.get(metric, "Metric not found")


tools = [get_weather, calculate, get_upi_stats]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


# ── ReAct Loop ────────────────────────────────────────────────
def react_agent(question: str, max_steps: int = 5) -> str:
    """
    ReAct loop:
    1. LLM thinks and decides action
    2. We execute the tool
    3. We pass result back to LLM
    4. LLM thinks again
    5. Repeat until LLM gives final answer (no more tool calls)
    """

    print(f"\nQuestion: {question}")
    print("="*50)

    # conversation history — grows with each step
    messages = [HumanMessage(content=question)]
    step = 0

    while step < max_steps:
        step += 1
        print(f"\n[Step {step}]")

        # LLM thinks and decides
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # if no tool calls — LLM has final answer
        if not response.tool_calls:
            print(f"Final Answer: {response.content}")
            return response.content

        # LLM wants to use tools
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"Thought : LLM decided to use '{tool_name}'")
            print(f"Action  : {tool_name}({tool_args})")

            # execute the tool
            result = tool_map[tool_name].invoke(tool_args)
            print(f"Observation: {result}")

            # pass tool result back to LLM as ToolMessage
            messages.append(ToolMessage(
                content=result,
                tool_call_id=tool_call["id"]
            ))

    return "Max steps reached without final answer"


# ── Run examples ──────────────────────────────────────────────
print("=== ReAct Agent Examples ===")

# Example 1 — single tool
react_agent("What is the weather in Pune?")

# Example 2 — two tools in sequence
react_agent("What is the weather in Mumbai? Convert that temperature to Fahrenheit.")

# Example 3 — three tools, multi-step reasoning
react_agent("What is UPI market share and how many times bigger is it than 50%? Calculate the ratio.")

print("""
=== Summary ===
ReAct = Reasoning + Acting loop

Step by step:
  1. LLM receives question
  2. LLM thinks → calls a tool (Action)
  3. Tool runs → result returned (Observation)
  4. LLM reads result → thinks again
  5. Calls another tool if needed
  6. When LLM has enough info → gives Final Answer

Key classes:
  ToolMessage → passes tool result back to LLM
  tool_calls  → LLM's decision to call tools
  messages[]  → full conversation including tool results

This is the foundation of every AI agent!
""")