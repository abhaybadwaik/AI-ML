import os
from datetime import datetime
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from crewai import LLM
from src.crew.due_diligence_crew import build_due_diligence_crew


# ── STATE ────────────────────────────────────────────────
class DueDiligenceState(BaseModel):
    company_name: str = ""
    started_at: str = ""
    completed_at: str = ""
    report_path: str = ""
    status: str = ""
    final_output: str = ""


# ── FLOW ─────────────────────────────────────────────────
class DueDiligenceFlow(Flow[DueDiligenceState]):

    def __init__(self, company_name: str, llm: LLM):
        super().__init__()
        self.company_name = company_name
        self.llm = llm

    @start()
    def initialize(self):
        print("\n" + "="*60)
        print("   AI POWERED FINANCIAL DUE DILIGENCE SYSTEM")
        print("="*60)
        print(f"\n🏢 Company        : {self.company_name}")
        print(f"📅 Started At     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 LLM            : Claude Sonnet 4.5")
        print(f"👥 Agents         : 7 Specialized AI Analysts")
        print(f"📋 Tasks          : 6 Due Diligence Tasks")
        print(f"⚙️  Process        : Hierarchical (Manager Coordinated)")
        print("="*60)
        print("\n⏳ Analysis in progress... This may take a few minutes.\n")

        self.state.company_name = self.company_name
        self.state.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state.status = "running"

    @listen(initialize)
    def run_analysis(self):
        print("🔍 Phase 1 — Financial Analysis")
        print("📰 Phase 2 — News & Sentiment Analysis")
        print("⚖️  Phase 3 — Legal & Compliance Analysis")
        print("🏆 Phase 4 — Competitive Analysis")
        print("⚠️  Phase 5 — Risk Scoring")
        print("📄 Phase 6 — Report Generation")
        print("\n🤖 Agents are working...\n")

        crew = build_due_diligence_crew(
            company_name=self.state.company_name,
            llm=self.llm
        )

        result = crew.kickoff()
        self.state.final_output = str(result)
        self.state.status = "completed"

    @listen(run_analysis)
    def finalize(self):
        self.state.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        company_slug = self.state.company_name.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.state.report_path = f"outputs/reports/{company_slug}_{timestamp}.md"

        print("\n" + "="*60)
        print("   ✅ DUE DILIGENCE ANALYSIS COMPLETE")
        print("="*60)
        print(f"\n🏢 Company        : {self.state.company_name}")
        print(f"📅 Started At     : {self.state.started_at}")
        print(f"✅ Completed At   : {self.state.completed_at}")
        print(f"📄 Report saved to: outputs/reports/")
        print(f"📊 Status         : {self.state.status.upper()}")
        print("\n" + "="*60)
        print("\n📋 FINAL REPORT PREVIEW:")
        print("="*60)
        print(self.state.final_output)