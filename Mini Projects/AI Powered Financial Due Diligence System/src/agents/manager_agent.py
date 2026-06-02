import yaml
from crewai import Agent, LLM

def get_manager_agent(llm: LLM) -> Agent:
    with open("config/agents.yaml", "r") as f:
        config = yaml.safe_load(f)["manager"]

    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        tools=[],
        llm=llm,
        verbose=False,
        allow_delegation=True,
        max_iter=5
    )