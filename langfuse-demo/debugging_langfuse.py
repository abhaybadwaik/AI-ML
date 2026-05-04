import os
from dotenv import load_dotenv
from groq import Groq
from langfuse import get_client, observe, propagate_attributes

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
langfuse = get_client()

@observe(name="chatbot-debug")
def chat(user_message: str, user_id: str, model: str):
    with propagate_attributes(
        user_id=user_id,
        session_id="debug-session-001",
        tags=["debug", "production"],
        metadata={"environment": "production"}
    ):
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": user_message}]
            )
            answer = response.choices[0].message.content
            print(f"✅ [{user_id}] Success!")

            trace_id = langfuse.get_current_trace_id()
            langfuse.create_score(
                trace_id=trace_id,
                name="status",
                value=1,
                data_type="NUMERIC",
                comment="Call succeeded"
            )
            return answer

        except Exception as e:
            print(f"❌ [{user_id}] Failed: {e}")

            trace_id = langfuse.get_current_trace_id()
            langfuse.create_score(
                trace_id=trace_id,
                name="status",
                value=0,
                data_type="NUMERIC",
                comment=f"FAILED: {str(e)}"
            )
            return None

# ✅ Good call
chat("What is LangChain?", user_id="user-001", model="llama-3.3-70b-versatile")

# ❌ Bad call — wrong model
chat("What is LangChain?", user_id="user-002", model="FAKE-MODEL")

langfuse.flush()
print("\n✅ Now check Langfuse dashboard!")