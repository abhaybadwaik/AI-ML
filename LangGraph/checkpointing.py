import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 🔑 Load API
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

FILE = "memory.json"

# 🧠 Load memory
def load_memory():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

# 🧠 Save memory
def save_memory(history):
    with open(FILE, "w") as f:
        json.dump(history, f, indent=2)

# 🚀 Load previous conversation
history = load_memory()

print("🤖 AI with Persistent Memory (type 'bye' to exit)")

# 🔥 System behavior (IMPORTANT UPGRADE)
system_prompt = {
    "role": "system",
    "content": "You remember all past user details and answer confidently based on conversation history. Do not say you don't remember."
}

while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "bye":
        print("AI🤖: Goodbye 👋")
        break

    # Add user input
    history.append({"role": "user", "content": user_input})

    # 🔥 Send system + history
    response = llm.invoke([system_prompt] + history)

    ai_reply = response.content
    print("AI🤖:", ai_reply)

    # Save AI response
    history.append({"role": "assistant", "content": ai_reply})

    # 🔥 Save checkpoint
    save_memory(history)

    