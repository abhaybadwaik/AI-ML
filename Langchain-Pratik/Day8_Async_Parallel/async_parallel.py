import asyncio
import time
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# -----------------------------
# 1. LLM
# -----------------------------
chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"   # 
)

# -----------------------------
# 2. Prompt
# -----------------------------
prompt = ChatPromptTemplate.from_template(
    "Answer this question clearly:\n{question}"
)

# -----------------------------
# 3. Chain (VERY IMPORTANT)
# -----------------------------
chain = prompt | chat | StrOutputParser()

# -----------------------------
# 4. Async function
# -----------------------------
async def ask_question(question, question_num):
    response = await chain.ainvoke({"question": question})
    return question_num, question, response

# -----------------------------
# 5. Runner
# -----------------------------
async def run_parallel():
    questions = [
        "What is machine learning?",
        "What is the capital of Japan?",
        "Who invented the telephone?",
        "What is photosynthesis?",
        "What is the speed of light?"
    ]

    print("=== SEQUENTIAL (one by one) ===")
    start = time.time()

    for i, q in enumerate(questions):
        response = chain.invoke({"question": q})
        print(f"Q{i+1}: {q}")
        print(f"A{i+1}: {response}")
        print()

    sequential_time = time.time() - start
    print(f"Sequential time: {sequential_time:.2f} seconds\n")

    print("=== PARALLEL (all at once) ===")
    start = time.time()

    tasks = [ask_question(q, i+1) for i, q in enumerate(questions)]
    results = await asyncio.gather(*tasks)

    for question_num, question, response in results:
        print(f"Q{question_num}: {question}")
        print(f"A{question_num}: {response}")
        print()

    parallel_time = time.time() - start
    print(f"Parallel time: {parallel_time:.2f} seconds")
    print(f"Time saved: {sequential_time - parallel_time:.2f} seconds")

# -----------------------------
# 6. Run
# -----------------------------
asyncio.run(run_parallel())