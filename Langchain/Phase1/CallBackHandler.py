"""
Phase 1 · Lesson 6 — Callbacks & Tracing
Real-world scenario: TechStore support bot with full visibility

WHAT WE ARE TRYING TO ACHIEVE:
Right now we only see final output.
Callbacks let us see everything happening inside the chain:
- When chain starts and ends
- What prompt was sent to LLM
- How many tokens were used
- How long it took
- When errors happen

Think of callbacks as CCTV cameras inside your chain.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from typing import Any, Dict, List
import time

load_dotenv()


# ── 1. StdOutCallbackHandler ──────────────────────────────────
# Built-in callback — prints everything to terminal automatically
# Use when: debugging, development, seeing what's happening inside chain

print("=== StdOutCallbackHandler ===")
print("Built-in callback — prints everything automatically")
print()

llm_with_callback = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=100,
    callbacks=[StdOutCallbackHandler()],  # attach callback to LLM
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a TechStore support agent. Be concise."),
    ("human", "{input}"),
])

chain = prompt | llm_with_callback | StrOutputParser()

response = chain.invoke({"input": "What is your return policy?"})
print()
print("Final response:", response)
print()


# ── 2. Custom Callback ────────────────────────────────────────
# Write your own callback to log anything you want
# Real world: log to file, database, monitoring system, alert on error

class TechStoreChatCallback(BaseCallbackHandler):
    """
    Custom callback for TechStore support bot.
    Logs timing, token usage, and errors.
    Real world: you would send these to your monitoring system.
    """

    def __init__(self):
        self.start_time = None

    def on_llm_start(self, serialized: Dict, prompts: List, **kwargs):
        """Fires when LLM receives the prompt"""
        self.start_time = time.time()
        print(f"🚀 LLM Started  — prompt length: {len(prompts[0])} chars")

    def on_llm_end(self, response: LLMResult, **kwargs):
        """Fires when LLM finishes responding"""
        elapsed = time.time() - self.start_time
        # get token usage from response
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            print(f"✅ LLM Finished — time: {elapsed:.2f}s")
            print(f"   Tokens used  — prompt: {usage.get('prompt_tokens', 'N/A')} | completion: {usage.get('completion_tokens', 'N/A')} | total: {usage.get('total_tokens', 'N/A')}")

    def on_llm_error(self, error: Exception, **kwargs):
        """Fires when LLM throws an error"""
        print(f"❌ LLM Error — {str(error)}")
        # real world: send alert to your team here

    def on_chain_start(self, serialized: Dict, inputs: Dict, **kwargs):
        """Fires when chain starts"""
        print(f"⛓️  Chain Started — input: {str(inputs)[:50]}...")

    def on_chain_end(self, outputs: Dict, **kwargs):
        """Fires when chain finishes"""
        print(f"⛓️  Chain Ended  — output: {str(outputs)[:50]}...")


print("=== Custom Callback ===")
print("Logs timing, tokens, and chain events")
print()

custom_callback = TechStoreChatCallback()

llm_custom = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=100,
    callbacks=[custom_callback],
)

chain_custom = prompt | llm_custom | StrOutputParser()

response = chain_custom.invoke({"input": "Do you sell warranties?"})
print()
print("Final response:", response)
print()


# ── 3. Multiple Callbacks ─────────────────────────────────────
# Attach multiple callbacks at once
# Real world: one for logging, one for monitoring, one for alerting

class SimpleLogCallback(BaseCallbackHandler):
    """Simple logger — just prints start and end"""

    def on_llm_start(self, serialized: Dict, prompts: List, **kwargs):
        print("📝 Logger: LLM call started")

    def on_llm_end(self, response: LLMResult, **kwargs):
        print("📝 Logger: LLM call completed")


print("=== Multiple Callbacks ===")
print("Two callbacks attached — both fire on same events")
print()

llm_multi = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=100,
    callbacks=[
        custom_callback,      # timing + tokens
        SimpleLogCallback(),  # simple logger
    ],
)

chain_multi = prompt | llm_multi | StrOutputParser()
response = chain_multi.invoke({"input": "How do I track my order?"})
print()
print("Final response:", response)
print()


# ── 4. Passing callbacks at invoke time ───────────────────────
# Instead of attaching to LLM, pass at invoke time
# Real world: different callbacks for different requests

print("=== Callbacks at Invoke Time ===")
print("Pass callbacks per request, not per LLM")
print()

llm_plain = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=100,
)

chain_plain = prompt | llm_plain | StrOutputParser()

# pass callback only for this specific invoke call
response = chain_plain.invoke(
    {"input": "What laptop brands do you sell?"},
    config={"callbacks": [custom_callback]}   # callback passed here
)
print()
print("Final response:", response)
print()

print("""
=== Summary ===
StdOutCallbackHandler → built-in, prints everything, use for debugging
Custom Callback       → extend BaseCallbackHandler, override event methods
Multiple Callbacks    → attach as many as you need, all fire on same events
Invoke-time Callbacks → pass via config, different callbacks per request

Key events:
  on_chain_start  → chain begins
  on_chain_end    → chain finishes
  on_llm_start    → prompt sent to LLM
  on_llm_end      → LLM reply received, token usage available
  on_llm_error    → something went wrong
  
Real world use:
  Development  → StdOutCallbackHandler for debugging
  Production   → Custom callback to log tokens, timing, errors to your system
""")