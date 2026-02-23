"""
Bubble Dashboard — FastAPI Backend
Déploiement : Railway (python main.py ou uvicorn main:app)
"""

import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from blocks.clock import get_clock
from blocks.emails import get_emails
from blocks.jobs import get_jobs
from blocks.movies import get_movies


# ── Cache in-memory ───────────────────────────────────────────────────────────
cache: dict = {}
clients: list[WebSocket] = []


async def broadcast(block_id: str, data: dict):
    payload = json.dumps({"block": block_id, "data": data})
    dead = []
    for ws in clients:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.remove(ws)


async def refresh_loop():
    """Boucle de refresh en arrière-plan."""
    INTERVALS = {
        "clock":  1,
        "emails": 120,
        "jobs":   3600,
        "movies": 3600,
    }
    counters = {k: v for k, v in INTERVALS.items()}

    while True:
        await asyncio.sleep(1)

        for block_id, interval in INTERVALS.items():
            counters[block_id] -= 1
            if counters[block_id] <= 0:
                counters[block_id] = interval
                try:
                    if block_id == "clock":
                        data = get_clock()
                    elif block_id == "emails":
                        data = await asyncio.to_thread(get_emails)
                    elif block_id == "jobs":
                        data = await asyncio.to_thread(get_jobs)
                    elif block_id == "movies":
                        data = await asyncio.to_thread(get_movies)
                    else:
                        continue

                    cache[block_id] = data
                    await broadcast(block_id, data)
                except Exception as e:
                    print(f"[Refresh] Erreur {block_id}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(refresh_loop())
    yield
    task.cancel()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Bubble Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST endpoints ────────────────────────────────────────────────────────────
@app.get("/api/{block_id}")
async def get_block(block_id: str):
    if block_id in cache:
        return JSONResponse({"ok": True, "data": cache[block_id]})

    # Premier appel — fetch immédiat
    try:
        if block_id == "clock":
            data = get_clock()
        elif block_id == "emails":
            data = await asyncio.to_thread(get_emails)
        elif block_id == "jobs":
            data = await asyncio.to_thread(get_jobs)
        elif block_id == "movies":
            data = await asyncio.to_thread(get_movies)
        else:
            return JSONResponse({"ok": False, "error": f"Bloc '{block_id}' inconnu"}, status_code=404)

        cache[block_id] = data
        return JSONResponse({"ok": True, "data": data})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.get("/api/status")
async def status():
    return {"status": "ok", "cached_blocks": list(cache.keys())}


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    print(f"[WS] Client connecté — {len(clients)} total")

    # Envoie le cache actuel au nouveau client
    for block_id, data in cache.items():
        await ws.send_text(json.dumps({"block": block_id, "data": data}))

    try:
        while True:
            await ws.receive_text()  # keep-alive
    except WebSocketDisconnect:
        clients.remove(ws)
        print(f"[WS] Client déconnecté — {len(clients)} restants")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)