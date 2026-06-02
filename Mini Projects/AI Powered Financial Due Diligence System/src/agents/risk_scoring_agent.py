import yaml
from crewai import Agent, LLM
from src.tools.custom_tools import calculate_risk_score

def get_risk_analyst(llm: LLM) -> Agent:
    with open("config/agents.yaml", "r") as f:
        config = yaml.safe_load(f)["risk_analyst"]

    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        tools=[calculate_risk_score],
        llm=llm,
        verbose=False,
        memory=True,
        max_iter=5
    )