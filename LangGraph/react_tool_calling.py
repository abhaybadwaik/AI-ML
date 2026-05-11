import os
import ast
import operator
import random
import requests
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent

load_dotenv()
groq_api    = os.getenv("GROQ_API_KEY")
weather_api = os.getenv("WEATHER_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_api)

@tool
def calculator(expression: str) -> str:
    """Use this ONLY when the user asks to calculate something. Input: math expression like '2 + 2'."""
    allowed_ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod,
    }
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.n
        elif isinstance(node, ast.BinOp):
            op = allowed_ops.get(type(node.op))
            if op is None:
                raise ValueError("Unsupported operator")
            return op(_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -_eval(node.operand)
        else:
            raise ValueError("Unsupported expression")
    try:
        return f"Result: {_eval(ast.parse(expression, mode='eval').body)}"
    except Exception as e:
        return f"Math Error: {e}"


@tool
def weather(city: str) -> str:
    """Use this ONLY when the user asks for weather of a city."""
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key={weather_api}&q={city}",
            timeout=10
        )
        data = response.json()
        if "error" in data:
            return f"Weather Error: {data['error']['message']}"
        c = data["current"]
        return f"Weather in {city}: {c['temp_c']}°C, {c['condition']['text']}, Humidity {c['humidity']}%"
    except Exception as e:
        return f"Weather Error: {e}"


@tool
def motivation(dummy: str = "") -> str:
    """Use this ONLY when the user asks for motivation or a motivational quote."""
    return random.choice([
        "Success comes from consistency 🔥",
        "Discipline beats motivation 💪",
        "Never stop learning 🚀",
        "Your future is created by what you do today 📈",
    ])


agent = create_agent(
    model=llm,
    tools=[calculator, weather, motivation],
    system_prompt=(
        "You are a helpful assistant with access to 3 tools: weather, calculator, and motivation. "
        "ONLY call a tool when the user explicitly asks for it. "
        "NEVER call multiple tools unless the user asked for multiple things. "
        "NEVER say you cannot access real-time data — you have tools for that. "
        "Give a short direct answer using only the tool result. No extra commentary."
    ),
)

def print_clean(messages: list):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            pass
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    args_str = ", ".join(f"{k}={v}" for k, v in tc["args"].items()) or "no args"
                    print(f"  🔧 Calling: {tc['name']}({args_str})")
            elif msg.content:
                print(f"\n🤖 {msg.content}\n")
        elif isinstance(msg, ToolMessage):
            print(f"  ✅ {msg.name}: {msg.content}")

print("\n🤖 ReAct Agent Started  (type 'bye' to exit)\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "bye":
        print("👋 Goodbye!")
        break

    result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
    print_clean(result["messages"])