import asyncio
import os
from dataclasses import dataclass, field
from typing import Dict, List

from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
    RunContextWrapper,
    set_tracing_disabled
)

# ---------------------------
# LOAD ENV
# ---------------------------
load_dotenv()
set_tracing_disabled(True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("❌ GEMINI_API_KEY missing in .env")

# ---------------------------
# GEMINI (OpenAI-compatible endpoint)
# ---------------------------
client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# ---------------------------
# CONTEXT
# ---------------------------
@dataclass
class UserContext:
    user_id: str

# ---------------------------
# IN-MEMORY DB
# ---------------------------
db: Dict[str, List[str]] = {}

# ---------------------------
# TOOL: BOOK ROOM
# ---------------------------
@function_tool
def book_room(
    wrapper: RunContextWrapper[UserContext],
    room: str
) -> str:
    user_id = wrapper.context.user_id

    db.setdefault(user_id, []).append(room)

    return f"🏨 Gemini: User {user_id} booked room {room}"

# ---------------------------
# TOOL: VIEW BOOKINGS
# ---------------------------
@function_tool
def view_bookings(
    wrapper: RunContextWrapper[UserContext],
    dummy: str = ""
) -> str:
    user_id = wrapper.context.user_id

    bookings = db.get(user_id, [])

    if not bookings:
        return f"📭 No bookings for user {user_id}"

    return f"📋 Bookings for {user_id}: {bookings}"

# ---------------------------
# TOOL: CANCEL BOOKING
# ---------------------------
@function_tool
def cancel_booking(
    wrapper: RunContextWrapper[UserContext],
    room: str
) -> str:
    user_id = wrapper.context.user_id

    if room in db.get(user_id, []):
        db[user_id].remove(room)
        return f"❌ Cancelled room {room} for user {user_id}"

    return "❌ Booking not found"

# ---------------------------
# AGENT
# ---------------------------
agent = Agent[UserContext](
    name="Hotel Assistant (Gemini)",
    model=model,
    instructions="You are a hotel booking assistant. Use tools for all actions.",
    tools=[book_room, view_bookings, cancel_booking],
)

# ---------------------------
# RUN DEMO
# ---------------------------
async def main():

    user_a = UserContext(user_id="A")
    user_b = UserContext(user_id="B")

     
    print(await Runner.run(agent, "book 202", context=user_b))
    print(await Runner.run(agent, "view bookings", context=user_a))

# ---------------------------
# START
# ---------------------------
if __name__ == "__main__":
    asyncio.run(main())