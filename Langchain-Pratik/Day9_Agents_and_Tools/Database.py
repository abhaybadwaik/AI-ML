import sqlite3
from langchain.tools import tool

# Create sample database
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
    
    cursor.executemany(
        "INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
        employees
    )
    conn.commit()
    conn.close()
    print("Database created with sample data!")

create_sample_db()

# Tool to query database
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
        
        if not results:
            return "No results found."
        
        return str(results)
    except Exception as e:
        return f"Query error: {str(e)}"

# Test directly
print(query_employee_database.invoke({"sql_query": "SELECT * FROM employees"}))
print()
print(query_employee_database.invoke({"sql_query": "SELECT AVG(salary) FROM employees"}))

