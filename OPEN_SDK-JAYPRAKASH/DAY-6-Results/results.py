import os
import asyncio
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
    set_tracing_disabled,
)

from openai.types.responses import ResponseTextDeltaEvent

# =====================================================
# ENV
# =====================================================

load_dotenv()
set_tracing_disabled(True)

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

model = OpenAIChatCompletionsModel(
    model="llama-3.1-8b-instant",
    openai_client=client,
)

# =====================================================
# TOOLS
# =====================================================

@function_tool
def calculate_refund(amount: float, tax: float) -> str:

    print("\n🔧 TOOL EXECUTING → calculate_refund")
    print("📥 AMOUNT:", amount)
    print("📥 TAX:", tax)

    total = amount + (amount * tax / 100)

    result = f"Refund amount after tax is {total}"

    print("📤 TOOL RESULT:", result)

    return result


@function_tool
def create_support_ticket(issue: str) -> str:

    print("\n🔧 TOOL EXECUTING → create_support_ticket")
    print("📥 ISSUE:", issue)

    ticket = "TICKET-45821"

    result = f"Support ticket created successfully: {ticket}"

    print("📤 TOOL RESULT:", result)

    return result


# =====================================================
# AGENT
# =====================================================

support_agent = Agent(
    name="Customer Support Assistant",
    instructions="""
You are an AI customer support assistant.

RULES:
- Refund/payment questions → use calculate_refund
- Technical complaints/issues → use create_support_ticket
- Keep responses short and professional
- After tool output, return final answer
""",
    tools=[
        calculate_refund,
        create_support_ticket,
    ],
    tool_use_behavior="stop_on_first_tool",
    model=model,
)

# =====================================================
# NORMAL RUN
# =====================================================

async def normal_run_demo():

    print("\n================ NORMAL RUN ================\n")

    result = await Runner.run(
        support_agent,
        "Refund 1000 rupees with 18 percent tax"
    )

    print("\n✅ FINAL OUTPUT:")
    print(result.final_output)

    print("\n🧠 MEMORY FOR NEXT TURN:")
    print(result.to_input_list())

    print("\n🤖 LAST AGENT:")
    print(result.last_agent.name)


# =====================================================
# STREAMING RUN
# =====================================================

async def streaming_demo():

    print("\n================ STREAMING RUN ================\n")

    result = Runner.run_streamed(
        support_agent,
        "My app crashes during payment"
    )

    async for event in result.stream_events():

        print("\n--------------------------------------------------")
        print("📡 EVENT:", event.type)
        print("--------------------------------------------------")

        # =================================================
        # RAW TOKEN STREAM
        # =================================================

        if event.type == "raw_response_event":

            if isinstance(event.data, ResponseTextDeltaEvent):

                print("🧠 TOKEN:", event.data.delta)

        # =================================================
        # STRUCTURED EVENTS
        # =================================================

        elif event.type == "run_item_stream_event":

            item = event.item

            print("📦 ITEM TYPE:", item.type)

            # TOOL CALL
            if item.type == "tool_call_item":

                print("\n🔧 TOOL CALL DETECTED")

                print("TOOL NAME:", item.raw_item.name)
                print("ARGUMENTS:", item.raw_item.arguments)

            # TOOL OUTPUT
            elif item.type == "tool_call_output_item":

                print("\n📦 TOOL OUTPUT RECEIVED")

                print(item.output)

            # FINAL MESSAGE
            elif item.type == "message_output_item":

                print("\n📩 FINAL MESSAGE RECEIVED")

        # =================================================
        # AGENT SWITCH EVENT
        # =================================================

        elif event.type == "agent_updated_stream_event":

            print("\n🔄 ACTIVE AGENT:")
            print(event.new_agent.name)

    print("\n✅ FINAL OUTPUT:")
    print(result.final_output)

    print("\n✅ STREAM COMPLETE:")
    print(result.is_complete)


# =====================================================
# INSPECTION / OBSERVABILITY
# =====================================================

async def inspection_demo():

    print("\n================ RESULT INSPECTION ================\n")

    result = await Runner.run(
        support_agent,
        "Refund 500 with 5 percent tax"
    )

    print("\n📦 NEW ITEMS:")
    for item in result.new_items:
        print("-", item.type)

    print("\n📡 RAW RESPONSES:")
    print(len(result.raw_responses))

    print("\n🛡 INPUT GUARDRAILS:")
    print(result.input_guardrail_results)

    print("\n🛡 OUTPUT GUARDRAILS:")
    print(result.output_guardrail_results)


# =====================================================
# MAIN
# =====================================================

async def main():

    await normal_run_demo()

    await streaming_demo()

    await inspection_demo()


if __name__ == "__main__":
    asyncio.run(main())