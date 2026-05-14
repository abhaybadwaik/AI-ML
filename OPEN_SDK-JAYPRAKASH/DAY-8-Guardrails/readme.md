# Day 8 — Guardrails: Input & Output Safety in AI Agents

This day covers guardrails — the mechanism for intercepting, inspecting, and blocking agent inputs and outputs before they cause harm or violate your application's rules. The file `guards.py` builds a customer support agent that refuses to engage with math problems, enforced at both ends of the pipeline.

---

## What Problem Are We Solving?

Agents are powerful but unpredictable. A customer support bot should only handle support topics — but without guardrails, nothing stops a user from asking it to solve equations, generate harmful content, or go off-topic. Similarly, even if the input looks fine, the model might produce an output that violates your rules.

Guardrails are the answer. They sit as checkpoints before the input reaches the agent and after the agent produces its output. If either check fails, the response is blocked entirely and a controlled exception is raised — no partial responses, no surprises.

---

## The Architecture

The system has five components working together.

The first is the main agent, `Customer Support`, which handles genuine support queries and is explicitly instructed not to solve math problems.

The second and third are two dedicated guard agents — `Input Guard` and `Output Guard`. These are small, fast agents whose only job is to classify content. They do not chat. They return structured Pydantic objects.

The fourth and fifth are the guardrail functions themselves — `math_input_guardrail` and `math_output_guardrail` — which wrap the guard agents and tell the SDK whether to block or allow the request.

```
User Input
    │
    ▼
[INPUT GUARDRAIL] ──── runs Input Guard agent ────► is_math=True? BLOCK → raise InputGuardrailTripwireTriggered
    │ (passes)
    ▼
[MAIN AGENT] ─── generates response ───►
    │
    ▼
[OUTPUT GUARDRAIL] ── runs Output Guard agent ──► has_math=True? BLOCK → raise OutputGuardrailTripwireTriggered
    │ (passes)
    ▼
Final Response to User
```

---

## Pydantic Output Schemas

Guard agents return structured data, not free text. This makes the classification machine-readable and reliable.

```python
class InputCheck(BaseModel):
    is_math: bool
    reason: str

class OutputCheck(BaseModel):
    has_math: bool
    reason: str
```

`is_math` tells us whether the input is a math problem. `has_math` tells us whether the output contains math. The `reason` field carries a human-readable explanation, which is printed to the user when a block occurs.

By setting `output_type=InputCheck` on the guard agent, the SDK forces the model to return only valid JSON matching this schema — no freeform text, no hallucinated fields.

---

## Input Guardrail — Parallel Execution

```python
@input_guardrail(run_in_parallel=True)
async def math_input_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guard_agent, input=input, context=ctx.context)
    check: InputCheck = result.final_output
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.is_math,
    )
```

The `@input_guardrail` decorator registers this function as a pre-check. It receives the raw user input before the main agent ever sees it.

The critical parameter here is `run_in_parallel=True`. When this is set, the input guardrail runs at the same time as the main agent invocation — not before it. This is a performance optimization. If the guardrail passes (input is not math), both finish around the same time and there is no wasted wait. If the guardrail triggers, the main agent's response is discarded.

The artificial `await asyncio.sleep(5)` in the guardrail is there specifically to demonstrate this behavior. With parallel mode, the 5-second guardrail delay does not add 5 seconds to the total response time because the main agent is running simultaneously. In sequential mode (set `run_in_parallel=False`), those 5 seconds would be paid before the main agent even starts.

`tripwire_triggered=check.is_math` is the decision point. When this is `True`, the SDK raises `InputGuardrailTripwireTriggered` and the main agent's output (if any) is never returned to the user.

---

## Output Guardrail — Sequential by Default

```python
@output_guardrail
async def math_output_guardrail(ctx, agent, output) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guard_agent, input=output, context=ctx.context)
    check: OutputCheck = result.final_output
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.has_math,
    )
```

The output guardrail runs after the main agent has produced its response. It receives the full output text and passes it to the `Output Guard` agent for classification.

Output guardrails are inherently sequential — they can only run after the main agent finishes, because they need something to inspect. The 1-second sleep here is much lighter than the input guardrail because by the time this runs, the user is already waiting on a response that exists.

If `has_math=True`, the SDK raises `OutputGuardrailTripwireTriggered`. The user never sees the blocked output.

This is a double safety net: even if a clever user somehow got a math-adjacent question past the input guardrail, the output guardrail would catch the math in the response.

---

## Exception Handling

The two guardrail exceptions are caught separately so they can give different messages:

```python
except InputGuardrailTripwireTriggered as e:
    check: InputCheck = e.guardrail_result.output.output_info
    print("INPUT BLOCKED")
    print(check.reason)

except OutputGuardrailTripwireTriggered as e:
    check: OutputCheck = e.guardrail_result.output.output_info
    print("OUTPUT BLOCKED")
    print(check.reason)
```

The `output_info` field carries the full Pydantic object that the guard agent returned — including the `reason` string — so you can show the user a meaningful explanation of why their request was blocked rather than a generic error.

---

## Timing and Logging

The code timestamps every major step using `time.strftime('%X')` and measures durations with `time.time()`. This is intentional — the file is designed to teach the difference between parallel and sequential execution visually, by watching the timestamps in the console output.

Running with `run_in_parallel=True`, you will see the input guardrail start and the main agent start almost simultaneously. Running with `run_in_parallel=False`, you will see the main agent start only after the guardrail finishes — paying the full 5-second penalty.

The total execution time printed at the end makes the performance difference immediately obvious.

---

## Registering Guardrails on the Agent

```python
agent = Agent(
    name="Customer Support",
    model=model,
    input_guardrails=[math_input_guardrail],
    output_guardrails=[math_output_guardrail],
)
```

Guardrails are attached directly to the agent definition. You can register multiple guardrails in each list — they run in order, and the first one to trigger a tripwire stops execution immediately.

---

## Real-World Use Cases

Input guardrails are useful anywhere you need to enforce topic restrictions, detect prompt injection attempts, filter profanity or PII before it reaches the model, enforce language restrictions, or block competitor mentions in a sales bot.

Output guardrails are useful for detecting hallucinated facts before they reach the user, catching accidental disclosure of sensitive information, enforcing brand tone or legal disclaimers, filtering out content that violates platform rules, or ensuring responses stay within a required length or format.

The pattern generalizes beyond math detection to any classification task. You swap out the guard agent's instructions and Pydantic schema, and the entire blocking mechanism works identically.

---

## Environment Variables Required

```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## How to Run

```bash
pip install openai-agents python-dotenv pydantic
python guards.py
```

Type any support question to get a normal response. Type a math question like "what is 24 times 17" to see the input guardrail block it. To test the output guardrail, you would need to modify the main agent's instructions to allow math responses and see if the output blocker catches it.

To switch between parallel and sequential input guardrail execution, change the decorator on `math_input_guardrail`:

```python
@input_guardrail(run_in_parallel=True)   # parallel — faster
@input_guardrail(run_in_parallel=False)  # sequential — safer for strict ordering
```

Watch the timestamps in the console to see exactly how the timing changes.

---

## Summary

Day 8 introduces guardrails as the safety layer around your agents. Input guardrails intercept requests before the model processes them. Output guardrails inspect responses before they reach the user. Guard agents are lightweight classifiers with structured Pydantic outputs that make the block/allow decision deterministic and explainable. Parallel execution of input guardrails is a key performance technique — running the check alongside the main agent avoids paying the full guardrail latency on every request. Together, input and output guardrails give you a reliable, principled way to enforce any rule your application requires.