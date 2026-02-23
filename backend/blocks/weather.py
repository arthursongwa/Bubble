"""
Bloc Météo — Données OpenWeatherMap.
Nécessite une clé API gratuite sur openweathermap.org
Config : { "city": "Paris", "api_key": "..." }
"""

import requests
from core.base_block import BaseBlock
from core.theme import THEME


WEATHER_ICONS = {
    "Clear": "☀",
    "Clouds": "☁",
    "Rain": "🌧",
    "Drizzle": "🌦",
    "Thunderstorm": "⛈",
    "Snow": "❄",
    "Mist": "🌫",
    "Fog": "🌫",
    "Haze": "🌫",
}


class WeatherBlock(BaseBlock):

    BLOCK_ID = "weather"
    BLOCK_TITLE = "Météo"
    REFRESH_MS = 10 * 60 * 1_000   # 10 minutes
    MIN_WIDTH = 240
    MIN_HEIGHT = 180

    def fetch(self) -> dict:
        api_key = self.config.get("api_key", "")
        city = self.config.get("city", "Paris")

        if not api_key or api_key == "YOUR_OPENWEATHER_KEY":
            return {"error": "Clé API manquante dans config.yaml"}

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={api_key}&units=metric&lang=fr"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()

        condition = d["weather"][0]["main"]
        return {
            "city": city,
            "temp": round(d["main"]["temp"]),
            "feels_like": round(d["main"]["feels_like"]),
            "humidity": d["main"]["humidity"],
            "description": d["weather"][0]["description"].capitalize(),
            "icon": WEATHER_ICONS.get(condition, "◌"),
            "wind": round(d["wind"]["speed"] * 3.6),  # m/s -> km/h
        }

    def render(self, data: dict):
        if "error" in data:
            self.add_label(data["error"], size=11, color=THEME["warning"])
            return

        # Icône + température
        self.add_row(
            data["city"],
            f"{data['icon']}  {data['temp']}°C",
            THEME["accent"]
        )
        self.add_row("Ressenti", f"{data['feels_like']}°C")
        self.add_row("Humidité", f"{data['humidity']}%")
        self.add_row("Vent", f"{data['wind']} km/h")
        self.add_label(data["description"], size=10, color=THEME["text_dim"])
