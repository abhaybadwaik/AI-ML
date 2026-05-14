import asyncio
import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    ModelSettings,
    set_tracing_disabled,
)

load_dotenv()
set_tracing_disabled(True)

# ---------------------------------------------------
# GROQ CLIENT
# ---------------------------------------------------
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client,
)

# ---------------------------------------------------
# AGENT
# ---------------------------------------------------
agent = Agent(
    name="Assistant",
    instructions="""
You are a helpful AI assistant.

Rules:
- Keep answers simple
- Use bullet points when helpful
- Keep response under 100 words
""",
    model=model,
)

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
async def main():

    result = await Runner.run(
        agent,
        input="Explain AI simply",

        # prevents infinite loops
        max_turns=3,

        # runtime execution config
        run_config=RunConfig(

            # override model settings at runtime
            model_settings=ModelSettings(
                temperature=0.3,
                max_tokens=150,
            ),

            # tracing disabled already
            tracing_disabled=True,
        ),
    )

    print("\nFINAL OUTPUT:\n")
    print(result.final_output)

asyncio.run(main())