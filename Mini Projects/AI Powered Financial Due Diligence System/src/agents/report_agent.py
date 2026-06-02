import yaml
from crewai import Agent, LLM

def get_report_generator(llm: LLM) -> Agent:
    with open("config/agents.yaml", "r") as f:
        config = yaml.safe_load(f)["report_generator"]

    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        tools=[],
        llm=llm,
        verbose=False,
        memory=True,
        max_iter=5
    )