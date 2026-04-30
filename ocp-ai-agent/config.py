from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    # LLM - Groq
    groq_api_key: str
    llm_model: str = "llama-3.3-70b-versatile"

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    email_from: str
    email_to: str

    # SSH to OCP Server
    ocp_ssh_host: str
    ocp_ssh_user: str
    ocp_ssh_password: str
    ocp_kubeconfig: str

    # Scheduler
    interval_minutes: int = 15
    timezone: str = "Asia/Kolkata"

    def get_email_recipients(self) -> List[str]:
        return json.loads(self.email_to)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()