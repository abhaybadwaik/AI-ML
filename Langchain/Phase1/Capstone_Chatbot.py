"""
Phase 1 — Capstone: Stateful Multi-turn CLI Chatbot
TechStore Support Bot

Uses everything from Phase 1:
✅ LLM Wrapper      — ChatGroq
✅ Prompt Template  — ChatPromptTemplate + MessagesPlaceholder  
✅ LCEL             — pipe operator chain
✅ Output Parser    — StrOutputParser
✅ Memory           — ChatMessageHistory
✅ Callbacks        — Custom callback for token logging
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_community.chat_message_histories import ChatMessageHistory
from typing import Any, Dict, List
import time

load_dotenv()


# ── Custom Callback ───────────────────────────────────────────
class SupportBotCallback(BaseCallbackHandler):
    """Logs token usage and response time for every message"""

    def __init__(self):
        self.start_time = None
        self.total_tokens = 0

    def on_llm_start(self, serialized: Dict, prompts: List, **kwargs):
        self.start_time = time.time()

    def on_llm_end(self, response: LLMResult, **kwargs):
        elapsed = time.time() - self.start_time
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            tokens = usage.get("total_tokens", 0)
            self.total_tokens += tokens
            print(f"\n📊 [{elapsed:.2f}s | tokens: {tokens} | total used: {self.total_tokens}]")

    def on_llm_error(self, error: Exception, **kwargs):
        print(f"\n❌ Error: {str(error)}")


# ── LLM Setup ─────────────────────────────────────────────────
callback = SupportBotCallback()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=300,
    callbacks=[callback],
)


# ── Prompt Template ───────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful customer support agent for TechStore.
You help customers with orders, returns, and product questions.
Always be polite and professional.
Always ask for order number if customer has a complaint.
If you don't know something, say so honestly.
If customer asks anything not related to TechStore — say 'I can only help with TechStore related questions.'"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])


# ── Chain ─────────────────────────────────────────────────────
chain = prompt | llm | StrOutputParser()


# ── Memory ────────────────────────────────────────────────────
history = ChatMessageHistory()


# ── Chat Function ─────────────────────────────────────────────
def chat(user_input: str) -> str:
    """Send message and get response with full memory"""

    response = chain.invoke({
        "input": user_input,
        "chat_history": history.messages,
    })

    # save to memory automatically
    history.add_user_message(user_input)
    history.add_ai_message(response)

    return response


# ── CLI Loop ──────────────────────────────────────────────────
def main():
    print("="*60)
    print("  TechStore Support Bot — Phase 1 Capstone")
    print("="*60)
    print("Type your message and press Enter.")
    print("Type 'quit' to exit | 'history' to see conversation | 'clear' to reset")
    print("="*60)
    print()

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        elif user_input.lower() == "quit":
            print(f"\nGoodbye! Total tokens used this session: {callback.total_tokens}")
            break

        elif user_input.lower() == "history":
            print("\n--- Conversation History ---")
            if not history.messages:
                print("No messages yet.")
            for msg in history.messages:
                role = "You" if msg.type == "human" else "Bot"
                print(f"{role}: {msg.content[:80]}...")
            print("----------------------------\n")
            continue

        elif user_input.lower() == "clear":
            history.clear()
            print("\n🗑️  Conversation cleared!\n")
            continue

        # get response
        response = chat(user_input)
        print(f"\nBot: {response}\n")


if __name__ == "__main__":
    main()