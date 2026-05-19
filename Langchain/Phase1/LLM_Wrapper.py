"""
Phase 1 · Lesson 1 — LLM Wrappers
Real-world scenario: Customer Support Chatbot for TechStore
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()


# ── 1. Creating the LLM ───────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=300,
)


# ── 2. Message Types ──────────────────────────────────────────
system = SystemMessage(content="""
You are a helpful customer support agent for TechStore.
Help customers with orders, returns, and product questions.
Always ask for an order number if needed.
""")

customer_msg = HumanMessage(content="Hi, my laptop hasn't arrived and it's been 10 days.")

response = llm.invoke([system, customer_msg])

print("=== Basic Response ===")
print("Customer:", customer_msg.content)
print("Bot     :", response.content)
print()


# ── 3. Multi-turn Conversation ────────────────────────────────
conversation = [
    system,
    HumanMessage(content="Hi, my laptop hasn't arrived and it's been 10 days."),
    AIMessage(content="Sorry to hear that! Can you share your order number?"),
    HumanMessage(content="It's ORDER-9821. I need it urgently for work."),
]

response = llm.invoke(conversation)

print("=== Multi-turn ===")
for msg in conversation[1:]:
    role = "Customer" if isinstance(msg, HumanMessage) else "Bot"
    print(f"{role}: {msg.content}")
print(f"Bot: {response.content}")
print()


# ── 4. invoke() vs stream() ───────────────────────────────────
messages = [system, HumanMessage(content="What is your laptop return policy?")]

print("=== invoke() ===")
print("Bot:", llm.invoke(messages).content)
print()

print("=== stream() ===")
print("Bot: ", end="", flush=True)
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
print("\n")


# ── 5. Response Object ────────────────────────────────────────
response = llm.invoke([system, HumanMessage(content="Do you sell warranties?")])

print("=== Response Object ===")
print("response.content          →", response.content)
print("type(response)            →", type(response).__name__)
print("response.response_metadata→", response.response_metadata)
print()


# ── 6. Provider Swap ──────────────────────────────────────────
def handle_query(llm, query: str) -> str:
    messages = [
        SystemMessage(content="You are a TechStore support agent. Be concise."),
        HumanMessage(content=query),
    ]
    return llm.invoke(messages).content


query = "Can I return a defective laptop after 45 days?"

llama_small = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=100)
llama_large = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, max_tokens=100)

print("=== Provider Swap (Groq models) ===")
print("Llama 8B :", handle_query(llama_small, query))
print()
print("Llama 70B:", handle_query(llama_large, query))