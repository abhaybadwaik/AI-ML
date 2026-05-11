import os
import ast
import datetime
import operator
import random
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()
groq_api = os.getenv("GROQ_API_KEY")
weather_api = os.getenv("WEATHER_API_KEY")

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api)


@tool
def calculator(expression: str) -> str:
    """Useful for performing mathematical calculations. Input must be a valid math expression like '2 + 2' or '10 * 5'."""
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
        result = _eval(ast.parse(expression, mode='eval').body)
        return f"Result: {result}"
    except Exception as e:
        return f"Math Error: {str(e)}"


@tool
def weather(city: str) -> str:
    """Useful for getting current weather of any city."""
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key={weather_api}&q={city}",
            timeout=10
        )
        if response.status_code != 200:
            return f"❌ Weather API Error {response.status_code}: {response.text}"

        data = response.json()["current"]
        return (
            f"🌤 Weather in {city}:\n"
            f"  🌡 Temp: {data['temp_c']}°C / {data['temp_f']}°F\n"
            f"  ☁ Condition: {data['condition']['text']}\n"
            f"  💧 Humidity: {data['humidity']}%\n"
            f"  💨 Wind: {data['wind_kph']} kph"
        )
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def current_date(dummy: str = "") -> str:
    """Useful for getting the current date."""
    return f"📅 Today's date is {datetime.datetime.now().strftime('%d-%m-%Y')}"


@tool
def motivation(dummy: str = "") -> str:
    """Useful for getting a motivational quote."""
    return random.choice([
        "Success comes from consistency 🔥",
        "Discipline beats motivation 💪",
        "Never stop learning 🚀",
        "Your future is created by what you do today 📈"
    ])


tools = [calculator, weather, current_date, motivation]
tools_by_name = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

print("\n🤖 Multi Tool AI Agent Started (type 'bye' to exit)\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "bye":
        print("👋 Goodbye!")
        break

    messages = [HumanMessage(content=user_input)]
    response = llm_with_tools.invoke(messages)
    messages.append(response)

    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_fn = tools_by_name.get(tool_call["name"])
            result = tool_fn.invoke(tool_call["args"]) if tool_fn else f"Tool '{tool_call['name']}' not found."
            print(f"\n🔧 {tool_call['name']} → {result}")
            messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

        final_response = llm_with_tools.invoke(messages)
        print(f"\n🤖 AI: {final_response.content}")
    else:
        print(f"\n🤖 AI: {response.content}")