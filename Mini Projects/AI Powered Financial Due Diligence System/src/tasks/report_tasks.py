import yaml
from crewai import Task, Agent
from datetime import datetime

def get_report_task(agent: Agent, company_name: str, context_tasks: list) -> Task:
    with open("config/tasks.yaml", "r") as f:
        config = yaml.safe_load(f)["report_generation_task"]

    filename = f"outputs/reports/{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"

    return Task(
        description=config["description"].replace("{company_name}", company_name),
        expected_output=config["expected_output"].replace("{company_name}", company_name),
        agent=agent,
        context=context_tasks,
        output_file=filename
    )