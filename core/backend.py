"""
Backend — Orchestre tous les blocs de données.
Gère les fetches sync/async et la config.
"""

import json
import threading
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"

DEFAULT_CONFIG = {
    "window": {"x": 50, "y": 50, "width": 1200, "height": 750},
    "blocks": {
        "clock":   {"enabled": True},
        "emails":  {
            "enabled": True,
            "imap_host": "imap.gmail.com",
            "email": "",
            "password": "",
            "max_display": 5
        },
        "jobs": {
            "enabled": True,
            "keywords": "Full Stack",
            "location": "France",
            "max_display": 6
        },
        "movies":  {"enabled": False, "tmdb_api_key": "", "language": "fr-FR"},
        "weather": {"enabled": False, "city": "Paris", "api_key": ""}
    }
}


class Backend:
    def __init__(self):
        self.config = self._load_config()
        self._blocks = {}
        self._register_blocks()

    def _load_config(self) -> dict:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        self.save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    def save_config(self, config=None):
        data = config or self.config
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _register_blocks(self):
        """Importe et instancie tous les blocs disponibles."""
        from blocks.clock import ClockBlock
        from blocks.emails import EmailsBlock
        from blocks.jobs import JobsBlock

        block_cfg = self.config.get("blocks", {})

        self._blocks = {
            "clock":  ClockBlock(block_cfg.get("clock", {})),
            "emails": EmailsBlock(block_cfg.get("emails", {})),
            "jobs":   JobsBlock(block_cfg.get("jobs", {})),
        }

        print(f"[Backend] {len(self._blocks)} bloc(s) enregistré(s) : {list(self._blocks.keys())}")

    def get_sync(self, block_id: str) -> dict:
        """
        Fetch synchrone — pour les blocs rapides (clock).
        Ne pas utiliser pour IMAP ou Selenium.
        """
        block = self._blocks.get(block_id)
        if not block:
            raise ValueError(f"Bloc '{block_id}' introuvable")
        return block.fetch()

    def fetch_async(self, block_id: str, callback):
        """
        Fetch asynchrone dans un thread séparé.
        Appelle callback(block_id, data) quand terminé.
        """
        block = self._blocks.get(block_id)
        if not block:
            print(f"[Backend] Bloc '{block_id}' introuvable pour fetch async")
            return

        def _run():
            try:
                print(f"[Backend] Fetch async '{block_id}'...")
                data = block.fetch()
                callback(block_id, data)
            except Exception as e:
                print(f"[Backend] Erreur fetch '{block_id}': {e}")
                callback(block_id, {"error": str(e)})

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def get_blocks_config(self) -> dict:
        """Retourne la config de tous les blocs pour que JS sache lesquels activer."""
        return self.config.get("blocks", {})
