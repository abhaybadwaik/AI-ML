import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel , set_tracing_disabled

load_dotenv()  # Load environment variables from .env file
set_tracing_disabled(True)  # Disable tracing for better performance


# 🔑 Groq client
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# 🤖 Model
model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client,
)

# 🧠 Agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model=model,
)

# ▶️ Run
async def main():
    result = await Runner.run(agent, "Explain AI in simple words")
    print(result.final_output)

asyncio.run(main())