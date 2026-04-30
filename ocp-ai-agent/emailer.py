import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from config import settings


def send_report(state: dict) -> bool:
    """Send the HTML report via Gmail SMTP."""

    failures = state.get("failures", [])
    critical = [f for f in failures if f.get("severity") == "CRITICAL"]
    warnings = [f for f in failures if f.get("severity") == "WARNING"]

    # ── Subject line based on status ──
    if critical:
        status = "🔴 CRITICAL"
    elif warnings:
        status = "🟡 WARNING"
    else:
        status = "🟢 HEALTHY"

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"{status} | OCP Health Check Report | {timestamp}"

    # ── Build email ──
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.email_from
    msg["To"] = ", ".join(settings.get_email_recipients())

    # Attach HTML report
    html_part = MIMEText(state.get("report_html", ""), "html")
    msg.attach(html_part)

    # ── Send via Gmail SMTP ──
    try:
        print(f"\n  [Email] Connecting to {settings.smtp_host}:{settings.smtp_port}...")
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(
                settings.email_from,
                settings.get_email_recipients(),
                msg.as_string()
            )
        print(f"  [Email] ✅ Report sent to {settings.get_email_recipients()}")
        return True
    except Exception as e:
        print(f"  [Email] ❌ Failed to send email: {e}")
        return False