import urllib.request
import json

url = "https://api.open-meteo.com/v1/forecast?latitude=39.35&longitude=-84.31&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto&temperature_unit=fahrenheit"

with urllib.request.urlopen(url) as response:
    data = json.load(response)

print("Current temp (°F):", data["current_weather"]["temperature"])
print("High (°F):", data["daily"]["temperature_2m_max"][0])
print("Low  (°F):", data["daily"]["temperature_2m_min"][0])
