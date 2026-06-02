import yaml
from crewai import Agent, LLM
from src.tools.search_tool import get_search_tool
from src.tools.scrape_tool import get_scrape_tool
from src.tools.custom_tools import convert_currency

def get_financial_analyst(llm: LLM) -> Agent:
    with open("config/agents.yaml", "r") as f:
        config = yaml.safe_load(f)["financial_analyst"]

    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        tools=[get_search_tool(), get_scrape_tool(), convert_currency],
        llm=llm,
        verbose=False,
        memory=True,
        max_iter=5
    )