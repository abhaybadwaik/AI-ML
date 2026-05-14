# run by this command: python Phase3/content_crew_v2.py
import os
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

# ── GET INPUT ─────────────────────────────────────────
topic = input("Enter the topic you want to research and write about: ")

# rest of code stays same...

# ── LLM ──────────────────────────────────────────────
llm = LLM(model="groq/llama-3.3-70b-versatile")

# ── AGENTS ───────────────────────────────────────────

researcher = Agent(
    role="Senior Research Analyst",
    goal=f"Find accurate and detailed information about {topic}",
    backstory="""You are an experienced research analyst with 10 years of 
    experience. You always find the most relevant, factual, and up-to-date 
    information. You present findings in a clear and structured way.""",
    verbose=True,
    llm=llm
)

writer = Agent(
    role="Content Writer",
    goal=f"Write an engaging blog article about {topic} based on research provided",
    backstory="""You are a skilled content writer who specializes in turning 
    complex research into easy-to-read blog posts. Your writing is clear, 
    engaging, and always structured with a proper introduction, body and conclusion.""",
    verbose=True,
    llm=llm
)

editor = Agent(
    role="Senior Editor",
    goal=f"Review and polish the article about {topic} for clarity and quality",
    backstory="""You are a meticulous senior editor with an eye for detail. 
    You improve articles by fixing grammar, improving sentence structure, 
    and ensuring the content flows naturally from start to finish.""",
    verbose=True,
    llm=llm
)

# ── TASKS ────────────────────────────────────────────

research_task = Task(
    description=f"""Research the topic: '{topic}'.
    Find key facts, real examples, statistics, and important trends.
    Present your findings in clear bullet points.""",
    expected_output=f"A structured list of key facts, examples and trends about {topic}.",
    agent=researcher
)

writing_task = Task(
    description=f"""Using the research provided, write a blog article about '{topic}'.
    The article must have:
    - A catchy title
    - An engaging introduction
    - 3 well-structured main sections
    - A strong conclusion
    Keep it under 500 words and make it beginner-friendly.""",
    expected_output=f"A complete blog article about {topic} with title, intro, 3 sections and conclusion.",
    agent=writer,
    context=[research_task]
)

editing_task = Task(
    description=f"""Review and polish the blog article about '{topic}'.
    Fix grammar, improve clarity, enhance flow.
    Return the final publication-ready version.""",
    expected_output=f"A polished, publication-ready blog article about {topic}.",
    agent=editor,
    context=[writing_task],
    output_file="Phase3/outputs/article.md"
)

# ── CREW ─────────────────────────────────────────────

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,
    verbose=True
)

# ── RUN ──────────────────────────────────────────────

result = crew.kickoff()

print("\n========= FINAL ARTICLE =========")
print(result)
print("\n✅ Article saved to Phase3/outputs/article.md")