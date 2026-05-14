import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

set_tracing_disabled(True)
load_dotenv()
# 🔑 Groq client
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

model = OpenAIChatCompletionsModel(
    model="llama-3.1-8b-instant",
    openai_client=client
)

# 🧠 Agent
agent = Agent(
    name="Spam Detector",
    instructions="""
    You are a spam detection system.

    Classify the message as:
    - Spam
    - Not Spam

    Return only one word.
    """,
    model=model
)

async def main():
    
 
        msg=input("Enter a message to classify: ")
        result = await Runner.run(agent, input=msg)
        print(f"{msg} ➜ {result.final_output}")

asyncio.run(main())