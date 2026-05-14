import asyncio
import json
import os

from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)
from tools import get_weather, send_weather_email, TO_EMAIL

load_dotenv()
set_tracing_disabled(True)


# -------------------------------------------------------------
# CLIENT & MODEL
# -------------------------------------------------------------
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)


# -------------------------------------------------------------
# SINGLE AGENT — both tools, clear instructions
# -------------------------------------------------------------
agent = Agent(
    name="Weather Agent",
    instructions=f"""
You are a weather assistant with two tools:

1. get_weather(city)           — fetches live weather for a city.
2. send_weather_email(content) — emails the report to {TO_EMAIL}.

Rules:
- When asked for weather → call get_weather(city) and return the result.
- When asked to send email → call send_weather_email(content) with the
  full weather text as content.
- Never ask for an email address. It is always {TO_EMAIL}.
- Never say the email was sent until the tool confirms it.
""",
    model=model,
    tools=[get_weather, send_weather_email],
)


# -------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------
def sep(char: str = "-", width: int = 60) -> None:
    print(char * width)


def show_interruption(interruption) -> None:
    raw     = interruption.arguments
    args    = json.loads(raw) if isinstance(raw, str) else raw
    preview = args.get("content", "(no content)")[:400]

    print()
    sep()
    print("  AGENT PAUSED -- email approval required")
    sep()
    print(f"  Tool : {interruption.tool_name}")
    print(f"  To   : {TO_EMAIL}")
    print(f"\n  Content preview:\n")
    for line in preview.splitlines():
        print(f"    {line}")
    print()
    sep()


def ask(prompt: str) -> bool:
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  Please type y or n.")


# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
async def main() -> None:
    print()
    sep("=")
    print("  HITL Weather Agent")
    print(f"  Email reports go to: {TO_EMAIL}")
    print("  Ctrl+C to quit.")
    sep("=")

    user_input = input("\nYou: ").strip()
    if not user_input:
        print("Nothing entered. Exiting.")
        return

    # ── STEP 1: fetch weather ─────────────────────────────────
    print("\n[Fetching weather...]\n")
    result       = await Runner.run(agent, input=user_input)
    weather_text = result.final_output or ""
    print(weather_text)

    # ── STEP 2: script asks the user ─────────────────────────
    print()
    if not ask("  Should I send this report via email? [y/n]: "):
        print("\n  OK, report not sent. Goodbye!\n")
        return

    # ── STEP 3: same agent, now asked to send email ───────────
    print("\n[Preparing to send email...]\n")
    result = await Runner.run(
        agent,
        input=f"Send this weather report via email:\n\n{weather_text}",
    )

    # ── STEP 4: HITL approval loop ────────────────────────────
    # send_weather_email has needs_approval=True, so the SDK pauses
    # here and waits for state.approve() before SMTP runs.
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

    # ── STEP 5: done ──────────────────────────────────────────
    print()
    sep("=")
    print("Agent:", result.final_output)
    sep("=")
    print()


if __name__ == "__main__":
    asyncio.run(main())