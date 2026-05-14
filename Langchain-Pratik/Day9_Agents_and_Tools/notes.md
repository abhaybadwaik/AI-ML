# Day 9 — Agents & Tools (Database + REST API + ReAct)

## What is the concept?
**Agents** are LLMs that can **decide which tool to use** and **when to use it** to answer a question — they reason step-by-step like a human problem-solver.  
**Tools** are functions you give to the agent (query a database, call an API, read a file) that the agent can invoke based on the question.

## Why do we use it?
A regular LLM chain is hardcoded: input → steps → output. An Agent is flexible: it reads the question, decides what tools are needed, calls them, reads the results, and then forms an answer — all autonomously.

## Real-Life Use Cases
- "What is the weather in the city where our highest-paid employee lives?" (needs DB + weather API)
- Stock market bot: gets stock price from API + reads company news from PDF
- Travel assistant: checks flight availability + hotel prices + weather simultaneously
- Your project (`combine.py`): finds engineers in DB + gets weather for their cities

---

## Part 1: Tool — SQLite Database Query (`Database.py`)

```python
import sqlite3
from langchain.tools import tool

@tool
def query_employee_database(sql_query: str) -> str:
    """Query the employee database using SQL.
    Table name is 'employees' with columns: id, name, department, salary, city.
    Use this for any questions about employees, salaries, departments."""
    
    try:
        conn = sqlite3.connect("company.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return str(results) if results else "No results found."
    except Exception as e:
        return f"Query error: {str(e)}"

# Test directly (without agent)
print(query_employee_database.invoke({"sql_query": "SELECT * FROM employees"}))
print(query_employee_database.invoke({"sql_query": "SELECT AVG(salary) FROM employees"}))
```

**Sample Database (`company.db`)**
```
| id | name   | department  | salary | city      |
|----|--------|-------------|--------|-----------|
| 1  | Pratik | Engineering | 80000  | Hyderabad |
| 2  | Rahul  | Marketing   | 60000  | Mumbai    |
| 3  | Sneha  | HR          | 55000  | Pune      |
| 4  | Amit   | Engineering | 90000  | Bangalore |
| 5  | Priya  | Sales       | 65000  | Delhi     |
```

---

## Part 2: Tool — REST API Weather (`REST_API.py`)

```python
import requests
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city. Use this when user asks about weather."""
    
    # Step 1: Get GPS coordinates for the city
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(geo_url).json()
    
    if not geo_response.get("results"):
        return f"City '{city}' not found."
    
    lat = geo_response["results"][0]["latitude"]
    lon = geo_response["results"][0]["longitude"]
    
    # Step 2: Get weather data
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,precipitation"
    weather = requests.get(weather_url).json()["current"]
    
    return f"Weather in {city}: Temp {weather['temperature_2m']}°C, Wind {weather['wind_speed_10m']} km/h, Rain {weather['precipitation']} mm"

print(get_weather.invoke({"city": "Hyderabad"}))
print(get_weather.invoke({"city": "Mumbai"}))
```

> Uses **Open-Meteo** (free API, no key needed) — geocoding API finds lat/lon, then weather API fetches data.

---

## Part 3: Full ReAct Agent with Both Tools (`combine.py`)

**ReAct = Reason + Act** — the agent thinks step by step, uses tools, observes results, and repeats until it has the final answer.

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

tools = [query_employee_database, get_weather]

# ReAct prompt — the agent MUST follow this exact format
prompt = PromptTemplate.from_template("""
You are a helpful assistant with access to an employee database and weather.

You have access to these tools: {tools}

Use this EXACT format:

Question: the input question
Thought: what should I do next?
Action: tool name (must be one of [{tool_names}])
Action Input: input to the tool
Observation: result from the tool
... (repeat Thought/Action/Action Input/Observation)
Thought: I now know the final answer
Final Answer: the complete answer

Question: {input}
Thought: {agent_scratchpad}
""")

agent = create_react_agent(llm=chat, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,      # shows the agent's thinking process
    max_iterations=8,  # safety limit (prevents infinite loops)
    handle_parsing_errors=True
)

result = agent_executor.invoke({
    "input": "Who are the engineers in the company and what is the weather in their cities?"
})

print("FINAL ANSWER:", result["output"])
```

**Agent's reasoning trace (verbose=True shows this):**
```
Question: Who are the engineers and what is the weather in their cities?
Thought: I need to find engineers in the database first
Action: query_employee_database
Action Input: SELECT name, city FROM employees WHERE LOWER(department) = 'engineering'
Observation: Pratik is in Hyderabad | Amit is in Bangalore

Thought: Now I need weather for Hyderabad
Action: get_weather
Action Input: Hyderabad
Observation: Hyderabad: Temp 38°C, Wind 12 km/h, Rain 0 mm

Thought: Now I need weather for Bangalore
Action: get_weather
Action Input: Bangalore
Observation: Bangalore: Temp 29°C, Wind 8 km/h, Rain 0 mm

Thought: I have all information needed
Final Answer: The engineers are Pratik (Hyderabad) and Amit (Bangalore).
Weather in Hyderabad: 38°C, Wind 12 km/h.
Weather in Bangalore: 29°C, Wind 8 km/h.
```

---

## Important Keywords
| Keyword | Meaning |
|---------|---------|
| `@tool` | Decorator that makes a Python function usable as a LangChain tool |
| `docstring` | Description inside `"""..."""` — the agent reads this to know when to use the tool |
| `create_react_agent()` | Creates an agent that uses the ReAct (Reason + Act) framework |
| `AgentExecutor` | Wrapper that runs the agent in a loop until it gets a final answer |
| `verbose=True` | Shows the agent's thinking process step by step |
| `max_iterations` | Prevents the agent from looping forever |
| `handle_parsing_errors=True` | Recovers gracefully if the LLM makes a formatting mistake |
| `agent_scratchpad` | Internal notepad where the agent writes its Thought/Action/Observation |
| `ReAct` | Reasoning + Acting — the pattern of: think → act → observe → repeat |
| `{tool_names}` | Auto-filled list of available tool names in the prompt |

---

## Tool Docstring Matters!

The **docstring** of a tool is what the agent reads to understand what the tool does and when to use it. Write clear, specific descriptions:

```python
@tool
def query_employee_database(sql_query: str) -> str:
    """Query the employee database using SQL.
    Table name is 'employees' with columns: id, name, department, salary, city.
    Use this for any questions about employees, salaries, departments."""
    ...
```

> The agent reads "Use this for any questions about employees" and knows to call this tool for HR questions. 🧠

---

## Beginner-Friendly Summary
An Agent is like a smart detective:
- **Tools** = the detective's toolkit (magnifying glass, database access, phone calls)
- **ReAct** = the detective's method: *think → look for clues → note what was found → think again*
- **AgentExecutor** = the detective's case file (keeps track of all steps)
- **Final Answer** = the detective's conclusion after gathering all evidence

The agent DECIDES what to do — you don't hardcode the steps. That's the power! 🕵️
