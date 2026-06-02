import yaml
from crewai import Task, Agent

def get_legal_task(agent: Agent, company_name: str) -> Task:
    with open("config/tasks.yaml", "r") as f:
        config = yaml.safe_load(f)["legal_compliance_task"]

    return Task(
        description=config["description"].replace("{company_name}", company_name),
        expected_output=config["expected_output"].replace("{company_name}", company_name),
        agent=agent
    )