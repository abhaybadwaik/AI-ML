"""
Phase 1 · Lesson 2 — Prompt Templates
Real-world scenario: Support bot that works for multiple stores

WHAT WE ARE TRYING TO ACHIEVE:
In Lesson 1 we hardcoded every message manually.
Problem — if store name, product, days keep changing we have to rewrite code every time.
Solution — Prompt Templates. Define structure once, fill different values each time.
Think of it like a WhatsApp business template:
"Dear {name}, your {product} will arrive by {date}." — same template, different data.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=300)


# ── 1. PromptTemplate ─────────────────────────────────────────
# Use when: you just need a simple plain string with variables
# Real world: generating email subject lines, simple text tasks
# HOW: define template with {variables}, invoke fills them in

prompt = PromptTemplate(
    template="You are a support agent for {store_name}. Customer says: {issue}. Reply politely in 2 lines.",
    input_variables=["store_name", "issue"]   # declare variables here
)

# .invoke() fills the variables — NO API call, just creates the string
filled_prompt = prompt.invoke({
    "store_name": "TechStore",
    "issue": "My laptop hasn't arrived in 10 days"
})

print("=== PromptTemplate ===")
print("Filled prompt:", filled_prompt.text)   # just a plain filled string
print()


# ── 2. ChatPromptTemplate ─────────────────────────────────────
# Use when: you need System + Human messages (90% of real projects)
# Real world: any chatbot, support bot, AI assistant
# HOW: define message structure once, fill variables each time

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a support agent for {store_name}. Always be polite and ask for order number if needed."),
    ("human", "Hi, my {product} hasn't arrived and it's been {days} days."),
])

# .invoke() fills variables and creates proper message list — still NO API call
filled_chat = chat_prompt.invoke({
    "store_name": "TechStore",
    "product": "laptop",
    "days": 10
})

print("=== ChatPromptTemplate ===")
print("Messages created:")
for msg in filled_chat.messages:
    print(f"  {msg.type}: {msg.content}")   # shows system and human messages
print()

# NOW the API call happens — send filled messages to LLM
response = llm.invoke(filled_chat)
print("Bot:", response.content)
print()


# ── 3. Reusability — same template, different stores ──────────
# THIS is the real power of Prompt Templates
# Real world: one bot serving 100 different stores
# HOW: loop through different data, same template fills each time

print("=== Same Template, Different Stores ===")

stores = [
    {"store_name": "TechStore",    "product": "laptop",  "days": 10},
    {"store_name": "FashionStore", "product": "jacket",  "days": 5},
    {"store_name": "FoodStore",    "product": "blender", "days": 3},
]

for store in stores:
    filled = chat_prompt.invoke(store)      # same template, different data
    response = llm.invoke(filled)           # API call for each store
    print(f"[{store['store_name']}] Bot: {response.content}")
    print()


# ── 4. Multi turn with template ───────────────────────────────
# Use when: you have a fixed conversation flow with variables
# Real world: onboarding flows, structured interviews, guided support
# HOW: include ai messages in template to simulate history

multi_turn_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a support agent for {store_name}."),
    ("human", "My {product} hasn't arrived."),
    ("ai", "Sorry to hear that! Can you share your order number?"),  # fixed bot reply in template
    ("human", "{followup}"),   # customer's next message is also a variable
])

filled = multi_turn_prompt.invoke({
    "store_name": "TechStore",
    "product": "laptop",
    "followup": "Sure, it's ORDER-9821. I need it urgently."
})

response = llm.invoke(filled)

print("=== Multi Turn with Template ===")
for msg in filled.messages:
    print(f"  {msg.type}: {msg.content}")
print(f"  Bot: {response.content}")

# SUMMARY OF WHAT WE ACHIEVED:
# Lesson 1 → hardcoded messages, works for one store only
# Lesson 2 → reusable templates, works for any store with zero code change
# Key rule → template defines STRUCTURE, invoke() fills the DATA