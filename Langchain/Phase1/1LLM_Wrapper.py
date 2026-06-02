# uv run python Phase1/LLM_Wrapper.py
"""
Phase 1 · Lesson 1 — LLM Wrappers
Real-world scenario: Customer Support Chatbot for TechStore
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq                          # LLM WRAPPER — imports ChatGroq wrapper class
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# STEP 1 — loads .env file and puts GROQ_API_KEY into RAM
load_dotenv()


# STEP 2 — creates LLM config object in RAM (NO API call yet)
# LLM WRAPPER — ChatGroq wraps Groq's API behind a standard interface
llm1 = ChatGroq(
    model="llama-3.1-8b-instant",   # fast cheap model for simple questions
    temperature=0,                   # 0 = consistent replies, no creativity
    max_tokens=300,                  # max length of reply
)

# LLM WRAPPER — second LLM object, completely separate from llm1, no conflict
llm2 = ChatGroq(
    model="llama-3.3-70b-versatile", # slow powerful model for complex questions
    temperature=0.7,                  # 0.7 = slightly creative
    max_tokens=300,
)


# STEP 3 — setting the protocol/persona for AI using SystemMessage
# think of this as rules given to a new employee before talking to customers
system = SystemMessage(content="""
You are a helpful customer support agent for TechStore.
Help customers with orders, returns, and product questions.
Always ask for an order number if needed.
""")


# ── Single turn conversation ──────────────────────────────────
print("=== Single Turn ===")

customer_msg = HumanMessage(content="Hi, my laptop hasn't arrived and it's been 10 days.")

# STEP 4 — THIS is where actual API call happens
# LLM WRAPPER — .invoke() converts messages to JSON, sends HTTP request to Groq,
#               gets JSON back, converts it to AIMessage object
response = llm1.invoke([system, customer_msg])

# response is AIMessage object (the box) — .content is the text inside (the pizza)
print("Customer:", customer_msg.content)
print("Bot     :", response.content)
print()


# ── Multi turn conversation ───────────────────────────────────
print("=== Multi Turn ===")

# full conversation list — we maintain this manually
# whichever LLM we call, we ALWAYS pass the full list — never just the last message
conversation = [
    system,
    HumanMessage(content="Hi, my laptop hasn't arrived and it's been 10 days."),
    AIMessage(content="Sorry to hear that! Can you share your order number?"),  # previous bot reply
    HumanMessage(content="It's ORDER-9821. I need it urgently for work."),
]

# passing full conversation to llm2 — llm2 sees complete history, no conflict
response = llm2.invoke(conversation)

for msg in conversation[1:]:
    role = "Customer" if isinstance(msg, HumanMessage) else "Bot"
    print(f"{role}: {msg.content}")
print(f"Bot: {response.content}")
print()


# ── invoke() vs stream() ─────────────────────────────────────
messages = [system, HumanMessage(content="What is your laptop return policy?")]

print("=== invoke() — full response at once ===")
# LLM WRAPPER — sends request, waits for full response, returns AIMessage
response = llm1.invoke(messages)
print("Bot:", response.content)
print()

print("=== stream() — token by token ===")
# LLM WRAPPER — sends request, yields tokens one by one as they arrive
# good for chat UIs — user sees words appear instead of waiting
print("Bot: ", end="", flush=True)
for chunk in llm1.stream(messages):
    print(chunk.content, end="", flush=True)
print("\n")


# ── Response object ──────────────────────────────────────────
print("=== Response Object ===")

response = llm1.invoke([system, HumanMessage(content="Do you sell warranties?")])

# LLM WRAPPER — converted Groq's raw JSON into this clean AIMessage object
print("response.content           →", response.content)         # the actual text
print("type(response)             →", type(response).__name__)  # AIMessage, not string
print("response.response_metadata →", response.response_metadata) # tokens, timing, model


# ── Two LLMs, same conversation, no conflict ─────────────────
print("\n=== Two LLMs, No Conflict ===")

def handle_query(llm, query: str, label: str):
    messages = [
        system,
        HumanMessage(content=query),
    ]
    # LLM WRAPPER — same .invoke() call works for any LLM wrapper
    response = llm.invoke(messages)
    print(f"{label}: {response.content}")
    print()

query = "Can I return a defective laptop after 45 days?"

# same function, two different LLMs — no conflict because each is independent object in RAM
handle_query(llm1, query, "Llama 8B  (llm1)")
handle_query(llm2, query, "Llama 70B (llm2)")