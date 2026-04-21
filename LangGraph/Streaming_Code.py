import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 🔑 Load API key
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    streaming=True   # 🔥 IMPORTANT
)

print("🤖 Streaming AI (type 'bye' to exit)")

while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "bye":
        print("AI: Goodbye 👋")
        break

    print("AI:", end=" ", flush=True)

    # 🔥 Streaming response
    for chunk in llm.stream(user_input):
        print(chunk.content, end="", flush=True)

    print()  # new line