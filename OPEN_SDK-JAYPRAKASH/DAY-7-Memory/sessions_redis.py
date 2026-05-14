import asyncio
import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    RunConfig,
    SessionSettings,
)

from agents.extensions.memory import RedisSession

# ---------------------------
# 🔴 CONFIG
# ---------------------------
load_dotenv()
set_tracing_disabled(True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client,
)

# ---------------------------
# 🤖 AGENT
# ---------------------------
agent = Agent(
    name="Assistant",
    instructions="""
You are a helpful assistant.

Rules:
- Use memory only when needed
- Do not repeat stored facts unnecessarily
- Do not assume user preferences
""",
    model=model,
)

# ---------------------------
# 🔥 REDIS SESSION
# ---------------------------
session = RedisSession.from_url(
    session_id="demo_user",
    url="redis://127.0.0.1:6379/0",
)

# ---------------------------
# 🧠 HISTORY CONTROL
# ---------------------------
def keep_recent_history(history, new_input):
    MAX_HISTORY = 7
    return history[-MAX_HISTORY:] + new_input

# ---------------------------
# 🚀 RUN AGENT
# ---------------------------
async def run_agent(user_input):
    result = await Runner.run(
        agent,
        input=user_input,
        session=session,
        run_config=RunConfig(
            session_settings=SessionSettings(limit=20),
            session_input_callback=keep_recent_history,
        ),
    )
    return result.final_output

# ---------------------------
# 🗑️ CLEAR MEMORY
# ---------------------------
async def clear_memory():
    await session.clear_session()

# ---------------------------
# 💬 CLI LOOP
# ---------------------------
async def main():
    print("\n🤖 Chat started (type 'exit' to stop, 'clear' to reset memory)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        if user_input.lower() == "clear":
            await clear_memory()
            print("🗑️ Memory cleared!\n")
            continue

        response = await run_agent(user_input)

        print(f"AI: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())