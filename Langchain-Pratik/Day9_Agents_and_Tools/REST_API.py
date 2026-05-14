import requests
from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city. Use this when user asks about weather."""
    
    # Using Open-Meteo free API (no API key needed)
    # First get coordinates for city
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(geo_url).json()
    
    if not geo_response.get("results"):
        return f"City '{city}' not found."
    
    lat = geo_response["results"][0]["latitude"]
    lon = geo_response["results"][0]["longitude"]
    
    # Get weather
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,precipitation"
    weather = requests.get(weather_url).json()["current"]
    
    return f"Weather in {city}: Temperature {weather['temperature_2m']}°C, Wind Speed {weather['wind_speed_10m']} km/h, Precipitation {weather['precipitation']} mm"

# Test tool directly
print(get_weather.invoke({"city": "Hyderabad"}))
print(get_weather.invoke({"city": "Mumbai"}))