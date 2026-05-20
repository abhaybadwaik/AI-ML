"""
Phase 1 · Lesson 3 — LCEL & Runnables
Real-world scenario: TechStore support bot using chains

WHAT WE ARE TRYING TO ACHIEVE:
In Lesson 1 and 2 we called prompt.invoke() and llm.invoke() separately.
LCEL lets us connect them with | pipe operator into one chain.
Chain = assembly line. Each step passes output to next step automatically.

prompt | llm          → basic chain
prompt | llm | parser → chain with output parser
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=300)


# ── 1. Basic Chain — prompt | llm ────────────────────────────
# Lesson 1&2 way → 3 steps manually
# LCEL way       → 1 chain, 1 call
# Real world: any simple question answer bot

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a support agent for TechStore. Be concise."),
    ("human", "{input}"),
])

basic_chain = prompt | llm

response = basic_chain.invoke({"input": "What is your return policy?"})

print("=== Basic Chain (prompt | llm) ===")
print("Type of response:", type(response).__name__)
print("Bot:", response.content)
print()


# ── 2. Chain with StrOutputParser ────────────────────────────
# Problem → basic chain returns AIMessage, not plain string
# StrOutputParser → extracts .content automatically
# Real world: when you want clean string output

chain_with_parser = prompt | llm | StrOutputParser()

response = chain_with_parser.invoke({"input": "Do you sell warranties?"})

print("=== Chain with StrOutputParser ===")
print("Type of response:", type(response).__name__)
print("Bot:", response)
print()


# ── 3. RunnablePassthrough ────────────────────────────────────
# Passes original input through unchanged alongside chain output
# Real world: logging, debugging, keeping context forward in chain

chain_with_passthrough = RunnablePassthrough.assign(
    response = prompt | llm | StrOutputParser()
)

result = chain_with_passthrough.invoke({"input": "How do I track my order?"})

print("=== RunnablePassthrough ===")
print("Original input :", result["input"])
print("LLM response   :", result["response"])
print()


# ── 4. RunnableLambda ─────────────────────────────────────────
# Wraps any custom Python function into a Runnable
# So it can be used inside chain with | pipe
# Real world: preprocessing input, postprocessing output

def add_urgency(text: str) -> str:
    return f"[URGENT] {text}"

chain_with_lambda = prompt | llm | StrOutputParser() | RunnableLambda(add_urgency)

response = chain_with_lambda.invoke({"input": "My laptop is broken!"})

print("=== RunnableLambda ===")
print("Bot with custom function:", response)
print()


# ── 5. RunnableParallel ───────────────────────────────────────
# Runs multiple chains at the same time in parallel
# Real world: compare formal vs casual reply, A/B testing prompts

formal_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a formal professional support agent for TechStore."),
    ("human", "{input}"),
])

casual_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly casual support agent for TechStore. Use simple words."),
    ("human", "{input}"),
])

parallel_chain = RunnableParallel(
    formal = formal_prompt | llm | StrOutputParser(),
    casual = casual_prompt | llm | StrOutputParser(),
)

result = parallel_chain.invoke({"input": "My laptop hasn't arrived in 10 days."})

print("=== RunnableParallel ===")
print("Formal reply:", result["formal"])
print()
print("Casual reply:", result["casual"])
print()


# ── 6. Full Production Chain ──────────────────────────────────
# Everything combined — prompt | llm | parser with MessagesPlaceholder
# Real world: production ready support chatbot

support_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a support agent for {store_name}. Be polite and ask for order number if needed."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

support_chain = support_prompt | llm | StrOutputParser()

chat_history = [
    HumanMessage(content="My laptop hasn't arrived."),
    AIMessage(content="Sorry! Can you share your order number?"),
]

response = support_chain.invoke({
    "store_name": "TechStore",
    "chat_history": chat_history,
    "input": "It's ORDER-9821. Any update?"
})

print("=== Full Production Chain ===")
print("Bot:", response)
print()

print("""
=== Summary ===
| operator          → connects steps, output of one becomes input of next
StrOutputParser    → converts AIMessage to plain string automatically
RunnablePassthrough→ keeps original input alongside chain output
RunnableLambda     → plugs any Python function into the chain
RunnableParallel   → runs multiple chains simultaneously
""")