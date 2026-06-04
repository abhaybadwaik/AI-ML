from crewai import Crew, Process, LLM
import time
from src.agents import (
    get_financial_analyst,
    get_news_sentiment_analyst,
    get_legal_compliance_analyst,
    get_competitor_analyst,
    get_risk_analyst,
    get_report_generator,
    get_manager_agent
)
from src.tasks import (
    get_financial_task,
    get_news_task,
    get_legal_task,
    get_competitor_task,
    get_risk_task,
    get_report_task
)

def build_due_diligence_crew(company_name: str, llm: LLM) -> Crew:

    # ── AGENTS ──────────────────────────────────────────
    financial_analyst   = get_financial_analyst(llm)
    news_analyst        = get_news_sentiment_analyst(llm)
    legal_analyst       = get_legal_compliance_analyst(llm)
    competitor_analyst  = get_competitor_analyst(llm)
    risk_analyst        = get_risk_analyst(llm)
    report_generator    = get_report_generator(llm)
    manager             = get_manager_agent(llm)

    # ── TASKS ───────────────────────────────────────────
    financial_task   = get_financial_task(financial_analyst, company_name)
    news_task        = get_news_task(news_analyst, company_name)
    legal_task       = get_legal_task(legal_analyst, company_name)
    competitor_task  = get_competitor_task(competitor_analyst, company_name)

    risk_task = get_risk_task(
        agent=risk_analyst,
        company_name=company_name,
        context_tasks=[financial_task, news_task, legal_task, competitor_task]
    )

    report_task = get_report_task(
        agent=report_generator,
        company_name=company_name,
        context_tasks=[financial_task, news_task, legal_task, competitor_task, risk_task]
    )

    # ── CREW ────────────────────────────────────────────
    return Crew(
        agents=[
            financial_analyst,
            news_analyst,
            legal_analyst,
            competitor_analyst,
            risk_analyst,
            report_generator
        ],
        tasks=[
            financial_task,
            news_task,
            legal_task,
            competitor_task,
            risk_task,
            report_task
        ],
        manager_agent=manager,
        process=Process.hierarchical,
        manager_llm=llm,
        memory=False,
        verbose=False,
        max_rpm=3,
        task_callback=lambda _: time.sleep(30)
    )