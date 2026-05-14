import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

# 🔹 Load .env
load_dotenv()
set_tracing_disabled(True)

# 🔑 API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 🔹 Client
client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# 🔹 Model
model = OpenAIChatCompletionsModel(
    model="llama-3.1-8b-instant",
    openai_client=client,
)

# 🔹 Agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model=model,
)
# ---------------------------
# 🚀 CLI LOOP
# ---------------------------
def main():
    print("🤖 Basic Agent (type 'exit' to quit)\n")

    while True:
        user_input = input("Ask: ")

        if user_input.lower() == "exit":
            break

        if not user_input.strip():
            print("⚠️ Enter something\n")
            continue

        result = Runner.run_sync(agent, user_input)
        print("\n🤖:", result.final_output, "\n")


if __name__ == "__main__":
    main()