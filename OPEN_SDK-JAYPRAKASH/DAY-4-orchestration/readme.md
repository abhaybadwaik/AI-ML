# Multi-Agent Systems: Agent-as-Tools vs Handoffs

A complete guide to two powerful patterns for building multi-agent AI systems using the OpenAI Agents SDK.

- 

## Pattern 1 — Agent-as-Tool (`agent_as_tools.py`)

### What It Does

The **orchestrator agent** (EmailRouter) acts as the central brain. Specialist agents are registered as **tools** — the orchestrator calls them like function calls and receives their output back, then decides what to return to the user.

### Architecture Diagram

```
User Input
    │
    ▼
┌─────────────────────┐
│   EmailRouter       │  ← Orchestrator (always in control)
│   (Orchestrator)    │
└──────┬──────────────┘
       │ calls one tool
  ┌────┴────┬──────────┐
  ▼         ▼          ▼
billing_  tech_     sales_
support   support   support
  │         │          │
  └────┬────┘──────────┘
       │ returns result to orchestrator
       ▼
  Final Response to User
```

### Code Walkthrough

**Step 1 — Create specialist agents**
```python
billing_agent = Agent(
    name="BillingAgent",
    model=model,
    instructions="You are a billing support expert. Handle refunds, payment failures..."
)
```
Each specialist is a fully functional agent with its own instructions and model.

**Step 2 — Register specialists as tools on the orchestrator**
```python
orchestrator = Agent(
    name="EmailRouter",
    tools=[
        billing_agent.as_tool(
            tool_name="billing_support",
            tool_description="Handles billing and refund issues"
        ),
        tech_agent.as_tool(...),
        sales_agent.as_tool(...),
    ],
)
```
The `.as_tool()` method wraps each agent so the orchestrator can invoke it like a function call.

**Step 3 — Run batch emails**
```python
async def main():
    emails = [
        "I was charged twice for my subscription",
        "What is the price of premium plan?"
    ]
    for email in emails:
        result = await Runner.run(orchestrator, input=email, max_turns=10)
        print("RESPONSE:", result.final_output)
```
Each email is processed independently. The orchestrator reads the email, picks the right tool, calls it, and returns the answer.

### Key Behaviors

- The orchestrator **always stays in control** — it receives the specialist's reply and may rephrase or augment it before responding to the user.
- The orchestrator can theoretically **call multiple tools** in sequence (though instructed to call only one here).
- The `max_turns=10` allows multi-step reasoning within a single run.
- Best for **pipelines where you want a single coordinating agent** to synthesize outputs.

---

## Pattern 2 — Handoff (`handsoff.py`)

### What It Does

The **router agent** reads the user message and **transfers full conversational control** to a specialist agent. Once handed off, the specialist handles the rest of the conversation directly — the router steps out entirely.

### Architecture Diagram

```
User Input
    │
    ▼
┌───────────────────────────┐
│  customer_support_router  │  ← Decides who should handle it
└───────────┬───────────────┘
            │ transfers control (handoff)
     ┌──────┼──────┐
     ▼      ▼      ▼
 billing_ tech_  order_
  agent   agent  agent
     │
     ▼
Final Response to User
     (router is no longer involved)
```

### Code Walkthrough

**Step 1 — Create specialist agents**
```python
billing_agent = Agent(
    name="billing_agent",
    model=model,
    instructions="You are a billing support specialist. Handle payment failures, refunds..."
)
```

**Step 2 — Register specialists as handoffs on the router**
```python
router_agent = Agent(
    name="customer_support_router",
    instructions="""
    Routing Rules:
    - payment/refund/billing → billing_agent
    - app/crash/technical → tech_support_agent
    - order/shipping/delivery → order_support_agent
    """,
    handoffs=[
        billing_agent,
        tech_support_agent,
        order_support_agent
    ]
)
```
Unlike `.as_tool()`, the `handoffs=` list tells the SDK these agents can **take over** the conversation.

**Step 3 — Interactive loop**
```python
async def main():
    while True:
        user_input = input("Ask: ")
        result = await Runner.run(router_agent, input=user_input)
        print("Response:", result.final_output)
```
Runs continuously until the user types `exit`. Each query is fully independent.

### Key Behaviors

- Once handed off, the **specialist agent is the one generating the final response** — the router has no further involvement.
- Control is **one-way**: router → specialist (no return path).
- Simpler mental model — the specialist just responds as if it were the only agent.
- Best for **isolated, self-contained tasks** where a specialist needs full ownership.

