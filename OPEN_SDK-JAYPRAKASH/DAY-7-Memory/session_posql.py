import os
import asyncio
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine

from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.memory import SQLAlchemySession

from agents import AsyncOpenAI, OpenAIChatCompletionsModel

# -------------------------------------------------
# ENV SETUP
# -------------------------------------------------
load_dotenv()
set_tracing_disabled(True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -------------------------------------------------
# GROQ CLIENT
# -------------------------------------------------
client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client
)

# -------------------------------------------------
# POSTGRES CONNECTION (LOCAL DB)
# -------------------------------------------------
DATABASE_URL = "postgresql+asyncpg://postgres:Jaya1234%40%23@localhost:5432/LOCAL"

engine = create_async_engine(DATABASE_URL, echo=False)

# -------------------------------------------------
# AGENT
# -------------------------------------------------
agent = Agent(
    name="Groq Assistant",
    instructions="You are a helpful assistant. Remember user context using PostgreSQL memory. do not give previous stored messages",
    model=model
)

# -------------------------------------------------
# MAIN CHAT LOOP
# -------------------------------------------------
async def main():

    session = SQLAlchemySession(
        session_id="user-456",
        engine=engine,
        create_tables=True
    )

    print("\n🔥 Chat Started (type 'exit' to stop)\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Chat ended")
            break

        result = await Runner.run(
            agent,
            user_input,
            session=session
        )

        print("Bot:", result.final_output)
        print("-" * 50)

    await engine.dispose()


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())