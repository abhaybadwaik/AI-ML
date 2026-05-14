# Day 9 — Human-in-the-Loop (HITL): Agent Approval Before Action

This day covers Human-in-the-Loop (HITL) — the pattern where an AI agent pauses before executing a consequential action and waits for a human to explicitly approve or reject it. The example builds a weather agent that can fetch weather freely but requires your approval before sending any email.

---

## What Problem Are We Solving?

Autonomous agents are powerful, but some actions are irreversible. Sending an email, deleting a file, charging a credit card, or posting to social media — these cannot be undone once executed. If an agent makes a mistake or misunderstands intent, the damage is already done by the time you notice.

HITL solves this by inserting a human checkpoint before the dangerous action runs. The agent does all the reasoning and preparation, but it cannot pull the trigger on sensitive operations without explicit human sign-off. This is the difference between an agent that assists you and one that acts on your behalf without oversight.

---

## File Overview

The system is split across two files for clean separation of concerns.

`tools.py` defines what the agent can do — fetch weather and send email. It also owns the HITL gate itself via `needs_approval=True`.

`hitl.py` defines the agent, orchestrates the conversation flow, handles the approval prompts, and manages the interruption/resume loop.

---

## `tools.py` — The Tools and the HITL Gate

### Tool 1 — `get_weather`

```python
@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city using the OpenWeatherMap API."""
```

A standard function tool with no special restrictions. When the agent calls this, it executes immediately — no pause, no approval needed. It calls the OpenWeatherMap API and returns a formatted weather report. This is a read-only operation with no side effects, so HITL is not needed here.

### Tool 2 — `send_weather_email` with `needs_approval=True`

```python
@function_tool(needs_approval=True)
def send_weather_email(content: str) -> str:
    """Send a weather report to the fixed recipient. Requires human approval."""
```

This is where HITL is implemented. The single parameter `needs_approval=True` changes everything about how this tool behaves. When the agent decides to call `send_weather_email`, the SDK does not enter the function body immediately. Instead it pauses execution, creates an interruption object describing the pending tool call, and surfaces it back to your code in `hitl.py`.

The SMTP code inside the function — the part that actually connects to Gmail and sends the email — only runs if and when `state.approve(interruption)` is called from the outside. If `state.reject(interruption)` is called instead, the function body never executes at all. The SMTP server is never contacted.

This is the core HITL guarantee: `needs_approval=True` is a hard gate, not a soft suggestion. Nothing inside the function runs without human sign-off.

---

## `hitl.py` — The Orchestration and Approval Loop

### The Agent

```python
agent = Agent(
    name="Weather Agent",
    instructions=f"""...""",
    model=model,
    tools=[get_weather, send_weather_email],
)
```

One agent handles both tools. The instructions make the routing logic explicit: use `get_weather` when asked for weather data, use `send_weather_email` when asked to email a report. The agent is told never to ask for an email address since it is hardcoded in `tools.py`.

### Step 1 — Fetch Weather (No Approval Needed)

```python
result = await Runner.run(agent, input=user_input)
weather_text = result.final_output or ""
print(weather_text)
```

The first run fetches weather. Since `get_weather` has no approval gate, this completes normally. The weather report is stored in `weather_text` for the next step.

### Step 2 — Human Confirms Before Even Asking the Agent

```python
if not ask("  Should I send this report via email? [y/n]: "):
    print("\n  OK, report not sent. Goodbye!\n")
    return
```

This is a lightweight pre-check done by the script itself — before the agent is even involved in the email decision. If the user says no here, the agent is never asked to send the email and the HITL loop never starts. This is a good pattern: fail fast before consuming API calls.

### Step 3 — Ask the Agent to Send Email

```python
result = await Runner.run(
    agent,
    input=f"Send this weather report via email:\n\n{weather_text}",
)
```

The agent receives explicit instruction to send the email. It decides to call `send_weather_email`. Because `needs_approval=True`, execution pauses here and the result contains an interruption instead of a final output.

### Step 4 — The HITL Approval Loop

```python
while result.interruptions:
    interruption = result.interruptions[0]
    show_interruption(interruption)

    state = result.to_state()

    if ask("  Confirm sending email? [y/n]: "):
        state.approve(interruption)
        print("\n  Approved. Sending email...\n")
    else:
        state.reject(interruption)
        print("\n  Cancelled. Email not sent.\n")

    result = await Runner.run(agent, input=state)
```

