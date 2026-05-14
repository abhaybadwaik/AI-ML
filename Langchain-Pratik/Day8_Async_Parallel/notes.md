# Day 8 — Async & Parallel LLM Calls

## What is the concept?
**Async (Asynchronous)** programming allows your code to run multiple tasks at the same time without waiting for each one to finish before starting the next.  
**Parallel LLM calls** = sending multiple questions to the AI simultaneously instead of one at a time.

## Why do we use it?
Each LLM call takes 1–3 seconds. If you have 5 questions:
- **Sequential**: 5 × 2 seconds = **10 seconds total** ❌
- **Parallel (async)**: All 5 start at once = **~2 seconds total** ✅

This is a massive performance improvement for any application that makes multiple LLM calls.

## Real-Life Use Cases
- Generating multiple product descriptions simultaneously
- Running 10 customer queries at the same time in a support system
- Batch translating documents into multiple languages at once
- Evaluating multiple AI model responses in parallel
- Your example: answering 5 different questions simultaneously

---

## From your code (`async_parallel.py`)

### Setup
```python
import asyncio
import time
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

chat = ChatGroq(model="llama-3.1-8b-instant", api_key="...")
chain = prompt | chat | StrOutputParser()
```

### Async Function
```python
async def ask_question(question, question_num):
    # ainvoke() is the async version of invoke()
    response = await chain.ainvoke({"question": question})
    return question_num, question, response
```

> `ainvoke()` = async version of `invoke()` — never blocks the program

### Sequential vs Parallel — Side by Side
```python
async def run_parallel():
    questions = [
        "What is machine learning?",
        "What is the capital of Japan?",
        "Who invented the telephone?",
        "What is photosynthesis?",
        "What is the speed of light?"
    ]

    # === SEQUENTIAL (one by one) ===
    start = time.time()
    for i, q in enumerate(questions):
        response = chain.invoke({"question": q})   # blocks until done
        print(f"Q{i+1}: {q}\nA: {response}\n")
    print(f"Sequential time: {time.time() - start:.2f} seconds")
    # Example output: Sequential time: 8.43 seconds

    # === PARALLEL (all at once) ===
    start = time.time()
    tasks = [ask_question(q, i+1) for i, q in enumerate(questions)]
    results = await asyncio.gather(*tasks)   # runs all tasks simultaneously
    for num, question, response in results:
        print(f"Q{num}: {question}\nA: {response}\n")
    print(f"Parallel time: {time.time() - start:.2f} seconds")
    # Example output: Parallel time: 1.87 seconds  ← much faster!

asyncio.run(run_parallel())
```

---

## Key Concepts Explained

### `async def` — Define an async function
```python
async def my_function():
    ...
```
An async function can be paused (while waiting for a response) and resumed later, allowing other tasks to run in the meantime.

### `await` — Wait for a single async task
```python
response = await chain.ainvoke({"question": "..."})
```
Pauses this function until the AI responds, but lets OTHER async tasks run while waiting.

### `asyncio.gather()` — Run all tasks simultaneously
```python
results = await asyncio.gather(*tasks)
```
Fires all tasks at once. Waits for ALL of them to finish. Returns results in order.

### `asyncio.run()` — Entry point
```python
asyncio.run(run_parallel())
```
Starts the async event loop — required to run async code from normal Python.

---

## Sync vs Async Methods in LangChain

| Use case | Sync method | Async method |
|----------|-------------|--------------|
| Single call | `chain.invoke()` | `await chain.ainvoke()` |
| Streaming | `chain.stream()` | `chain.astream()` |
| Batch | `chain.batch()` | `await chain.abatch()` |

---

## Important Keywords
| Keyword | Meaning |
|---------|---------|
| `async def` | Declares an asynchronous function |
| `await` | Waits for an async operation to complete |
| `asyncio.gather()` | Runs multiple async tasks simultaneously |
| `asyncio.run()` | Starts the async event loop |
| `ainvoke()` | Async version of `invoke()` — non-blocking |
| `astream()` | Async version of `stream()` |
| `task` | A unit of work that can run concurrently |
| `event loop` | The engine that manages and schedules async tasks |
| Sequential | One at a time (blocking) |
| Parallel | All at once (non-blocking) |

---

## Beginner-Friendly Summary
Imagine you're a waiter at a restaurant:

**Sequential (sync)** = Take order from Table 1 → wait at kitchen until food is ready → bring food → then go to Table 2  
→ Tables 2, 3, 4, 5 all waiting. Very slow! ❌

**Parallel (async)** = Take order from Table 1 → give it to kitchen → go to Table 2 → give order → go to Table 3...  
→ All kitchens cooking at once → bring all food when ready  
→ Everyone served much faster! ✅

The `await` keyword = "I'm going to wait for this order, but go handle other tables in the meantime."  
`asyncio.gather()` = "Start ALL orders at once, come back when they're all done."
