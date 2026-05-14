import asyncio
import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_export_api_key,
)

# =================================================
# LOAD ENV VARIABLES
# =================================================
load_dotenv()

set_tracing_export_api_key(
    os.getenv("TRACING_EXPORT_API_KEY")
)

# =================================================
# GEMINI CLIENT
# =================================================
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# =================================================
# BILLING AGENT
# =================================================
billing_agent = Agent(
    name="billing_agent",

    model=model,

    instructions="""
You are a billing support specialist.

Handle:
- payment failures
- refunds
- duplicate charges
- subscription issues
- money deducted problems

Give polite and professional responses.
"""
)

# =================================================
# TECH SUPPORT AGENT
# =================================================
tech_support_agent = Agent(
    name="tech_support_agent",

    model=model,

    instructions="""
You are a technical support specialist.

Handle:
- app crashes
- login issues
- bugs/errors
- slow performance
- technical troubleshooting

Provide troubleshooting steps clearly.
"""
)

# =================================================
# ORDER SUPPORT AGENT
# =================================================
order_support_agent = Agent(
    name="order_support_agent",

    model=model,

    instructions="""
You are an order support specialist.

Handle:
- order tracking
- delayed deliveries
- shipment updates
- canceled orders
- package status

Provide helpful order assistance.
"""
)

# =================================================
# ROUTER AGENT
# =================================================
router_agent = Agent(
    name="customer_support_router",

    model=model,

    instructions="""
You are a smart customer support router.

Your responsibilities:
- Understand the user's issue
- Transfer the conversation to the correct specialist agent

Routing Rules:
- payment/refund/billing → billing_agent
- app/crash/technical → tech_support_agent
- order/shipping/delivery → order_support_agent

If multiple issues exist:
- choose the MOST important issue
- transfer to ONLY ONE specialist agent
""",

    handoffs=[
        billing_agent,
        tech_support_agent,
        order_support_agent
    ]
)

# =================================================
# MAIN LOOP
# =================================================
async def main():

    print("✅ Multi-Agent Handoff System Started")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("Ask: ")

        if user_input.lower() == "exit":
            print("👋 Exiting...")
            break

        try:

            result = await Runner.run(
                router_agent,
                input=user_input
            )

            print("\nResponse:", result.final_output)
            print("-" * 60)

        except Exception as e:

            print("\n❌ ERROR:", e)
            print("-" * 60)

# =================================================
# START PROGRAM
# =================================================
if __name__ == "__main__":
    asyncio.run(main())