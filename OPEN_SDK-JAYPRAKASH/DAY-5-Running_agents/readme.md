# Day 5 — Running Agents: Async, Sync, Streamed & RunConfig

This day covers the different ways to execute an agent using the `Runner` class. Four files demonstrate four distinct execution modes and configuration patterns, from the simplest one-liner to a fully streamed event pipeline with runtime controls.

---

## What Problem Are We Solving?

Every agent needs to be run somehow — but "run" means different things in different situations. A CLI script can block and wait. A web server cannot. A chatbot wants to show text appearing word by word. A batch pipeline needs strict control over temperature and token limits. The `Runner` class handles all of these, and choosing the right mode is the difference between a responsive application and a frozen one.

---

## File 1 — `run.py` (Standard Async Run)

This is the baseline — the simplest correct way to run an agent.

```python
async def main():
    result = await Runner.run(agent, "Explain AI in simple words")
    print(result.final_output)

asyncio.run(main())
```

`Runner.run()` is a coroutine. It sends the input to the agent, waits for the full response, and returns a result object. `result.final_output` is the complete text the agent produced.

The key word is `await` — this is non-blocking at the event loop level. While the agent is waiting for the LLM response over the network, the event loop is free to handle other coroutines. This makes it the right choice for async applications like FastAPI, Discord bots, or any service handling concurrent requests.

`set_tracing_disabled(True)` is called at the top. This disables the OpenAI Agents SDK's built-in tracing, which would otherwise send run data to a tracing backend. Disabling it reduces overhead and avoids any network calls to tracing endpoints during development.

When to use this: any async application, API servers, bots, or anywhere you already have an event loop running.

---

## File 2 — `run_sync.py` (Synchronous Run)

The synchronous version removes all async machinery.

```python
result = Runner.run_sync(
    agent,
    "Explain AI in simple words"
)
print(result.final_output)
```

No `async def`, no `await`, no `asyncio.run()`. `Runner.run_sync()` is a regular blocking function call. It internally creates and manages its own event loop, runs the coroutine, and returns the result before the next line of code executes.

This blocks the entire thread until the agent responds. For a web server, that is catastrophic — no other requests can be handled during the wait. But for a simple script, a Jupyter notebook cell, a test, or a command-line tool, it is perfectly appropriate and much simpler to read and reason about.

When to use this: scripts, notebooks, tests, one-off tools, or any context where you do not have an existing event loop and do not need concurrency.

---

## File 3 — `run_config.py` (Runtime Configuration with RunConfig)

This file introduces `RunConfig` — the mechanism for controlling agent execution behavior at the point of the call, not at the point of agent definition.

```python
result = await Runner.run(
    agent,
    input="Explain AI simply",
    max_turns=3,
    run_config=RunConfig(
        model_settings=ModelSettings(
            temperature=0.3,
            max_tokens=150,
        ),
        tracing_disabled=True,
    ),
)
```

`max_turns=3` is a safety valve. An agent can loop — it might call a tool, get a result, call another tool, and so on. Without a cap, a bug or a confused model could loop indefinitely, burning tokens and money. Setting `max_turns=3` means if the agent has not produced a final output after 3 turns, the run is stopped. This is essential for production safety.

`RunConfig` is the runtime override layer. The agent was defined with certain defaults, but `RunConfig` lets you change behavior per call without touching the agent definition. This matters when the same agent needs different settings in different contexts — a quick draft versus a careful final response, for example.

`ModelSettings(temperature=0.3)` makes the model more deterministic. Lower temperature means the model picks more predictable, less creative tokens. For factual or structured outputs, you want low temperature. For creative writing, you want high temperature. Setting this at runtime lets you tune per request rather than baking it into the agent forever.

`ModelSettings(max_tokens=150)` caps the response length. The agent's instructions already say to keep answers under 100 words, but `max_tokens` is a hard ceiling enforced at the API level, not just a guideline the model might ignore.

When to use RunConfig: any time you need per-request control over model behavior, safety caps on turns, or different settings for different callers of the same agent.

---

## File 4 — `run_streamed.py` (Streaming with Event Loop)

This is the most complex file and demonstrates real-time streaming — where the agent's response is processed token by token as it arrives, rather than waiting for the complete response.

### Why Streaming Matters

Without streaming, the user stares at a blank screen for several seconds, then suddenly sees the full response appear. With streaming, text appears word by word, just like ChatGPT's typing effect. For long responses this feels dramatically more responsive even though the total time is the same.

### Starting a Streamed Run

```python
result = Runner.run_streamed(
    agent,
    input=user_input,
    max_turns=2,
)
```

