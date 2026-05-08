import os
import ast
import datetime
import operator
import random
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# 🔑 Load API Keys
load_dotenv()

groq_api = os.getenv("GROQ_API_KEY")
weather_api = os.getenv("WEATHER_API_KEY")

# ✅ Validate keys on startup
if not groq_api:
    raise ValueError("❌ GROQ_API_KEY not found in .env")
if not weather_api:
    raise ValueError("❌ WEATHER_API_KEY not found in .env")

print(f"✅ Weather API Key loaded: {weather_api[:6]}...{weather_api[-4:]}")

# 🤖 LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=groq_api
)

# 🔧 TOOL 1 → Calculator (safe, no eval)
@tool
def calculator(expression: str) -> str:
    """Useful for performing mathematical calculations. Input must be a valid math expression like '2 + 2' or '10 * 5'."""
    try:
        # Safe math operators only
        allowed_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
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

        tree = ast.parse(expression, mode='eval')
        result = _eval(tree.body)
        return f"Result: {result}"
    except Exception as e:
        return f"Math Error: {str(e)}"


# 🔧 TOOL 2 → Weather with proper error reporting
@tool
def weather(city: str) -> str:
    """Useful for getting current weather of any city."""

    if not weather_api:
        return "❌ WEATHER_API_KEY is not set in your .env file."

    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api}&q={city}"

    try:
        response = requests.get(url, timeout=10)

        # ✅ Catch HTTP-level errors (401, 403, 404, etc.)
        if response.status_code == 401:
            return "❌ Weather API Error 401: Invalid API key. Check your WEATHER_API_KEY in .env"
        elif response.status_code == 403:
            return "❌ Weather API Error 403: API key doesn't have access. Check your plan."
        elif response.status_code == 400:
            return f"❌ Weather API Error 400: City '{city}' not found or bad request."
        elif response.status_code != 200:
            return f"❌ Weather API Error {response.status_code}: {response.text}"

        data = response.json()
        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]
        humidity = data["current"]["humidity"]
        wind_kph = data["current"]["wind_kph"]

        return (
            f"🌤 Weather in {city}:\n"
            f"  🌡 Temp: {temp_c}°C / {temp_f}°F\n"
            f"  ☁ Condition: {condition}\n"
            f"  💧 Humidity: {humidity}%\n"
            f"  💨 Wind: {wind_kph} kph"
        )

    except requests.exceptions.Timeout:
        return "❌ Weather API timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return "❌ Could not connect to Weather API. Check your internet."
    except KeyError as e:
        return f"❌ Unexpected API response format. Missing key: {e}. Raw: {response.text[:200]}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


# 🔧 TOOL 3 → Current Date
@tool
def current_date(dummy: str = "") -> str:
    """Useful for getting the current date."""
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    return f"📅 Today's date is {today}"


# 🔧 TOOL 4 → Motivation
@tool
def motivation(dummy: str = "") -> str:
    """Useful for getting a motivational quote."""
    quotes = [
        "Success comes from consistency 🔥",
        "Discipline beats motivation 💪",
        "Never stop learning 🚀",
        "Your future is created by what you do today 📈"
    ]
    return random.choice(quotes)


# 🔥 Bind tools
tools = [calculator, weather, current_date, motivation]
tools_by_name = {t.name: t for t in tools}  # ✅ Cleaner lookup

llm_with_tools = llm.bind_tools(tools)

# 🚀 Agent Loop
print("\n🤖 Multi Tool AI Agent Started (type 'bye' to exit)\n")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue
    if user_input.lower() == "bye":
        print("👋 Goodbye!")
        break

    # Build message history for this turn
    messages = [HumanMessage(content=user_input)]

    # 🧠 AI decides tool(s)
    response = llm_with_tools.invoke(messages)
    messages.append(response)  # Add AI response to history

    # 🔥 Execute all tool calls (handles multi-tool turns)
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            print(f"\n🔧 Using tool: {tool_name} with args: {tool_args}")

            tool_fn = tools_by_name.get(tool_name)
            if tool_fn:
                result = tool_fn.invoke(tool_args)
                print(f"✅ Tool Result: {result}")

                # ✅ Feed result back into message history
                messages.append(
                    ToolMessage(content=result, tool_call_id=tool_id)
                )
            else:
                messages.append(
                    ToolMessage(content=f"Tool '{tool_name}' not found.", tool_call_id=tool_id)
                )

        # ✅ Let LLM generate final natural language answer using tool results
        final_response = llm_with_tools.invoke(messages)
        print(f"\n🤖 AI: {final_response.content}")

    else:
        print(f"\n🤖 AI: {response.content}")