import requests
import sqlite3
from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# FIX 1 — Use larger model, much better at ReAct
chat = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key="YOUR_GROQ_API-KEY"
)

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city. Returns temperature, wind speed and rainfall."""
    try:
        city = city.strip()
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url).json()

        if not geo_response.get("results"):
            return f"City '{city}' not found."

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,precipitation"
        weather = requests.get(weather_url).json()["current"]

        return f"{city}: Temp {weather['temperature_2m']}°C, Wind {weather['wind_speed_10m']} km/h, Rain {weather['precipitation']} mm"

    except Exception as e:
        return f"Weather error: {str(e)}"


def create_sample_db():
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary INTEGER,
            city TEXT
        )
    """)
    cursor.execute("DELETE FROM employees")
    employees = [
        (1, "Pratik", "Engineering", 80000, "Hyderabad"),
        (2, "Rahul", "Marketing", 60000, "Mumbai"),
        (3, "Sneha", "HR", 55000, "Pune"),
        (4, "Amit", "Engineering", 90000, "Bangalore"),
        (5, "Priya", "Sales", 65000, "Delhi"),
    ]
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", employees)
    conn.commit()
    conn.close()

create_sample_db()


@tool
def query_employee_database(sql_query: str) -> str:
    """
    Run SQL query on the employees table.
    Table has columns: id, name, department, salary, city.
    Always use LOWER() for text comparisons.
    Example: SELECT name, city FROM employees WHERE LOWER(department) = 'engineering'
    """
    try:
        conn = sqlite3.connect("company.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()

        if not results:
            return "No results found."

        formatted = []
        for row in results:
            if len(row) == 2:
                formatted.append(f"{row[0]} is in {row[1]}")
            elif len(row) == 1:
                formatted.append(str(row[0]))
            else:
                formatted.append(str(row))

        return " | ".join(formatted)

    except Exception as e:
        return f"SQL Error: {str(e)}"


tools = [query_employee_database, get_weather]

# FIX 2 — Clean simple prompt, no excessive warnings
prompt = PromptTemplate.from_template("""
You are a helpful assistant with access to an employee database and weather information.

You have access to these tools:
{tools}

Use this exact format:

Question: the input question
Thought: think about what to do next
Action: the tool to use, must be one of [{tool_names}]
Action Input: the input to the tool
Observation: the result of the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the complete answer to the question

Important: After getting all the information you need, always end with Final Answer.

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

agent = create_react_agent(llm=chat, tools=tools, prompt=prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=8,
    handle_parsing_errors=True
)

print("\nAGENT READY\n")

result = agent_executor.invoke({
    "input": "Who are the engineers in the company and what is the weather in their cities?"
})

print("\nFINAL ANSWER:\n", result["output"])