Note the absence of `await` here. `Runner.run_streamed()` returns a stream object immediately — it does not wait for anything yet. The actual execution happens as you iterate over events.

### The Event Loop

```python
async for event in result.stream_events():
    if event.type == "raw_response_event":
        ...
    elif event.type == "run_item_stream_event":
        ...
    elif event.type == "agent_updated_stream_event":
        ...
```

Every meaningful thing that happens during the run emits an event. You consume them in real time with an async for loop. Three event types are handled here.

`raw_response_event` carries individual tokens as they arrive from the LLM. Each token is a fragment of text — sometimes a word, sometimes half a word. Printing these as they arrive creates the streaming typewriter effect.

```python
if event.type == "raw_response_event":
    if hasattr(event.data, "delta"):
        token = event.data.delta
        if token:
            print("TOKEN:", token)
```

`run_item_stream_event` signals completed logical units — a tool call being made, a tool result arriving, or a final message being produced. These are higher-level than individual tokens. You use these to know when tool execution started, when it finished, and when the agent has completed its reasoning.

```python
if item.type == "tool_call_item":
    print("TOOL NAME:", item.raw_item.name)
    print("ARGUMENTS:", item.raw_item.arguments)
elif item.type == "tool_call_output_item":
    print(item.output)
elif item.type == "message_output_item":
    print("FINAL MESSAGE RECEIVED")
```

`agent_updated_stream_event` fires when the active agent changes — relevant in multi-agent systems with handoffs. It tells you which agent is now producing output.

### `tool_use_behavior="stop_on_first_tool"`

```python
agent = Agent(
    ...
    tool_use_behavior="stop_on_first_tool",
)
```

By default, after a tool returns a result, the agent reasons about it and might call another tool. `stop_on_first_tool` tells the agent to stop after the first tool call completes and return its output directly. This prevents unnecessary additional LLM turns for simple tool lookups like weather or bill calculations. Combined with `max_turns=2`, this keeps the streamed run tight and predictable.

### Tools in This File

Two simple tools are defined for demonstration. `get_weather` looks up a city name in a hardcoded dictionary and returns a weather string. `calculate_bill` computes a total with tax. Both print debug lines when they execute, so you can see in the console exactly when tool execution happens relative to the streaming events.

When to use streaming: any user-facing chat interface, long-form generation where users would otherwise wait, or anywhere real-time feedback improves the perceived experience.

---

## The Four Modes at a Glance

`Runner.run()` is async, non-blocking, returns when complete. Use it in async applications and servers.

`Runner.run_sync()` is synchronous, blocks the thread, returns when complete. Use it in scripts, notebooks, and tests.

`Runner.run_streamed()` is async, returns a stream object immediately, delivers events token by token. Use it in chat UIs and anywhere you want real-time output.

`RunConfig` is not a run mode but a configuration layer that works with any of the above. Use it to control temperature, token limits, turn caps, and tracing per call.

---

## Real-World Use Cases

`Runner.run()` powers async API endpoints. A FastAPI route handler can await the agent and return the result to the HTTP client without blocking other requests.

`Runner.run_sync()` is ideal for data pipelines and ETL scripts that process records sequentially. No async complexity needed, and the blocking behavior is exactly what you want in a linear pipeline.

`RunConfig` is essential in multi-tenant SaaS products. Different subscription tiers can be given different `max_tokens` and `temperature` settings. Free tier users get capped outputs; premium users get longer, more creative responses — all using the same agent, configured differently per call.

Streaming is the standard for any modern chat product. Users expect to see text appearing in real time. Without streaming, even a fast model feels slow because users have nothing to look at while they wait. Streaming also allows early cancellation — if the user sees the response is going in the wrong direction, they can stop it before it finishes.

Streaming with tool events is particularly useful for agent transparency. Showing the user "searching the database..." or "calculating your total..." as a tool executes gives them visibility into what the agent is doing, which builds trust and helps users understand why the response took a moment.

---

## Environment Variables Required

```env
GROQ_API_KEY=your_groq_api_key
```

All four files use Groq with LLaMA. No other API keys are needed.

---

## How to Run

```bash
pip install openai-agents python-dotenv
```

Run the standard async version:
```bash
python run.py
```

Run the sync version:
```bash
python run_sync.py
```

Run with RunConfig:
```bash
python run_config.py
```

Run the streamed version with tool events:
```bash
python run_streamed.py
```

---

## Summary

Day 5 is about execution modes. The agent definition is the same across all four files — what changes is how you invoke it and how you consume the result. `run_sync` for scripts, `run` for async apps, `run_streamed` for real-time UIs, and `RunConfig` for per-call control over model behavior and safety limits. Understanding these modes is fundamental to building agents that fit correctly into real applications rather than just working in isolation.