import os
import asyncio
import requests
from dotenv import load_dotenv


from agents import (
    Agent,
    Runner,
    function_tool,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_export_api_key
)

# ---------------------------
# 🔑 Load ENV
# ---------------------------
load_dotenv() 
set_tracing_export_api_key(os.getenv("TRACING_EXPORT_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------------------
# 🔹 LLM (Groq)
# ---------------------------
client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client,
)

# ---------------------------
# 🌤 TOOL
# ---------------------------
@function_tool
def get_weather(city: str) -> str:
    """ Get weather for a city"""

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    res = requests.get(url)
    data = res.json()

    if data.get("cod") != 200:
        return f"❌ City not found: {city}"

    return (
        f"🌍 {city}\n"
        f"🌤 {data['weather'][0]['description']}\n"
        f"🌡 {data['main']['temp']}°C\n"
        f"💧 {data['main']['humidity']}%\n"
        f"💨 {data['wind']['speed']} m/s"
    )

# ---------------------------
# 🧠 AGENT
# ---------------------------
agent = Agent(
    name="Weather Agent",
    model=model,
    instructions="""
Only use get_weather when the user explicitly asks
about weather, temperature, climate, or forecast.

If the user only provides a city name without
weather-related intent, ask a clarification question.
""",
    tools=[get_weather],
)

# ---------------------------
# 🚀 RUN
# ---------------------------
async def main():
    while True:
        user_input = input("\nAsk: ")

        if user_input.lower() == "exit":
            break

        result = await Runner.run(agent, input=user_input)
        print("\n", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())