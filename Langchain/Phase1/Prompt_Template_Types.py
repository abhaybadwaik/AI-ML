"""
Phase 1 · Lesson 2 — Zero Shot, One Shot, Few Shot Prompting
Real-world scenario: TechStore review classifier

WHAT WE ARE TRYING TO ACHIEVE:
Teach the LLM how to classify customer reviews as positive/negative/neutral.
We will see how adding examples changes the quality and consistency of replies.

Zero Shot → no examples, LLM uses its own knowledge
One Shot  → one example, LLM understands your pattern
Few Shot  → multiple examples, LLM gives most consistent results
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=100)

# test reviews we will classify
reviews = [
    "This laptop is absolutely amazing, best purchase ever!",
    "Worst product I have ever bought, completely useless.",
    "It is okay, nothing special about it.",
]


# ── 1. Zero Shot ──────────────────────────────────────────────
# No examples given — LLM uses its own training knowledge
# Use when: task is simple and LLM already knows what to do
# Problem: LLM may reply in different formats each time

zero_shot_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a review classifier for TechStore.
Classify the review as positive, negative, or neutral.
Reply in this exact format: Classification: <result>"""),
    ("human", "Review: {review}"),
])

print("=== Zero Shot ===")
print("No examples given — LLM uses its own knowledge")
print()

for review in reviews:
    filled = zero_shot_prompt.invoke({"review": review})
    response = llm.invoke(filled)
    print(f"Review    : {review}")
    print(f"Result    : {response.content}")
    print()


# ── 2. One Shot ───────────────────────────────────────────────
# One example given — LLM understands your pattern
# Use when: you want a specific format or style in the reply
# Better than zero shot — LLM now knows exactly what you expect

one_shot_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a review classifier for TechStore.
Classify the review as positive, negative, or neutral.

Here is one example to understand the pattern:
Review: "The delivery was super fast and product quality is great!"
Classification: positive
Reason: customer is happy with delivery and quality

Now classify the review in the exact same format."""),
    ("human", "Review: {review}"),
])

print("=== One Shot ===")
print("One example given — LLM understands your pattern")
print()

for review in reviews:
    filled = one_shot_prompt.invoke({"review": review})
    response = llm.invoke(filled)
    print(f"Review    : {review}")
    print(f"Result    : {response.content}")
    print()


# ── 3. Few Shot ───────────────────────────────────────────────
# Multiple examples given — most consistent and accurate results
# Use when: you need very specific format and high accuracy
# Best for: classification, data extraction, structured output tasks

few_shot_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a review classifier for TechStore.
Classify the review as positive, negative, or neutral.
Always reply in this exact format:
Classification: <result>
Reason: <one line reason>

Here are examples to understand the pattern:

Example 1:
Review: "The delivery was super fast and product quality is great!"
Classification: positive
Reason: customer is happy with delivery and quality

Example 2:
Review: "Completely broken on arrival, waste of money!"
Classification: negative
Reason: customer received damaged product and lost money

Example 3:
Review: "Product is fine, nothing extraordinary about it."
Classification: neutral
Reason: customer has no strong feelings, neither happy nor unhappy

Now classify the review in the exact same format."""),
    ("human", "Review: {review}"),
])

print("=== Few Shot ===")
print("Multiple examples given — most consistent and accurate results")
print()

for review in reviews:
    filled = few_shot_prompt.invoke({"review": review})
    response = llm.invoke(filled)
    print(f"Review    : {review}")
    print(f"Result    : {response.content}")
    print()


# ── Key Observations ──────────────────────────────────────────
print("=== What to observe in output ===")
print("""
Zero Shot  → LLM may reply in different formats, less consistent
One Shot   → LLM starts following your format pattern
Few Shot   → LLM replies in exact same format every time, most accurate

Real world rule:
  Simple tasks          → Zero Shot
  Need specific format  → One Shot
  Need high accuracy    → Few Shot
  Production classifier → Always Few Shot
""")

# template has a blank slot — MessagesPlaceholder fills it dynamically
messages_placeholder_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a support agent for {store_name}."),
    MessagesPlaceholder("chat_history"),  # ← blank slot for dynamic history
    ("human", "{input}"),                 # ← latest customer message
])

# this is the growing conversation history
# in real projects this keeps getting longer as customer chats
chat_history = [
    HumanMessage(content="My laptop hasn't arrived."),
    AIMessage(content="Sorry to hear that! Can you share your order number?"),
    HumanMessage(content="It's ORDER-9821."),
    AIMessage(content="Let me check that for you."),
]

# fill template — history is passed dynamically, not hardcoded
filled = messages_placeholder_prompt.invoke({
    "store_name": "TechStore",
    "chat_history": chat_history,       # full dynamic history goes into placeholder
    "input": "Any update on my order?", # latest customer message
})

print("=== MessagesPlaceholder ===")
print("Most used pattern in real production chatbots")
print()
print("Messages passed to LLM:")
for msg in filled.messages:
    print(f"  {msg.type}: {msg.content}")
print()

response = llm.invoke(filled)
print(f"Bot: {response.content}")
print()
print("""
Key difference from hardcoded System+Human+AI template:
  Hardcoded  → AI replies fixed in template, cant grow
  Placeholder → history passed dynamically, grows with conversation
  
This is the foundation of Lesson 5 Memory — 
Memory classes automatically manage this chat_history list for you.
""")