---

## Core Difference: Control Flow

```
Agent-as-Tool:
  User → Orchestrator → [calls tool] → Specialist → [returns result] → Orchestrator → User
                                                                               ↑
                                                              orchestrator can modify/enrich

Handoff:
  User → Router → [transfers control] → Specialist → User
                         ↑
                   router is done here
```

The orchestrator in `agent_as_tools.py` **wraps** the specialist's output. The router in `handsoff.py` **steps aside** and lets the specialist respond directly.

---

## Real-World Use Cases

### When to Use Agent-as-Tool

| Use Case | Why it fits |
|---|---|
| **Email triage with summaries** | Orchestrator can summarize specialist reply before sending |
| **Multi-department reports** | Call billing + tech + sales, then combine all outputs |
| **Quality gating** | Orchestrator reviews specialist reply before passing to user |
| **Audit/logging systems** | Central agent logs all sub-agent interactions |
| **Conditional escalation** | Orchestrator decides: "billing agent said X, now also call tech agent" |

**Example:** A support system where the orchestrator reads a complaint, calls the billing agent, and if the billing agent says "this is actually a technical issue," the orchestrator then calls the tech agent — all transparently to the user.

### When to Use Handoff

| Use Case | Why it fits |
|---|---|
| **Live customer chat** | Feels like being transferred to a human specialist |
| **Medical triage bots** | Route to the right department (cardiology, billing, scheduling) |
| **Legal intake systems** | Router identifies case type, hands off to specialist attorney bot |
| **HR support** | Route payroll vs. PTO vs. onboarding queries to different agents |
| **E-commerce support** | Route orders vs. returns vs. account issues separately |

**Example:** A hospital chatbot where the router identifies "this is about billing" and transfers the patient to a billing specialist agent that handles the full conversation with relevant context about insurance and invoices.

---

## LLM Provider Differences

### `agent_as_tools.py` — Groq + LLaMA 3.3 70B

```python
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=client,
)
```

Groq provides **ultra-fast inference** (often 500+ tokens/sec) using LPU hardware. LLaMA 3.3 70B is open-source and strong at instruction-following. Best for high-throughput batch processing.

### `handsoff.py` — Gemini 2.5 Flash

```python
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)
```

Gemini 2.5 Flash via Google's API accessed through an OpenAI-compatible endpoint. Optimized for fast, cost-efficient responses. Good for interactive chat loops.

Both use the `OpenAIChatCompletionsModel` wrapper — meaning **any OpenAI-compatible provider** can be swapped in without changing the agent logic.

---

## Environment Variables Required

### `agent_as_tools.py`
```env
GROQ_API_KEY=your_groq_api_key
TRACING_EXPORT_API_KEY=your_tracing_key   # optional, for observability
```

### `handsoff.py`
```env
GEMINI_API_KEY=your_gemini_api_key
TRACING_EXPORT_API_KEY=your_tracing_key   # optional, for observability
```

---

## How to Run

### Prerequisites
```bash
pip install openai-agents python-dotenv
```

### Run Agent-as-Tool (batch mode)
```bash
python agent_as_tools.py
```
Processes two hardcoded emails and prints responses. No user input needed.

### Run Handoff (interactive mode)
```bash
python handsoff.py
```
Starts an interactive prompt. Type your support question and press Enter. Type `exit` to quit.

---

## Quick Decision Guide

```
Do you need the orchestrator to review or combine specialist outputs?
  YES → Agent-as-Tool (agent_as_tools.py)
  NO  → Handoff (handsoff.py)

Is this a batch pipeline or interactive chat?
  Batch    → Agent-as-Tool
  Chat     → Handoff

Do multiple agents need to contribute to one response?
  YES → Agent-as-Tool (call multiple tools, synthesize)
  NO  → Handoff (one specialist owns the answer)

Do you want the user experience of being "transferred"?
  YES → Handoff
  NO  → Agent-as-Tool
```

---

## Summary

Both patterns solve the same problem — routing users to the right specialist — but with different philosophies:

**Agent-as-Tool** treats specialists as **functions**: call them, get a result, decide what to do with it. The orchestrator never relinquishes control.

**Handoff** treats specialists as **owners**: transfer the user to them and step back. The specialist is fully responsible for the response.

Neither is universally better. Complex workflows with synthesis or conditional logic benefit from Agent-as-Tool. Clean, isolated domain handling is cleaner with Handoffs. Many production systems combine both patterns at different levels of the agent hierarchy.