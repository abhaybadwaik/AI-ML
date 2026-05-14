          # Day 1 — Basic CLI AI Agent (OpenAI Agents SDK + Groq)

## What this script does
Creates a simple command-line AI assistant using the OpenAI Agents SDK with Groq API (LLaMA 3.1). The user types a question in the terminal, the agent sends it to the Groq model, and prints the response back in real time.

---

## Concepts Covered
- OpenAI Agents SDK basics
- Agent creation and configuration
- AsyncOpenAI client setup
- OpenAI-compatible APIs (Groq endpoint)
- Model wrapper using OpenAIChatCompletionsModel
- CLI-based interaction loop
- Runner execution pipeline (run_sync)
- Environment variable management (.env file)

---
## Real-World Use Case
**Foundation of OpenAI Agents SDK Systems**

This basic agent architecture is the starting point for building:
- AI agents
- AI copilots
- autonomous workflows
- customer support bots
- AI research assistants
- enterprise AI systems

It is the simplest form of an AI agent system before adding tools, memory, or multi-agent orchestration.

---

## How It Works (Architecture Flow)

```text
User Input
   ↓
CLI Loop (input)
   ↓
Runner.run_sync()
   ↓
Agent
   ↓
OpenAIChatCompletionsModel
   ↓
Groq API (LLaMA 3.1)
   ↓
AI Response Generated
   ↓
Runner returns result
   ↓
final_output printed in terminal