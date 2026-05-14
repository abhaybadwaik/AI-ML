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

# 🧠 Model
model = OpenAIChatCompletionsModel(
    model="llama-3.1-8b-instant",
    openai_client=client
)

# 📌 One-shot Agent
agent = Agent(
    name="Resume Parser",
    instructions="""
You are a resume information extraction system.

Convert resume text into JSON format.

Example:
Input: John Doe has 5 years experience in Python and works at Google
Output:
{
  "name": "John Doe",
  "experience_years": 5,
  "skills": ["Python"],
  "company": "Google"
}

Now follow the same format strictly.
Return only JSON.
""",
    model=model
)

async def main():
    resume_text = input("Enter resume text: ")

    result = await Runner.run(
        agent,
        input=resume_text
    )

    print(result.final_output)

asyncio.run(main())