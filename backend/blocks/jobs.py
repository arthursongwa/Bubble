"""
Jobs — scraping LinkedIn (sans Selenium pour Railway, via requests + BS4).
Sur Railway, Selenium headless est complexe à déployer.
On utilise l'API publique LinkedIn Jobs RSS ou le scraping léger avec requests.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime, timedelta
import re


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def _parse_date(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    if "seconde" in text or "minute" in text:
        return "À l'instant"
    m = re.search(r"(\d+)\s*heure", text)
    if m:
        return f"Il y a {m.group(1)}h"
    m = re.search(r"(\d+)\s*jour", text)
    if m:
        d = int(m.group(1))
        return "Hier" if d == 1 else f"Il y a {d}j"
    m = re.search(r"(\d+)\s*semaine", text)
    if m:
        return f"Il y a {m.group(1)} sem."
    return text


def get_jobs() -> dict:
    keywords = os.environ.get("JOBS_KEYWORDS", "Full Stack")
    location = os.environ.get("JOBS_LOCATION", "France")
    max_n    = int(os.environ.get("JOBS_MAX", "8"))

    url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?keywords={quote(keywords)}&location={quote(location)}"
        f"&f_TPR=r86400&sortBy=DD"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select("div.base-card")[:max_n]

        jobs = []
        for card in cards:
            title_el   = card.select_one("h3.base-search-card__title")
            company_el = card.select_one("h4.base-search-card__subtitle")
            location_el= card.select_one("span.job-search-card__location")
            date_el    = card.select_one("time")
            link_el    = card.select_one("a.base-card__full-link")

            title   = title_el.get_text(strip=True)   if title_el    else "N/A"
            company = company_el.get_text(strip=True)  if company_el  else "N/A"
            loc     = location_el.get_text(strip=True) if location_el else ""
            date    = _parse_date(date_el.get_text(strip=True) if date_el else "")
            link    = link_el.get("href", "")          if link_el     else ""

            if title and title != "N/A":
                jobs.append({
                    "title":    title,
                    "company":  company,
                    "location": loc,
                    "date":     date,
                    "link":     link,
                })

        return {"jobs": jobs, "total": len(jobs), "keywords": keywords, "location": location, "error": None}

    except Exception as e:
        return {"error": str(e), "jobs": [], "total": 0}