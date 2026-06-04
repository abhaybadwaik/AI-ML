import os
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

from dotenv import load_dotenv
from crewai import LLM
from src.flows.due_diligence_flow import DueDiligenceFlow

load_dotenv()

def main():
    print("\n" + "="*60)
    print("   AI POWERED FINANCIAL DUE DILIGENCE SYSTEM")
    print("   Powered by CrewAI + Claude")
    print("="*60)

    company_name = input("\n🏢 Enter Company Name for Due Diligence: ").strip()

    if not company_name:
        print("❌ Company name cannot be empty!")
        return

    llm = LLM(
    model="anthropic/claude-3-5-sonnet-20241022", # Added provider prefix
    temperature=0.3,
    max_tokens=4000
    )

    flow = DueDiligenceFlow(
        company_name=company_name,
        llm=llm
    )

    flow.kickoff()

if __name__ == "__main__":
    main()