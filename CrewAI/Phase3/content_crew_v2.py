import os
os.environ["OTEL_SDK_DISABLED"] = "true"

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

load_dotenv()

# ── GET INPUT ─────────────────────────────────────────
topic = input("Enter topic to research: ")

# ── LLM ──────────────────────────────────────────────
llm = LLM(model="groq/llama-3.1-8b-instant")

# ── TOOLS ────────────────────────────────────────────
search_tool = SerperDevTool()

# ── AGENTS ───────────────────────────────────────────

researcher = Agent(
    role="Senior Web Researcher",
    goal=f"Find the latest and most accurate real-time information about {topic}",
    backstory="""You are an expert web researcher who uses Google search 
    to find the most current and relevant information.""",
    tools=[search_tool],
    verbose=False,
    llm=llm
)

writer = Agent(
    role="Content Writer",
    goal=f"Write a well-structured, factual article about {topic}",
    backstory="""You are a skilled writer who turns research findings 
    into clear, engaging, and accurate articles.""",
    verbose=False,
    llm=llm
)

# ── TASKS ────────────────────────────────────────────

research_task = Task(
    description=f"""Search the web and find the latest information about '{topic}'.
    Use the search tool to find relevant results.
    Summarize the most important and recent facts you find.""",
    expected_output=f"A detailed summary of the latest real-world information about {topic} with sources.",
    agent=researcher
)

writing_task = Task(
    description=f"""Using the real research provided, write a factual article about '{topic}'.
    The article must have:
    - A catchy title
    - An introduction
    - 3 main sections with real facts
    - A conclusion
    Keep it under 500 words.""",
    expected_output=f"A factual, well-structured article about {topic} based on real web research.",
    agent=writer,
    context=[research_task],
    output_file="Phase4/outputs/web_article.md"
)

# ── CREW ─────────────────────────────────────────────

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=False
)

# ── RUN ──────────────────────────────────────────────

print("\n🔍 Researching and writing your article... please wait!\n")
result = crew.kickoff()

print("\n========= FINAL ARTICLE =========")
print(result)
print("\n✅ Article saved to Phase4/outputs/web_article.md")