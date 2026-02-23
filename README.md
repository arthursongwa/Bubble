# Bubble Dashboard

Dashboard de veille personnel — accessible partout, blocs modulables.

**Live** → [bubble-pink.vercel.app](https://bubble-pink.vercel.app)

## Structure

```
Bubble/
├── backend/          ← FastAPI (Railway)
│   ├── main.py
│   ├── blocks/
│   │   ├── clock.py
│   │   ├── emails.py
│   │   ├── jobs.py
│   │   ├── movies.py
│   │   └── weather.py
│   ├── requirements.txt
│   ├── Procfile
│   └── runtime.txt
└── frontend/         ← HTML statique (Vercel)
    └── index.html
```

## Variables Railway

```
EMAIL_ADDRESS     = ...
EMAIL_PASSWORD    = ...
EMAIL_MAX         = 6
JOBS_KEYWORDS     = Full Stack
JOBS_LOCATION     = France
JOBS_MAX          = 8
TMDB_API_KEY      = ...
TMDB_LANGUAGE     = fr-FR
MOVIES_MAX        = 6
WEATHER_API_KEY   = ...
WEATHER_CITY      = Tours
```

## Ajouter un bloc

1. Crée `backend/blocks/mon_bloc.py` avec une fonction `get_mon_bloc() -> dict`
2. Branche-le dans `backend/main.py` (refresh_loop + get_block)
3. Ajoute `renderMonBloc()` dans `frontend/index.html`
4. Push → Railway + Vercel redéploient automatiquement
