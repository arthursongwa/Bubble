import os
import requests


def get_weather() -> dict:
    api_key = os.environ.get("WEATHER_API_KEY", "")
    city    = os.environ.get("WEATHER_CITY", "Paris")
    units   = os.environ.get("WEATHER_UNITS", "metric")

    if not api_key:
        return {"error": "WEATHER_API_KEY non configuré"}

    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q":     city,
                "appid": api_key,
                "units": units,
                "lang":  "fr",
            },
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()

        return {
            "city":        d["name"],
            "temp":        round(d["main"]["temp"]),
            "feels_like":  round(d["main"]["feels_like"]),
            "humidity":    d["main"]["humidity"],
            "wind":        round(d["wind"]["speed"] * 3.6),  # m/s → km/h
            "description": d["weather"][0]["description"].capitalize(),
            "icon":        d["weather"][0]["icon"],
            "error":       None,
        }
    except Exception as e:
        return {"error": str(e)}