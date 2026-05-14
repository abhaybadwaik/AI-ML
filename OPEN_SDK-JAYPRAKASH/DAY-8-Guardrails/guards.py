import asyncio
import os

from dotenv import load_dotenv
from pydantic import BaseModel

from agents import (
    Agent,
    Runner,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    input_guardrail,
    output_guardrail,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

# =========================================================
# ENV SETUP
# =========================================================

load_dotenv()
set_tracing_disabled(True)

# =========================================================
# GEMINI CLIENT
# =========================================================

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# =========================================================
# PYDANTIC OUTPUT SCHEMAS
# =========================================================

class InputCheck(BaseModel):
    is_math: bool
    reason: str


class OutputCheck(BaseModel):
    has_math: bool
    reason: str


# =========================================================
# INPUT GUARD AGENT
# =========================================================

input_guard_agent = Agent(
    name="Input Guard",
    instructions="""
Detect whether the user input is a math problem.

Return:
- is_math=True if user asks calculations/math
- otherwise False
""",
    model=model,
    output_type=InputCheck,
)

# =========================================================
# OUTPUT GUARD AGENT
# =========================================================

output_guard_agent = Agent(
    name="Output Guard",
    instructions="""
Detect whether the output contains
math calculations or solved equations.
""",
    model=model,
    output_type=OutputCheck,
)

# =========================================================
# INPUT GUARDRAIL
# =========================================================

@input_guardrail(run_in_parallel=True)
async def math_input_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str,
) -> GuardrailFunctionOutput:

    result = await Runner.run(
        input_guard_agent,
        input=input,
        context=ctx.context,
    )

    check: InputCheck = result.final_output

    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.is_math,
    )

# =========================================================
# OUTPUT GUARDRAIL
# =========================================================

@output_guardrail
async def math_output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:

    result = await Runner.run(
        output_guard_agent,
        input=output,
        context=ctx.context,
    )

    check: OutputCheck = result.final_output

    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.has_math,
    )

# =========================================================
# MAIN AGENT
# =========================================================

agent = Agent(
    name="Customer Support",

    instructions="""
You are a customer support assistant.

VERY IMPORTANT:
Generate a detailed response of around 300 words.
Speak politely and professionally.

DO NOT solve math problems.
""",

    model=model,

    input_guardrails=[math_input_guardrail],

    output_guardrails=[math_output_guardrail],
)

# =========================================================
# MAIN PROGRAM
# =========================================================

async def main():

    print("\n==============================")
    print(" GUARDRAILS DEMO ")
    print("==============================\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            break

        try:

            result = await Runner.run(
                agent,
                input=user_input,
            )

            print("\n==============================")
            print(" BOT RESPONSE ")
            print("==============================\n")

            print(result.final_output)

            print("\n==============================\n")

        except InputGuardrailTripwireTriggered as e:

            check: InputCheck = (
                e.guardrail_result.output.output_info
            )

            print("\nINPUT BLOCKED")
            print(check.reason)

        except OutputGuardrailTripwireTriggered as e:

            check: OutputCheck = (
                e.guardrail_result.output.output_info
            )

            print("\nOUTPUT BLOCKED")
            print(check.reason)

        except Exception as e:

            print(f"\nERROR: {e}\n")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())