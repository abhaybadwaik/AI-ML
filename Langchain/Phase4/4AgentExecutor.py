"""
Phase 4 · Lesson 4 — AgentExecutor
LangChain's built-in agent runner — replaces manual ReAct loop

WHAT WE ARE TRYING TO ACHIEVE:
Lessons 2-3 → manual ReAct loop, no error handling, messy code
AgentExecutor → built-in loop, error handling, memory, streaming
Same result — much cleaner code
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
import json
import os

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=500)


# ── Setup RAG ─────────────────────────────────────────────────
print("Setting up...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
faiss_store = FAISS.load_local(
    "Phase2/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
retriever = faiss_store.as_retriever(search_kwargs={"k": 3})
print("✅ Ready!")
print()


# ── Tools ─────────────────────────────────────────────────────
@tool
def search_document(question: str) -> str:
    """Search the UPI research document for specific information.
    Use for questions about the MBA project, sample size, methodology, hypotheses."""
    docs = retriever.invoke(question)
    results = []
    for doc in docs:
        page = doc.metadata.get('page', 'N/A')
        results.append(f"[Page {page}]: {doc.page_content[:300]}")
    return "\n\n".join(results)


@tool
def calculate(expression: str) -> str:
    """Perform math calculations. Pass only the math expression.
    Example: '150 * 0.15' or '83 / 50'"""
    try:
        expression = expression.strip().strip("{}")
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


@tool
def analyze_data(data_json: str) -> str:
    """Analyze a list of numbers. Input must be JSON with 'numbers' key.
    Example: '{"numbers": [92, 500, 1800, 5000]}'"""
    try:
        data = json.loads(data_json)
        numbers = data["numbers"]
        total   = sum(numbers)
        average = total / len(numbers)
        growth  = ((numbers[-1] - numbers[0]) / numbers[0]) * 100
        return f"Count: {len(numbers)}, Total: {total}, Average: {average:.2f}, Growth: {growth:.1f}%"
    except Exception as e:
        return f"Error: {e}"


tools = [search_document, calculate, analyze_data]


# ── 1. Create Agent with AgentExecutor ────────────────────────
# create_tool_calling_agent → creates the agent brain
# AgentExecutor             → runs the ReAct loop automatically

print("=== AgentExecutor — Basic Usage ===")

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful research assistant with access to tools.
Use tools to find accurate information. Be concise in your final answers."""),
    MessagesPlaceholder("chat_history"),   # for memory
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),  # required for AgentExecutor
])

# create agent
agent = create_tool_calling_agent(llm, tools, prompt)

# create executor — this is what you actually run
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,          # shows ReAct steps automatically
    max_iterations=5,      # max tool calls before stopping
    handle_parsing_errors=True,  # handles LLM formatting errors gracefully
)

# run — much simpler than manual loop!
result = agent_executor.invoke({
    "input": "What is the sample size of the UPI study?",
    "chat_history": [],
})
print(f"\nFinal Answer: {result['output']}")
print()


# ── 2. AgentExecutor with Memory ─────────────────────────────
# Add conversation memory so follow-up questions work

print("="*55)
print("=== AgentExecutor with Memory ===")
print("="*55)

history = ChatMessageHistory()

def chat_with_agent(question: str) -> str:
    result = agent_executor.invoke({
        "input": question,
        "chat_history": history.messages,
    })
    # save to memory
    history.add_user_message(question)
    history.add_ai_message(result["output"])
    return result["output"]

# multi-turn conversation
questions = [
    "What is the sample size of the UPI study?",
    "Why was this sample size chosen?",       # follow up
    "Calculate 15% of that sample size.",     # uses previous context + calculator
]

for q in questions:
    print(f"\nYou: {q}")
    answer = chat_with_agent(q)
    print(f"Agent: {answer}")
print()


# ── 3. Error handling ─────────────────────────────────────────
print("="*55)
print("=== Error Handling ===")
print("="*55)

# AgentExecutor handles errors gracefully with handle_parsing_errors=True
result = agent_executor.invoke({
    "input": "Calculate the square root of -1",  # will cause math error
    "chat_history": [],
})
print(f"Answer: {result['output']}")

print("""
=== Manual Loop vs AgentExecutor ===

Manual Loop (Lessons 2-3):
  ❌ Write while loop yourself
  ❌ Handle tool execution manually
  ❌ No error handling
  ❌ No built-in memory
  ❌ 50+ lines of boilerplate

AgentExecutor:
  ✅ Loop handled automatically
  ✅ Tool execution handled
  ✅ handle_parsing_errors=True
  ✅ Works with ChatMessageHistory
  ✅ 5 lines to set up

Use AgentExecutor in production always.
Use manual loop only to understand internals.
""")