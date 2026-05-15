import os
os.environ["OTEL_SDK_DISABLED"] = "true"

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from datetime import datetime

load_dotenv()

topic = input("Enter your topic: ")

llm = LLM(model="groq/llama-3.3-70b-versatile")

# ── STATE ─────────────────────────────────────────────
class ContentState(BaseModel):
    topic: str = ""
    research: str = ""
    article: str = ""
    timestamp: str = ""

# ── FLOW ──────────────────────────────────────────────
class ContentFlow(Flow[ContentState]):

    @start()
    def set_topic(self):
        print(f"\n🚀 Starting Content Flow for: {topic}")
        self.state.topic = topic
        self.state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    @listen(set_topic)
    def run_research(self):
        print(f"\n🔍 Researching: {self.state.topic}")

        researcher = Agent(
            role="Senior Researcher",
            goal=f"Research {self.state.topic} thoroughly",
            backstory="Expert researcher with 10 years experience.",
            verbose=False,
            llm=llm
        )

        task = Task(
            description=f"Research '{self.state.topic}' and provide key facts in bullet points.",
            expected_output="Detailed bullet points about the topic.",
            agent=researcher
        )

        crew = Crew(
            agents=[researcher],
            tasks=[task],
            verbose=False
        )

        result = crew.kickoff()
        self.state.research = str(result)
        print("✅ Research completed!")

    @listen(run_research)
    def run_writing(self):
        print(f"\n✍️ Writing article about: {self.state.topic}")

        writer = Agent(
            role="Content Writer",
            goal=f"Write an article about {self.state.topic}",
            backstory="Expert writer who creates engaging content.",
            verbose=False,
            llm=llm
        )

        task = Task(
            description=f"""Write a blog article about '{self.state.topic}'.
            Use this research: {self.state.research}
            Include: title, introduction, 3 sections, conclusion.""",
            expected_output="Complete blog article.",
            agent=writer
        )

        crew = Crew(
            agents=[writer],
            tasks=[task],
            verbose=False
        )

        result = crew.kickoff()
        self.state.article = str(result)
        print("✅ Article written!")

    @listen(run_writing)
    def save_output(self):
        print(f"\n💾 Saving output...")

        os.makedirs("Phase5/outputs", exist_ok=True)

        filename = f"Phase5/outputs/{self.state.topic.replace(' ', '_')}.md"

        with open(filename, "w") as f:
            f.write(f"# {self.state.topic}\n")
            f.write(f"Generated: {self.state.timestamp}\n\n")
            f.write("## Research\n")
            f.write(self.state.research)
            f.write("\n\n## Article\n")
            f.write(self.state.article)

        print(f"✅ Saved to {filename}")
        print(f"\n========= FINAL ARTICLE =========")
        print(self.state.article)

# ── RUN ───────────────────────────────────────────────
flow = ContentFlow()
flow.kickoff()