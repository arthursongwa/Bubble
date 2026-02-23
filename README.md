# Bubble Dashboard — Web App

Frontend statique + Backend FastAPI. Déployable gratuitement en 10 minutes.

---

## Structure

```
bubble/
├── backend/          ← FastAPI (Railway)
│   ├── main.py
│   ├── blocks/
│   │   ├── clock.py
│   │   ├── emails.py
│   │   ├── jobs.py
│   │   └── movies.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/         ← HTML statique (Vercel / Netlify)
    └── index.html
```

---

## Déploiement Backend — Railway

1. Va sur **railway.app** → New Project → Deploy from GitHub
2. Pointe vers le dossier `backend/`
3. Railway détecte automatiquement Python via `requirements.txt`
4. Dans **Variables** (onglet Variables de ton projet Railway), ajoute :

```
EMAIL_ADDRESS    = tonemail@gmail.com
EMAIL_PASSWORD   = xxxx xxxx xxxx xxxx
EMAIL_MAX        = 6
JOBS_KEYWORDS    = Full Stack
JOBS_LOCATION    = France
JOBS_MAX         = 8
TMDB_API_KEY     = ta_cle_tmdb
TMDB_LANGUAGE    = fr-FR
MOVIES_MAX       = 6
```

5. Dans **Settings** → Start Command :
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

6. Note l'URL générée : `https://ton-projet.railway.app`

---

## Déploiement Frontend — Vercel

1. Va sur **vercel.com** → New Project → Import Git ou drag & drop le dossier `frontend/`
2. Dans `frontend/index.html`, ligne ~195, remplace :
```javascript
: 'https://TON-PROJET.railway.app';
```
par ton URL Railway réelle.

3. Deploy → l'app est accessible depuis n'importe où.

---

## Test local

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # remplis tes vraies valeurs
python main.py         # démarre sur http://localhost:8000
```

Ouvre `frontend/index.html` dans ton navigateur — la grille 3 colonnes s'affiche directement.

---

## Ajouter un nouveau bloc

1. Crée `backend/blocks/mon_bloc.py` avec une fonction `get_mon_bloc() -> dict`
2. Dans `backend/main.py`, importe et branche dans `refresh_loop()` et `get_block()`
3. Dans `frontend/index.html`, ajoute le bloc dans `BLOCKS_META` et une fonction `renderMonBloc()`
4. Redéploie Railway → le bloc apparaît

---

## Sécurité

Le dashboard est public (pas de login). Pour le protéger :
- Ajoute un middleware d'auth basique dans FastAPI
- Ou utilise Vercel Edge Middleware pour un mot de passe simple