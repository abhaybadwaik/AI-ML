import asyncio
import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_export_api_key
    )

# ─────────────────────────────
# SETUP
# ─────────────────────────────

load_dotenv()
set_tracing_export_api_key(os.getenv("TRACING_EXPORT_API_KEY"))

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client,
)

# ─────────────────────────────
# SPECIALIST AGENTS
# ─────────────────────────────

billing_agent = Agent(
    name="BillingAgent",
    model=model,
    instructions="""
You are a billing support expert.

Handle:
- refund requests
- payment failures
- double charges

Reply in 2-3 lines only.
"""
)

tech_agent = Agent(
    name="TechAgent",
    model=model,
    instructions="""
You are a technical support expert.

Handle:
- app crashes
- bugs
- login issues

Reply in 2-3 lines only.
"""
)

sales_agent = Agent(
    name="SalesAgent",
    model=model,
    instructions="""
You are a sales support expert.

Handle:
- pricing questions
- subscription plans
- discounts

Reply in 2-3 lines only.
"""
)

# ─────────────────────────────
# ORCHESTRATOR (REAL USE CASE)
# ─────────────────────────────

orchestrator = Agent(
    name="EmailRouter",
    model=model,
    instructions="""
You are an email triage system.

TASK:
- Read user message
- Decide correct department
- Call ONLY ONE tool
- Return final answer

Routing:
- billing_support → payment/refund issues
- tech_support → bugs/crashes
- sales_support → pricing/questions
""",
    tools=[
        billing_agent.as_tool(
            tool_name="billing_support",
            tool_description="Handles billing and refund issues"
        ),
        tech_agent.as_tool(
            tool_name="tech_support",
            tool_description="Handles technical issues"
        ),
        sales_agent.as_tool(
            tool_name="sales_support",
            tool_description="Handles pricing and sales questions"
        ),
    ],
)

# ─────────────────────────────
# RUN DEMO
# ─────────────────────────────

async def main():
    emails = [
        "I was charged twice for my subscription",
        "What is the price of premium plan?"
    ]

    for email in emails:
        print("\nEMAIL:", email)

        result = await Runner.run(
            orchestrator,
            input=email,
            max_turns=10
        
        )

        print("RESPONSE:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())