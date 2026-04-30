from config import settings

print("Groq Key loaded:", settings.groq_api_key[:10] + "...")
print("LLM Model:", settings.llm_model)
print("SMTP Host:", settings.smtp_host)
print("Timezone:", settings.timezone)
print("Email recipients:", settings.get_email_recipients())
print("\nConfig loaded successfully!")