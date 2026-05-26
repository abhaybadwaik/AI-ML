"""
Phase 4 · Lesson 1 — Tool Definition & Binding
Teaching the LLM what tools it can use

WHAT WE ARE TRYING TO ACHIEVE:
LLM alone can only generate text.
Tools give LLM the ability to take actions — search, calculate, query APIs.
This lesson shows how to define tools and bind them to an LLM.

Two ways to define tools:
  @tool decorator  → simple, most common
  StructuredTool   → when you need more control
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool, StructuredTool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import json

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=500)


# ── 1. @tool decorator — simplest way ────────────────────────
# Just add @tool above any Python function
# LLM reads the docstring to understand what the tool does
# Docstring is critical — LLM uses it to decide when to call the tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city.
    Use this when user asks about weather in any location."""
    # in real project — call a weather API here
    weather_data = {
        "Mumbai": "28°C, Humid, Partly Cloudy",
        "Delhi": "35°C, Hot, Clear Sky",
        "Pune": "26°C, Pleasant, Light Breeze",
        "Hyderabad": "30°C, Warm, Sunny",
    }
    return weather_data.get(city, f"Weather data not available for {city}")


@tool
def calculate(expression: str) -> str:
    """Perform mathematical calculations.
    Use this for any math operations like addition, multiplication, percentages.
    Example: '25 * 9/5 + 32' or '150 * 0.15'"""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def search_upi_info(query: str) -> str:
    """Search for information about UPI digital payments in India.
    Use this when user asks about UPI, digital payments, or NPCI."""
    # in real project — call a search API or query your RAG pipeline
    info = {
        "growth": "UPI transactions grew from 92 crore in 2018 to 17,221 crore in 2024",
        "market share": "UPI accounts for 83% of all digital payment transactions in India",
        "launched": "UPI was launched in 2016 by NPCI",
        "users": "India processes 48.5% of all real-time digital payments globally",
    }
    for key, value in info.items():
        if key in query.lower():
            return value
    return "UPI is a real-time payment system developed by NPCI launched in 2016."


print("=== Tools defined ===")
print(f"Tool 1: {get_weather.name} — {get_weather.description[:60]}...")
print(f"Tool 2: {calculate.name} — {calculate.description[:60]}...")
print(f"Tool 3: {search_upi_info.name} — {search_upi_info.description[:60]}...")
print()


# ── 2. Tool Schema — what LLM sees ───────────────────────────
# When you bind tools to LLM, it sees the schema
# Schema tells LLM: tool name, what it does, what inputs it needs

print("=== Tool Schema (what LLM sees) ===")
print(json.dumps(get_weather.args_schema.model_json_schema(), indent=2))
print()


# ── 3. Binding tools to LLM ──────────────────────────────────
# bind_tools() tells the LLM what tools are available
# LLM can now decide to call a tool instead of just generating text

tools = [get_weather, calculate, search_upi_info]
llm_with_tools = llm.bind_tools(tools)

print("=== LLM with tools bound ===")
print("Tools bound:", [t.name for t in tools])
print()


# ── 4. LLM decides to use a tool ─────────────────────────────
# When LLM thinks it needs a tool — it returns a tool_call
# not a text response — a structured call with tool name and arguments

print("=== LLM deciding to use tools ===")

messages = [HumanMessage(content="What is the weather in Mumbai?")]
response = llm_with_tools.invoke(messages)

print(f"Question: What is the weather in Mumbai?")
print(f"Response type     : {type(response).__name__}")
print(f"response.content  : '{response.content}'")  # empty — LLM wants to use tool
print(f"response.tool_calls: {response.tool_calls}")  # tool call details
print()


# ── 5. Executing the tool call ────────────────────────────────
# LLM said "call get_weather with city=Mumbai"
# Now we actually execute it

print("=== Executing the tool ===")

if response.tool_calls:
    tool_call = response.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]

    print(f"LLM wants to call : {tool_name}")
    print(f"With arguments    : {tool_args}")

    # find and execute the right tool
    tool_map = {t.name: t for t in tools}
    result = tool_map[tool_name].invoke(tool_args)
    print(f"Tool result       : {result}")
print()


# ── 6. Multiple tool calls ────────────────────────────────────
print("=== Complex question — multiple tools needed ===")

complex_question = "What is the weather in Delhi and calculate 35 celsius to fahrenheit?"
messages = [HumanMessage(content=complex_question)]
response = llm_with_tools.invoke(messages)

print(f"Question: {complex_question}")
print(f"Tool calls requested: {len(response.tool_calls)}")
for tc in response.tool_calls:
    print(f"  → {tc['name']}({tc['args']})")
    result = tool_map[tc['name']].invoke(tc['args'])
    print(f"     Result: {result}")
print()


print("""
=== Summary ===
@tool decorator    → define any Python function as a tool
docstring          → critical! LLM reads this to decide when to use the tool
bind_tools()       → tell LLM what tools are available
response.tool_calls → LLM's decision to call a tool with arguments
tool.invoke()      → actually execute the tool

Key insight:
  LLM doesn't execute tools itself
  LLM just DECIDES which tool to call and with what arguments
  YOUR code executes the actual tool
  This is called "tool calling" or "function calling"
""")