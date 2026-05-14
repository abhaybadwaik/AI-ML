# Day 3 — Tools & Tool-Based Orchestration in OpenAI Agents SDK

## What this script does
This script demonstrates how to build **tool-using AI agents** and **tool-based orchestration systems** using the OpenAI Agents SDK.

It includes:
- Single-tool agent (Weather agent)
- Multi-tool routing (Customer support system)
- Tool-based orchestration (LLM decides + combines multiple tools)
- Real API integration (OpenWeather + external LLM APIs)

---

## Concepts Covered
- Function tools (`@function_tool`)
- Tool calling in Agents SDK
- Single tool execution flow
- Multi-tool routing
- Tool-based orchestration (LLM-controlled execution flow)
- How LLM selects tools
- How tools are executed internally
- Async execution (`Runner.run`)
- External API integration
- OpenAI-compatible LLMs (Groq / Gemini)
- Agent instructions for tool control
- Combining multiple tool outputs

---

# 1. Weather Agent (Single Tool)

## What it does
Fetches real-time weather using OpenWeather API.

The agent itself does NOT know live weather data.

Instead:
- LLM understands user intent
- selects weather tool
- tool fetches live data
- LLM formats response naturally

---

## Architecture Flow

```text
User Input
   ↓
Runner.run()
   ↓
Agent
   ↓
LLM analyzes request
   ↓
Should a tool be called?
   ↓
YES
   ↓
Select get_weather tool
   ↓
SDK executes Python function
   ↓
Function calls OpenWeather API
   ↓
Weather data returned
   ↓
LLM reads tool result
   ↓
Generates human-friendly answer
   ↓
final_output