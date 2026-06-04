import yaml
from crewai import Agent, LLM
from src.tools.search_tool import get_search_tool
from src.tools.scrape_tool import get_scrape_tool

def get_legal_compliance_analyst(llm: LLM) -> Agent:
    with open("config/agents.yaml", "r") as f:
        config = yaml.safe_load(f)["legal_compliance_analyst"]

    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        tools=[],
        llm=llm,
        verbose=False,
        memory=False,
        max_iter=5
    )