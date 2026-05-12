from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

load_dotenv()

# Define the LLM using Groq
llm = LLM(model="groq/llama-3.3-70b-versatile")

# Step 1: Define an agent
researcher = Agent(
    role="Senior Researcher",
    goal="Find clear, accurate information about any topic",
    backstory="You are an expert researcher who always gives concise, factual answers.",
    verbose=True,
    llm=llm
)

# Step 2: Define a task
research_task = Task(
    description="Explain what CrewAI is in 3 simple sentences.",
    expected_output="A 3-sentence explanation suitable for a beginner.",
    agent=researcher
)

# Step 3: Assemble the crew
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True
)

# Step 4: Run it!
result = crew.kickoff()
print("\n========= RESULT =========")
print(result)