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

# 📌 Few-shot Agent
agent = Agent(
    name="Product Categorizer",
    instructions="""
You are a product classification system.

Classify products into categories:

Examples:
Product: iPhone 15 Pro Max
Category: Electronics > Mobile Phones

Product: Nike Air Zoom Pegasus
Category: Sports > Shoes

Product: Samsung 55 inch TV
Category: Electronics > Television

Product: Levi's Jeans
Category: Fashion > Clothing

Now classify new product.

Return only category.
""",
    model=model
)

async def main():
    product = input("Enter product name: ")

    result = await Runner.run(agent, input=product)
    print(f"{product} ➜ {result.final_output}")

asyncio.run(main())