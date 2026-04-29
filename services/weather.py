import os
import requests

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "Kochi")

def get_weather(city=None):
    city = city or CITY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    r = requests.get(url).json()

    if r.get("cod") != 200:
        return "Weather data not available."

    temp = r["main"]["temp"]
    desc = r["weather"][0]["description"]

    return f"Weather in {city}: {temp}°C, {desc}"
