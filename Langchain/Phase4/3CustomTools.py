"""
Phase 4 · Lesson 3 — Custom Tools
Building real world tools for agents

WHAT WE ARE TRYING TO ACHIEVE:
Lessons 1-2 used fake hardcoded tools.
Real projects need tools that connect to actual APIs, databases, RAG pipelines.
This lesson builds three production-ready custom tools.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import json
from ddgs import DDGS

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=500)


# ── Setup RAG pipeline for Tool 2 ────────────────────────────
print("Setting up RAG pipeline...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
faiss_store = FAISS.load_local(
    "Phase2/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
retriever = faiss_store.as_retriever(search_kwargs={"k": 3})
print("✅ RAG ready!")
print()


# ── Tool 1: Web Search ────────────────────────────────────────
# Real tool — searches DuckDuckGo for current information
# Use when: user asks about current events, news, latest info

@tool
def web_search(query: str) -> str:
    """Search the web for current information about any topic.
    Use this for recent news, current events, or any info not in documents.
    Input: search query string"""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "No results found"
            formatted = []
            for r in results:
                formatted.append(f"Title: {r['title']}\nSummary: {r['body'][:200]}")
            return "\n\n".join(formatted)
    except Exception as e:
        return f"Search error: {str(e)}"


# ── Tool 2: RAG Document Search ───────────────────────────────
# Searches your MBA project PDF
# Use when: user asks about the research document

@tool
def search_document(question: str) -> str:
    """Search the UPI research document for specific information.
    Use this when user asks about the MBA project, UPI study, research methodology,
    sample size, hypotheses, objectives, or any document specific information.
    Input: question about the document"""
    docs = retriever.invoke(question)
    if not docs:
        return "No relevant information found in document"

    results = []
    for doc in docs:
        page = doc.metadata.get('page', 'N/A')
        results.append(f"[Page {page}]: {doc.page_content[:300]}")
    return "\n\n".join(results)


# ── Tool 3: Data Analyzer ─────────────────────────────────────
# Analyzes lists of numbers — average, max, min, percentage
# Use when: user asks to analyze data or calculate statistics

@tool
def analyze_data(data_json: str) -> str:
    """Analyze a list of numbers and return statistics.
    Use this when user wants to analyze data, calculate averages, find trends.
    Input: JSON string with 'numbers' key, e.g. '{"numbers": [10, 20, 30, 40]}'"""
    try:
        data = json.loads(data_json)
        numbers = data["numbers"]

        total   = sum(numbers)
        average = total / len(numbers)
        maximum = max(numbers)
        minimum = min(numbers)
        growth  = ((numbers[-1] - numbers[0]) / numbers[0]) * 100

        return f"""Analysis Results:
Count   : {len(numbers)} data points
Total   : {total}
Average : {average:.2f}
Maximum : {maximum}
Minimum : {minimum}
Growth  : {growth:.1f}% from first to last value"""
    except Exception as e:
        return f"Analysis error: {str(e)}"


# ── Bind all tools ────────────────────────────────────────────
tools = [web_search, search_document, analyze_data]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

print("=== Custom Tools Ready ===")
for t in tools:
    print(f"  {t.name}: {t.description[:70]}...")
print()


# ── ReAct loop ────────────────────────────────────────────────
def react_agent(question: str, max_steps: int = 5) -> str:
    print(f"\nQuestion: {question}")
    print("="*55)

    messages = [HumanMessage(content=question)]
    step = 0

    while step < max_steps:
        step += 1
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            print(f"Final Answer: {response.content}")
            return response.content

        for tool_call in response.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]
            print(f"[Step {step}] {name}({args})")
            result = tool_map[name].invoke(args)
            print(f"Result: {result[:150]}...")
            messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))

    return "Max steps reached"


# ── Run examples ──────────────────────────────────────────────
print("="*55)
print("=== Testing Custom Tools ===")
print("="*55)

# Tool 2 — RAG search
react_agent("What is the sample size and research methodology in the UPI study?")

# Tool 3 — Data analysis
react_agent("Analyze this UPI growth data: 92, 500, 1800, 5000, 8900, 17221 crore transactions")

# Tool 1 + Tool 2 — combining web search and document
react_agent("What does the UPI study say about digital payment barriers?")

print("""
=== Summary ===
Custom tools connect agents to real world:
  web_search     → live internet search via DuckDuckGo
  search_document → queries your RAG pipeline
  analyze_data   → calculates statistics from numbers

Key point:
  Any Python function can become a tool with @tool decorator
  Docstring tells LLM WHEN to use the tool
  Tool output goes back to LLM as Observation
  LLM decides next step based on observation
""")