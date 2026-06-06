from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# print(f"DEBUG KEY: {ANTHROPIC_API_KEY}") 


MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 8096

SYSTEM_PROMPT = """You are Claude, an AI assistant made by Anthropic. 
You are helpful, harmless, and honest. 
Answer clearly and concisely."""