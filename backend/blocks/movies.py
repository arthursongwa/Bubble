import os
import requests
from datetime import datetime, timedelta


TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE  = "https://image.tmdb.org/t/p/w200"


def get_movies() -> dict:
    api_key  = os.environ.get("TMDB_API_KEY", "")
    language = os.environ.get("TMDB_LANGUAGE", "fr-FR")
    max_n    = int(os.environ.get("MOVIES_MAX", "6"))

    if not api_key:
        return {"error": "TMDB_API_KEY non configuré", "movies": []}

    today = datetime.today()
    date_from = (today - timedelta(days=14)).strftime("%Y-%m-%d")
    date_to   = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        resp = requests.get(
            f"{TMDB_BASE}/discover/movie",
            params={
                "api_key":                    api_key,
                "language":                   language,
                "sort_by":                    "primary_release_date.desc",
                "primary_release_date.gte":   date_from,
                "primary_release_date.lte":   date_to,
                "with_release_type":          "3|2",
                "page":                       1,
            },
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])[:max_n]

        movies = []
        for m in results:
            movies.append({
                "title":    m.get("title", ""),
                "date":     m.get("release_date", ""),
                "rating":   round(m.get("vote_average", 0), 1),
                "poster":   IMG_BASE + m["poster_path"] if m.get("poster_path") else None,
                "overview": m.get("overview", "")[:120] + "…" if m.get("overview") else "",
                "id":       m.get("id"),
            })

        return {"movies": movies, "total": len(movies), "error": None}

    except Exception as e:
        return {"error": str(e), "movies": []}