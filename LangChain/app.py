# AI CODE WITH MEMORY STORED👇🏾👇🏾👇🏾👇🏾
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant"
)

chat_history = []

print("Welcome to my AI bot 🤖")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Bye 👋")
        break

    chat_history.append(("user", user_input))

    response = llm.invoke(chat_history)

    chat_history.append(("ai", response.content))

    print("AI:", response.content)


# AI CODE WITHOUT MEMORY STORED👇🏾👇🏾👇🏾👇🏾

# from langchain_groq import ChatGroq
# from dotenv import load_dotenv

# load_dotenv()

# llm = ChatGroq(
#     model="llama-3.1-8b-instant"
# )

# while True:
#     user_input = input("You: ")

#     if user_input.lower() == "exit":
#         print("Bye 👋")
#         break

#     response = llm.invoke(user_input)

#     print("AI:", response.content)

