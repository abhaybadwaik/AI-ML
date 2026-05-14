# Day 6 — Run Results: What the Agent Returns and How to Use It

This file goes deeper into the result object that `Runner.run()` and `Runner.run_streamed()` return. Most examples just print `result.final_output` and move on — this file opens up everything else sitting inside the result and shows how to use it for multi-turn memory, observability, and real-time streaming inspection.

---

## What Problem Are We Solving?

When an agent finishes running, it gives you back far more than just the final text. It gives you the full conversation history ready to feed into the next turn, a reference to which agent produced the output, every intermediate item that was generated (tool calls, tool outputs, messages), the raw API responses, and guardrail results. Ignoring all of this means you are flying blind — you cannot build multi-turn conversations, you cannot debug what the agent actually did, and you cannot inspect tool usage.

This file demonstrates three things: a normal run that explores the result object, a streaming run that processes every event type, and an inspection run that reads the observability fields.

---

## The Agent and Tools

The agent is a customer support assistant with two tools.

`calculate_refund` takes an amount and tax percentage and returns the refund total. It is triggered for payment and refund questions.

`create_support_ticket` takes a description of an issue and returns a fake ticket number. It is triggered for technical complaints.

Both tools print debug output when they execute — amount in, result out — so you can see exactly when tool execution happens during a run.

`tool_use_behavior="stop_on_first_tool"` is set on the agent, which means after any tool runs and returns a result, the agent stops immediately. The tool output becomes the final answer rather than passing back through the LLM for further reasoning. This makes the flow deterministic and cheap for simple lookup-style tools.

---

## Demo 1 — Normal Run and Result Fields

```python
result = await Runner.run(
    support_agent,
    "Refund 1000 rupees with 18 percent tax"
)
```

After this completes, three things are pulled from the result.

`result.final_output` is the complete text response from the agent. This is what you print to the user. For this query, it will contain the calculated refund amount.

`result.to_input_list()` is how multi-turn conversations work. This method serializes the entire conversation — the original input, every intermediate tool call, every tool output, and the final message — into a list that can be passed directly as the `input` parameter of the next `Runner.run()` call. The new agent run picks up exactly where the last one left off. Without this, every run is stateless and the agent forgets everything. With this, you build conversation history manually but correctly.

```python
# Turn 1
result = await Runner.run(agent, "Hello")

# Turn 2 — agent remembers turn 1
result = await Runner.run(agent, result.to_input_list() + [{"role": "user", "content": "What did I just say?"}])
```

`result.last_agent.name` tells you which agent produced the final output. In single-agent systems this is always the same agent, but in multi-agent systems with handoffs, the orchestrator might hand off to a specialist and the specialist produces the final output. Knowing which agent was last active is essential for logging, routing follow-up messages, and debugging unexpected behavior.

---

## Demo 2 — Streaming Run and Event Types

```python
result = Runner.run_streamed(
    support_agent,
    "My app crashes during payment"
)

async for event in result.stream_events():
    ...
```

The streamed run emits events continuously as the agent works. Three event types are handled.

`raw_response_event` with `ResponseTextDeltaEvent` carries individual tokens from the LLM as they are generated. Each `event.data.delta` is a small fragment of text — sometimes a word, sometimes punctuation. Printing these creates the typing effect. The import at the top of the file is specifically for type-checking this event's data:

```python
from openai.types.responses import ResponseTextDeltaEvent
```

Using `isinstance(event.data, ResponseTextDeltaEvent)` is more precise than checking string types — it avoids processing other raw events that carry non-text data like tool call deltas.

`run_item_stream_event` fires for completed logical units rather than individual tokens. Three sub-types appear here.

`tool_call_item` means the agent has decided to call a tool and the call is fully formed. You can read `item.raw_item.name` for the tool name and `item.raw_item.arguments` for the arguments the agent prepared. This fires before the tool actually executes, so you can use it to show the user "searching..." or "calculating..." indicators.

`tool_call_output_item` means the tool has finished executing and returned its result. `item.output` contains the string the tool returned. This fires after tool execution completes.

