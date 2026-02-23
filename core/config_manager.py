"""
Gestionnaire de configuration.
Lit et écrit config.yaml — positions, taille, paramètres de chaque bloc.
"""

import yaml
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

DEFAULT_CONFIG = {
    "window": {
        "x": 50,
        "y": 50,
        "width": 1100,
        "height": 700,
        "opacity": 0.95,
        "always_on_top": True,
    },
    "blocks": [
        {
            "id": "clock",
            "enabled": True,
            "grid_row": 0,
            "grid_col": 0,
            "config": {}
        },
        {
            "id": "weather",
            "enabled": False,
            "grid_row": 0,
            "grid_col": 1,
            "config": {
                "city": "Paris",
                "api_key": "YOUR_OPENWEATHER_KEY"
            }
        },
        {
            "id": "emails",
            "enabled": False,
            "grid_row": 1,
            "grid_col": 0,
            "config": {
                "imap_host": "imap.gmail.com",
                "email": "YOUR_EMAIL",
                "password": "YOUR_APP_PASSWORD",
                "max_display": 5
            }
        },
        {
            "id": "jobs",
            "enabled": False,
            "grid_row": 1,
            "grid_col": 1,
            "config": {
                "keywords": ["python", "developer"],
                "location": "Paris"
            }
        },
        {
            "id": "movies",
            "enabled": False,
            "grid_row": 0,
            "grid_col": 2,
            "config": {
                "tmdb_api_key": "YOUR_TMDB_KEY",
                "language": "fr-FR"
            }
        }
    ]
}


def load() -> dict:
    """Charge la config depuis config.yaml. Crée le fichier si inexistant."""
    if not CONFIG_PATH.exists():
        save(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data or DEFAULT_CONFIG


def save(config: dict):
    """Persiste la config dans config.yaml."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def update_block_position(config: dict, block_id: str, row: int, col: int):
    """Met à jour la position d'un bloc dans la config et sauvegarde."""
    for block in config.get("blocks", []):
        if block["id"] == block_id:
            block["grid_row"] = row
            block["grid_col"] = col
            break
    save(config)


def get_enabled_blocks(config: dict) -> list:
    """Retourne uniquement les blocs activés, triés par position."""
    blocks = [b for b in config.get("blocks", []) if b.get("enabled", False)]
    return sorted(blocks, key=lambda b: (b.get("grid_row", 0), b.get("grid_col", 0)))