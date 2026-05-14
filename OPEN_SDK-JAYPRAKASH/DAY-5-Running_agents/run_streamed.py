import asyncio
import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
    set_tracing_disabled,
)

set_tracing_disabled(True)
load_dotenv()

 

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# ---------------------------------------------------
# 🔑 MODEL
# ---------------------------------------------------

model = OpenAIChatCompletionsModel(
    model="llama-3.1-8b-instant",
    openai_client=client,
)

# ---------------------------------------------------
# 🛠 WEATHER TOOL
# ---------------------------------------------------

@function_tool
def get_weather(city: str) -> str:
    print("\n🔧 TOOL EXECUTING → get_weather")
    print("📥 CITY:", city)

    fake_db = {
        "hyderabad": "32°C and sunny",
        "delhi": "38°C and hot",
        "mumbai": "29°C and rainy",
    }

    result = fake_db.get(city.lower(), "Weather unavailable")

    print("📤 TOOL RESULT:", result)

    return result

# ---------------------------------------------------
# 🛠 BILL TOOL
# ---------------------------------------------------

@function_tool
def calculate_bill(amount: float, tax: float) -> str:
    print("\n🔧 TOOL EXECUTING → calculate_bill")
    print("📥 AMOUNT:", amount)
    print("📥 TAX:", tax)

    total = amount + (amount * tax / 100)

    result = f"Final amount is {total}"

    print("📤 TOOL RESULT:", result)

    return result

# ---------------------------------------------------
# 🧠 MAIN AGENT
# ---------------------------------------------------

agent = Agent(
    name="Main Assistant",
    instructions="""
You are a smart assistant.

RULES:
- Use ONE tool only
- Never call multiple tools
- After tool result:
  respond immediately
- Never continue reasoning
- Never retry tools
""",
    model=model,
    tools=[
        get_weather,
        calculate_bill,
    ],
    tool_use_behavior="stop_on_first_tool",
)

# ---------------------------------------------------
# 🚀 STREAMED RUN
# ---------------------------------------------------

async def run_query(user_input: str):

    print("\n" + "=" * 60)
    print("👤 USER:", user_input)
    print("=" * 60)

    result = Runner.run_streamed(
        agent,
        input=user_input,
        max_turns=2,
    )

    async for event in result.stream_events():

        print("\n" + "-" * 50)
        print("📡 EVENT:", event.type)
        print("-" * 50)

        # -----------------------------------------
        # RAW TOKEN STREAM
        # -----------------------------------------

        if event.type == "raw_response_event":

            if hasattr(event.data, "delta"):

                token = event.data.delta

                if token:
                    print("🧠 TOKEN:", token)

        # -----------------------------------------
        # RUN ITEM EVENTS
        # -----------------------------------------

        elif event.type == "run_item_stream_event":

            item = event.item

            print("📦 ITEM TYPE:", item.type)

            # TOOL CALL
            if item.type == "tool_call_item":

                print("\n🔧 TOOL CALL DETECTED")

                try:
                    print("TOOL NAME:", item.raw_item.name)
                    print("ARGUMENTS:", item.raw_item.arguments)
                except:
                    pass

            # TOOL OUTPUT
            elif item.type == "tool_call_output_item":

                print("\n📦 TOOL OUTPUT RECEIVED")
                print(item.output)

            # FINAL MESSAGE
            elif item.type == "message_output_item":

                print("\n📩 FINAL MESSAGE RECEIVED")

        # -----------------------------------------
        # AGENT SWITCH
        # -----------------------------------------

        elif event.type == "agent_updated_stream_event":

            print("\n🔄 ACTIVE AGENT:", event.new_agent.name)

    print("\n✅ FINAL OUTPUT:")
    print(result.final_output)

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

async def main():

    queries = [
        "What is the weather in Hyderabad?",
        "Calculate bill for 1000 with 18 percent tax",
    ]

    for q in queries:
        try:
            await run_query(q)

        except Exception as e:
            print("\n❌ ERROR:", str(e))

# ---------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())