`message_output_item` means the agent has produced a final text message. This fires when the agent is done reasoning and has a response ready.

`agent_updated_stream_event` fires when the active agent changes. `event.new_agent.name` tells you which agent has taken over. In this single-agent example it fires once at the start. In a handoff-based system it fires each time control transfers to a new agent, letting you update a UI indicator showing which specialist is currently responding.

After the stream completes, two fields on the result are checked.

`result.final_output` is available after the stream ends, same as in a normal run.

`result.is_complete` is a boolean that confirms the stream finished cleanly without being cut off. If streaming is interrupted by a network error or timeout, this will be `False`, which you can use to detect incomplete responses and retry.

---

## Demo 3 — Result Inspection for Observability

```python
result = await Runner.run(
    support_agent,
    "Refund 500 with 5 percent tax"
)
```

Four fields are inspected after a normal run.

`result.new_items` is the list of every item generated during this run — tool calls, tool outputs, and messages. Each item has a `.type` property. Iterating over this gives you a complete audit trail of what the agent did step by step. For debugging a confused agent, this is the first place to look — you can see exactly which tools were called in which order and what they returned.

```python
for item in result.new_items:
    print("-", item.type)
# Output might be: tool_call_item, tool_call_output_item, message_output_item
```

`result.raw_responses` is the list of raw API response objects from the LLM provider. `len(result.raw_responses)` tells you how many API calls were made during this run. A simple one-tool run typically produces two raw responses — one where the model decides to call the tool, and one where it generates the final message (or just one if `stop_on_first_tool` is set and the tool output is returned directly). More than expected means the agent looped more times than you intended, which is worth monitoring.

`result.input_guardrail_results` and `result.output_guardrail_results` are lists of results from any guardrails attached to the agent. In this file the agent has no guardrails, so both are empty lists. In a system with guardrails (like Day 8), these fields tell you whether any guardrail fired, what the classification result was, and whether a tripwire was triggered. Logging these in production lets you build a dashboard of how often content is blocked and why.

---

## Real-World Use Cases

`result.to_input_list()` is the foundation of any stateful chat application. Every turn passes the previous result's input list as the starting context, building a growing conversation that the agent can reference. Session memory backends like SQLite and Redis (from Day 7) automate this, but `to_input_list()` is what they use internally.

`result.last_agent` matters in customer support routing. If a billing agent handled the query, you tag the conversation record as billing in your CRM. If the tech agent handled it, you tag it as technical. Downstream analytics depend on knowing which specialist dealt with each issue.

`result.new_items` is invaluable for billing and usage tracking. Count the number of tool calls an agent made, which tools it used, and how many LLM turns it took. This data feeds into cost calculation, user quota enforcement, and identifying agents that are looping unnecessarily.

`result.raw_responses` length monitoring catches runaway agents in production. If a run that normally takes 2 API calls is suddenly taking 10, something is wrong — the agent is confused, a tool is returning unexpected results, or the instructions are producing a loop. Alerting on this in real time prevents expensive runaway sessions.

`result.is_complete` in streaming is critical for resumable generation. If a stream is cut off, you can detect it, save the partial output, and offer the user a "continue" option that resumes from where the stream broke rather than starting over.

Guardrail result logging builds compliance records. In regulated industries, you need to prove that content was screened before reaching users. Storing `input_guardrail_results` and `output_guardrail_results` per conversation gives you an auditable trail showing what was checked and what decisions were made.

---

## Environment Variables Required

```env
GROQ_API_KEY=your_groq_api_key
```

---

## How to Run

```bash
pip install openai-agents python-dotenv
python results.py
```

The script runs all three demos sequentially — normal run, streaming run, and inspection run — and prints detailed output for each. Read the console output top to bottom to follow the event flow.

---

## Summary

Day 6 part two is about treating the result object as a first-class data source, not just a text wrapper. `final_output` is the surface. Underneath it is conversation history for multi-turn memory, agent identity for routing, item traces for debugging, API call counts for cost monitoring, and guardrail results for compliance. The streaming result adds token-level events, structured item events, and a completion flag. Together these fields give you full visibility into what the agent did, how it did it, and whether it did it correctly.