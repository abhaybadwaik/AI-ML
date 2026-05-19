from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

# ── LLM ──────────────────────────────────────────────
llm = LLM(model="groq/llama-3.3-70b-versatile")

# ── AGENTS ───────────────────────────────────────────

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find accurate and detailed information about the given topic",
    backstory="""You are an experienced research analyst with 10 years of 
    experience. You always find the most relevant, factual, and up-to-date 
    information. You present findings in a clear and structured way.""",
    verbose=True,
    llm=llm
)

writer = Agent(
    role="Content Writer",
    goal="Write engaging and informative blog articles based on research provided",
    backstory="""You are a skilled content writer who specializes in turning 
    complex research into easy-to-read blog posts. Your writing is clear, 
    engaging, and always structured with a proper introduction, body and conclusion.""",
    verbose=True,
    llm=llm
)

editor = Agent(
    role="Senior Editor",
    goal="Review and improve articles for clarity, grammar and overall quality",
    backstory="""You are a meticulous senior editor with an eye for detail. 
    You improve articles by fixing grammar, improving sentence structure, 
    and ensuring the content flows naturally from start to finish.""",
    verbose=True,
    llm=llm
)

# ── TASKS ────────────────────────────────────────────

research_task = Task(
    description="""Research the topic: 'What is Artificial Intelligence and 
    how is it changing the world?'. Find key facts, real examples, and 
    important trends. Present findings in bullet points.""",
    expected_output="A structured list of key facts, examples and trends about AI.",
    agent=researcher
)

writing_task = Task(
    description="""Using the research provided, write a blog article about 
    Artificial Intelligence. The article should have:
    - A catchy title
    - An introduction
    - 3 main sections
    - A conclusion
    Keep it simple and under 400 words.""",
    expected_output="A complete blog article about AI with title, intro, body and conclusion.",
    agent=writer,
    context=[research_task]  # Writer gets the researcher's output!
)

editing_task = Task(
    description="""Review the blog article written by the writer. 
    Fix any grammar issues, improve clarity, and make sure it reads 
    naturally. Return the final polished version.""",
    expected_output="A polished, publication-ready blog article.",
    agent=editor,
    context=[writing_task]  # Editor gets the writer's output!
)

# ── CREW ─────────────────────────────────────────────

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,  # Tasks run one after another
    verbose=True
)

# ── RUN ──────────────────────────────────────────────

result = crew.kickoff()
print("\n========= FINAL ARTICLE =========")
print(result)

#"I built a 3-agent autonomous content pipeline where a Researcher, Writer and Editor AI agents collaborate sequentially — each agent reads the previous agent's output and builds on it — to produce a publication-ready article with zero human intervention."

# IndustryUse CaseMediaResearcher finds news → Writer writes article → Editor polishes itMarketingResearcher finds competitor data → Strategist makes plan → Copywriter writes campaignSoftwareAnalyst writes requirements → Developer writes code → Reviewer checks codeReal EstateAgent researches property market → Agent writes listing description → Agent creates email to buyerEducationAgent researches topic → Agent creates lesson plan → Agent creates quiz