import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from agents import function_tool
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SMTP_EMAIL          = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD       = os.getenv("SMTP_PASSWORD")
TO_EMAIL            = "divvijayaprakash.eidiko@gmail.com"


# ─────────────────────────────────────────────────────────────
# TOOL 1 — get_weather
# Runs immediately, no approval needed.
# ─────────────────────────────────────────────────────────────
@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city using the OpenWeatherMap API."""

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    try:
        data = requests.get(url, timeout=10).json()
    except requests.RequestException as e:
        return f"❌ Network error: {e}"

    if data.get("cod") != 200:
        return f"❌ City not found: {city}"

    return (
        f"🌤 Weather Report for {city.title()}:\n"
        f"  Condition : {data['weather'][0]['description']}\n"
        f"  Temp      : {data['main']['temp']}°C "
        f"(feels like {data['main']['feels_like']}°C)\n"
        f"  Humidity  : {data['main']['humidity']}%\n"
        f"  Wind      : {data['wind']['speed']} m/s"
    )


# ─────────────────────────────────────────────────────────────
# TOOL 2 — send_weather_email
#
# needs_approval=True  ← THIS is the HITL gate.
#
# When the agent calls this tool, the SDK:
#   1. Pauses execution BEFORE entering this function body.
#   2. Surfaces an interruption object to the caller (hitl.py).
#   3. Waits for state.approve() or state.reject().
#
# Everything below the def line only runs AFTER approval.
# If rejected, this body never executes — SMTP is never touched.
# ─────────────────────────────────────────────────────────────
@function_tool(needs_approval=True)
def send_weather_email(content: str) -> str:
    """Send a weather report to the fixed recipient. Requires human approval."""

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return "❌ SMTP credentials missing. Add SMTP_EMAIL and SMTP_PASSWORD to .env"

    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = "🌤 Your Weather Report"
        msg["From"]    = SMTP_EMAIL
        msg["To"]      = TO_EMAIL
        msg.attach(MIMEText(content, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, TO_EMAIL, msg.as_string())

        return f"✅ Email sent successfully to {TO_EMAIL}"

    except smtplib.SMTPAuthenticationError:
        return "❌ Gmail auth failed. Use a Gmail App Password, not your account password."
    except smtplib.SMTPException as e:
        return f"❌ SMTP error: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"