import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langfuse import get_client
from langfuse.langchain import CallbackHandler  # ← ADD THIS

# 🔑 Load API key
load_dotenv()

# ← ADD THESE 2 LINES
langfuse = get_client()
langfuse_handler = CallbackHandler()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    streaming=True
)

print("🤖 Streaming AI with Langfuse (type 'bye' to exit)")

while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "bye":
        print("AI: Goodbye 👋")
        langfuse.flush()  # ← ADD THIS to send data before exit
        break

    print("AI:", end=" ", flush=True)

    # 🔥 Streaming response — just add config with callback!
    for chunk in llm.stream(
        user_input,
        config={"callbacks": [langfuse_handler]}  # ← ADD THIS
    ):
        print(chunk.content, end="", flush=True)

    print()