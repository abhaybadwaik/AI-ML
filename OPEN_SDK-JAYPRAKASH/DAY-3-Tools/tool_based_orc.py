import asyncio
import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
    set_tracing_export_api_key
)

# -------------------------------------------------
# LOAD ENV VARIABLES
# -------------------------------------------------
load_dotenv()

set_tracing_export_api_key(
    os.getenv("TRACING_EXPORT_API_KEY")
)

# -------------------------------------------------
# GROQ CLIENT
# -------------------------------------------------
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# -------------------------------------------------
# BILLING TOOL
# -------------------------------------------------
@function_tool
def billing_tool(issue: str) -> str:
    """
    Handles billing-related issues such as:
    - payment failures
    - refunds
    - duplicate charges
    - subscription problems
    """

    return "💳 Billing Team: Refund initiated. ETA 3–5 days."


# -------------------------------------------------
# TECH SUPPORT TOOL
# -------------------------------------------------
@function_tool
def tech_tool(issue: str) -> str:
    """
    Handles technical issues such as:
    - app crashes
    - login problems
    - bugs/errors
    - performance issues
    """

    return "🛠 Tech Support: Please restart the app and clear cache."


# -------------------------------------------------
# ORDER SUPPORT TOOL
# -------------------------------------------------
@function_tool
def order_tool(issue: str) -> str:
    """
    Handles order and delivery issues such as:
    - tracking orders
    - delayed delivery
    - shipment updates
    """

    return "📦 Order Support: Your order is currently in transit."


# -------------------------------------------------
# ROUTER AGENT
# -------------------------------------------------
router = Agent(
    name="Customer Support Router",

    model=model,

instructions="""
You are a support routing assistant.

Analyze all user issues carefully.

If multiple issues exist:
- call ALL relevant tools
- combine all responses into one helpful answer

Examples:
- payment failed + app crash
  → billing_tool + tech_tool

- payment failed + order canceled
  → billing_tool + order_tool
""",

    tools=[
        billing_tool,
        tech_tool,
        order_tool
    ],
)

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
async def main():

    print("✅ Customer Support Agent Started")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("Ask: ")

        if user_input.lower() == "exit":
            print("👋 Exiting...")
            break

        result = await Runner.run(
            router,
            input=user_input
        )

        print("\nResponse:", result.final_output)
        print("-" * 50)


# -------------------------------------------------
# START PROGRAM
# -------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())