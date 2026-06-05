import yaml
from crewai import Agent, LLM

def get_financial_analyst(llm: LLM) -> Agent:
    with open("config/agents.yaml", "r") as f:
        config = yaml.safe_load(f)["financial_analyst"]

    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        tools=[],
        llm=llm,
        verbose=False,
        memory=False,
        max_iter=3
    )