import os
from dotenv import load_dotenv
from groq import Groq
from langfuse import get_client, observe, propagate_attributes

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
langfuse = get_client()

@observe(name="filter-demo")
def chat(question, user_id, session_id, tags):
    with propagate_attributes(
        user_id=user_id,
        session_id=session_id,
        tags=tags,
        metadata={"environment": "production"}
    ):
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": question}]
        )
        answer = response.choices[0].message.content

        langfuse.create_score(
            trace_id=langfuse.get_current_trace_id(),
            name="quality",
            value=1 if len(answer) > 100 else 0,
            data_type="NUMERIC",
            comment="Auto scored"
        )
        return answer

# Different users, sessions, tags
chat("What is AI?",          user_id="abhay-123",  session_id="session-001", tags=["production"])
chat("What is ML?",          user_id="abhay-123",  session_id="session-001", tags=["production"])
chat("What is LangChain?",   user_id="rahul-456",  session_id="session-002", tags=["development"])
chat("What is Langfuse?",    user_id="rahul-456",  session_id="session-002", tags=["development"])
chat("What is Docker?",      user_id="priya-789",  session_id="session-003", tags=["production"])

langfuse.flush()
print("✅ Done! Now go check Langfuse dashboard!")