import os
from dotenv import load_dotenv
from groq import Groq
from langfuse import get_client, observe, propagate_attributes

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
langfuse = get_client()

# Simulating a real user session
USER_ID = "abhay-123"
SESSION_ID = "chat-session-001"

@observe(name="chatbot-response")
def chat(user_message: str):
    with propagate_attributes(
        user_id=USER_ID,
        session_id=SESSION_ID,
        tags=["chatbot", "production"],
        metadata={"environment": "production"}
    ):
        # Call Groq
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_message}]
        )
        answer = response.choices[0].message.content

        # Auto-score based on response length (simple quality check)
        quality_score = min(len(answer) / 500, 1.0)  # longer = better up to 1.0

        trace_id = langfuse.get_current_trace_id()
        langfuse.create_score(
            trace_id=trace_id,
            name="response-quality",
            value=round(quality_score, 2),
            data_type="NUMERIC",
            comment=f"Auto-scored based on response length"
        )

        return answer

# Chat loop
print("🤖 Chatbot started! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        print("Goodbye! Check your Langfuse dashboard 👋")
        break

    if not user_input:
        continue

    response = chat(user_input)
    print(f"\n🤖 Bot: {response}\n")
    print("-" * 50)

langfuse.flush()


# import os
# from dotenv import load_dotenv
# from groq import Groq
# from langfuse import get_client, observe, propagate_attributes

# load_dotenv()

# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# langfuse = get_client()

# @observe(name="ask-groq")
# def ask_groq(question: str):
#     with propagate_attributes(
#         user_id="abhay-123",
#         session_id="demo-session-001",
#         tags=["demo", "groq", "observability"],
#         metadata={"environment": "development", "topic": "AI"}
#     ):
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": question}]
#         )
#         answer = response.choices[0].message.content
#         print("Response:", answer)

#         # ⭐ Score using trace_id — the correct v4 way
#         trace_id = langfuse.get_current_trace_id()
#         langfuse.create_score(
#             trace_id=trace_id,
#             name="user-feedback",
#             value=1,
#             data_type="NUMERIC",
#             comment="User found this answer helpful!"
#         )

#         return answer

# ask_groq("What is RAG in AI?")

# langfuse.flush()
# print("\n✅ Check your Langfuse dashboard now!")
















# import os
# from dotenv import load_dotenv
# from groq import Groq
# from langfuse import get_client, observe, propagate_attributes

# # Load your .env file
# load_dotenv()

# # Setup clients
# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# langfuse = get_client()

# @observe(name="ask-groq")
# def ask_groq(question: str):
#     # propagate_attributes is the v4 way to attach user/session/tags
#     with propagate_attributes(
#         user_id="abhay-123",
#         session_id="demo-session-001",
#         tags=["demo", "groq", "observability"],
#         metadata={"environment": "development", "topic": "AI"}
#     ):
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": question}]
#         )
#         answer = response.choices[0].message.content
#         print("Response:", answer)
#         return answer

# # Run it!
# ask_groq("What is prompt engineering?")

# langfuse.flush()
# print("\n✅ Check your Langfuse dashboard now!")

# import os
# from dotenv import load_dotenv
# from groq import Groq
# from langfuse import get_client, observe

# # Load your .env file
# load_dotenv()

# # Setup Groq client
# groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# # Get Langfuse client (reads keys from .env automatically)
# langfuse = get_client()

# # The @observe decorator traces this function automatically
# @observe(name="ask-groq")
# def ask_groq(question: str):
#     response = groq_client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": question}]
#     )
#     answer = response.choices[0].message.content
#     print("Response:", answer)
#     return answer

# # Run it!
# ask_groq("What is observability in AI?")

# # Send data to Langfuse dashboard
# langfuse.flush()

# print("\n✅ Check your Langfuse dashboard now!")