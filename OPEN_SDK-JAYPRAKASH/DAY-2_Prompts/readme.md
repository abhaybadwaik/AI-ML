# Day 2 — Prompting (Zero-shot, One-shot, Few-shot) in OpenAI Agents SDK

## What this script does
This script demonstrates how an AI Agent behaves differently based on prompting style using the OpenAI Agents SDK.

It shows how adding examples inside `instructions` improves response accuracy, structure, and consistency without changing the model.

---

## Concepts Covered
- Zero-shot prompting (no examples)
- One-shot prompting (1 example)
- Few-shot prompting (multiple examples)
- Role of `instructions` in Agents SDK
- How examples guide model behavior
- Prompt engineering basics in agent systems

---

## Real-World Use Case
**Smart Text Classification System**

This pattern is used in production AI systems such as:
- Sentiment analysis engines
- Spam detection systems
- Customer feedback classification
- Support ticket routing

It helps control AI output without fine-tuning by guiding behavior through examples.

---

## How It Works (Architecture Flow)

```text
User Input
   ↓
Runner.run_sync()
   ↓
Agent
   ↓
Instructions (Zero / One / Few-shot Prompting)
   ↓
LLM (via OpenAI Agents SDK)
   ↓
Pattern learned from examples (if provided)
   ↓
Generated Response
   ↓
final_output printed in terminal