This is the heart of HITL. The loop runs as long as there are pending interruptions.

`result.interruptions` is the list of paused tool calls waiting for a decision. Each interruption carries the tool name and the arguments the agent prepared — in this case, the full email content.

`show_interruption` parses the arguments and prints a preview of what the agent is about to send, so the human can read it before deciding.

`result.to_state()` converts the current run into a resumable state object. This is what allows the run to be paused and resumed rather than restarted.

`state.approve(interruption)` marks the tool call as approved. `state.reject(interruption)` marks it as cancelled. Both return without executing the tool — the decision is recorded in the state object.

`Runner.run(agent, input=state)` resumes execution from where it was paused, now with the decision applied. If approved, the SMTP code runs. If rejected, it is skipped and the agent produces a cancellation message.

The loop structure handles the case where an agent might have multiple pending approvals — though in this example there is only one.

### `show_interruption` — Transparency Before Approval

```python
def show_interruption(interruption) -> None:
    raw  = interruption.arguments
    args = json.loads(raw) if isinstance(raw, str) else raw
    preview = args.get("content", "(no content)")[:400]
```

The arguments the agent prepared are JSON-encoded. This helper decodes them and shows the first 400 characters of the email content. The human sees exactly what the agent is about to send before making the decision. This transparency is what makes HITL meaningful — you are not just approving a black box, you are reading the actual output.

---

## The Full Flow, Step by Step

The user types a question like "what is the weather in London". The agent calls `get_weather("London")` and the weather report is printed. The script asks whether to send it via email. If the user says no, the program ends. If yes, the agent is asked to send the email. The SDK intercepts the `send_weather_email` call, pauses before the function body runs, and surfaces an interruption. The human reads the email preview and either approves or rejects. If approved, the SMTP connection is made and the email is sent. If rejected, the function never runs and the agent confirms cancellation.

---

## Real-World Use Cases

Financial transactions are the most obvious application. An agent that manages payments or transfers should never move money without explicit human confirmation. The agent prepares the transaction — amount, recipient, account — and a human reviews and approves before the API call to the bank is made.

Content publishing follows the same pattern. An agent that drafts and posts social media content or blog articles should pause before publishing. The human reads the draft, approves it, and only then does the POST request go out to Twitter or WordPress.

Database mutations are another strong use case. An agent that can write to a production database — inserting, updating, or deleting records — should require approval for any destructive or wide-reaching operation. Read queries can run freely; writes need a human checkpoint.

Customer communication in enterprise software is critical. An agent that emails customers on behalf of a company should surface the draft for a compliance or legal review before sending. The agent handles writing and personalization; the human handles sign-off.

Infrastructure changes in DevOps are irreversible if done wrong. An agent managing cloud resources — scaling, termination, configuration changes — should pause before applying any change to production. The agent composes the change plan, a human approves it, then execution proceeds.

Legal document generation and filing needs HITL because submitted documents cannot easily be recalled. An agent that prepares contracts or regulatory filings presents the final document for attorney review before submission.

Medical or health recommendation systems should always have a clinician in the loop before any recommendation reaches a patient. The agent processes the data and proposes a recommendation; the human validates it before it is surfaced to the end user.

---

## Environment Variables Required

```env
GEMINI_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
SMTP_EMAIL=your_gmail_address
SMTP_PASSWORD=your_gmail_app_password
```

For Gmail, `SMTP_PASSWORD` must be an App Password generated from Google Account settings, not your regular Gmail password.

---

## How to Run

```bash
pip install openai-agents python-dotenv requests
python hitl.py
```

When prompted, type a weather query such as "weather in Tokyo". The agent fetches and displays the report. You are then asked whether to send it via email. If you say yes, a second approval prompt shows you the email content before anything is sent. At every stage you remain in control.

---

## Summary

Day 9 introduces Human-in-the-Loop as the pattern for keeping humans in control of consequential agent actions. The `needs_approval=True` parameter on a tool is a hard SDK-level gate — the tool body never runs without an explicit `state.approve()` call. The interruption and state system allows a run to be paused, inspected, decided upon, and resumed cleanly without restarting from scratch. The transparency step — showing the human exactly what the agent prepared before asking for approval — is what makes HITL genuinely useful rather than just a formality. This pattern applies anywhere an agent's action is irreversible, sensitive, or carries real-world consequences.