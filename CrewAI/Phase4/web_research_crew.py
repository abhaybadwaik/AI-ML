# # | Tool                     | What It Does                       |
# | ------------------------ | ---------------------------------- |
# | `SerperDevTool`          | Google search in real time         |
# | `ScrapeWebsiteTool`      | Reads content from any website URL |
# | `FileReadTool`           | Reads content from a local file    |
# | `FileWriterTool`         | Writes content to a local file     |
# | `DirectoryReadTool`      | Lists files in a folder            |
# | `YoutubeVideoSearchTool` | Searches YouTube videos            |
# | `PDFSearchTool`          | Reads and searches inside PDFs     |


import requests
import os
from dotenv import load_dotenv

load_dotenv()

topic = input("Enter topic to research: ")

url = "https://google.serper.dev/search"
headers = {"X-API-KEY": os.getenv("SERPER_API_KEY")}
payload = {"q": topic}

response = requests.post(url, json=payload, headers=headers)
results = response.json()

print("\n========= SEARCH RESULTS =========")
for item in results["organic"][:5]:
    print(f"\n📌 {item['title']}")
    print(f"🔗 {item['link']}")
    print(f"📝 {item.get('snippet', 'No snippet available')}")

# import os
# os.environ["OTEL_SDK_DISABLED"] = "true"

# from dotenv import load_dotenv
# from crewai import Agent, Task, Crew, Process, LLM
# from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# load_dotenv()

# # ── GET INPUT ─────────────────────────────────────────
# topic = input("Enter topic to research: ")

# # ── LLM ──────────────────────────────────────────────
# llm = LLM(model="gpt-4o-mini")

# # ── TOOLS ────────────────────────────────────────────
# search_tool = SerperDevTool()        # Google search
# scrape_tool = ScrapeWebsiteTool()    # Read website content

# # ── AGENTS ───────────────────────────────────────────

# researcher = Agent(
#     role="Senior Web Researcher",
#     goal=f"Find the latest and most accurate real-time information about {topic}",
#     backstory="""You are an expert web researcher who uses Google search 
#     to find the most current and relevant information. You always verify 
#     facts by reading actual websites.""",
#     tools=[search_tool, scrape_tool],  # 👈 Agent gets tools!
#     verbose=True,
#     llm=llm
# )

# writer = Agent(
#     role="Content Writer",
#     goal=f"Write a well-structured, factual article about {topic}",
#     backstory="""You are a skilled writer who turns research findings 
#     into clear, engaging, and accurate articles.""",
#     verbose=True,
#     llm=llm
# )

# # ── TASKS ────────────────────────────────────────────

# research_task = Task(
#     description=f"""Search the web and find the latest information about '{topic}'.
#     Use the search tool to find relevant results.
#     Use the scrape tool to read the actual content of the top websites.
#     Summarize the most important and recent facts you find.""",
#     expected_output=f"A detailed summary of the latest real-world information about {topic} with sources.",
#     agent=researcher
# )

# writing_task = Task(
#     description=f"""Using the real research provided, write a factual article about '{topic}'.
#     The article must have:
#     - A catchy title
#     - An introduction
#     - 3 main sections with real facts
#     - A conclusion
#     Keep it under 500 words.""",
#     expected_output=f"A factual, well-structured article about {topic} based on real web research.",
#     agent=writer,
#     context=[research_task],
#     output_file="Phase4/outputs/web_article.md"
# )

# # ── CREW ─────────────────────────────────────────────

# crew = Crew(
#     agents=[researcher, writer],
#     tasks=[research_task, writing_task],
#     process=Process.sequential,
#     verbose=True
# )

# # ── RUN ──────────────────────────────────────────────

# result = crew.kickoff()

# print("\n========= FINAL ARTICLE =========")
# print(result)
# print("\n✅ Article saved to Phase4/outputs/web_article.md")