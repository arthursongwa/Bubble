"""
TEMPLATE — Copie ce fichier pour créer un nouveau bloc.
Renomme le fichier en snake_case (ex: github_notifs.py)
et place-le dans le dossier blocks/.

Checklist :
  [ ] Renommer la classe
  [ ] Définir BLOCK_ID (snake_case unique)
  [ ] Définir BLOCK_TITLE (affiché dans la sidebar)
  [ ] Définir REFRESH_MS (fréquence de mise à jour)
  [ ] Implémenter fetch() → retourne des données
  [ ] Implémenter render(data) → met à jour l'UI
  [ ] Ajouter le bloc dans config.yaml
"""

from core.base_block import BaseBlock
from core.theme import THEME


class MonNouveauBloc(BaseBlock):

    BLOCK_ID = "mon_bloc"          # ← Changer
    BLOCK_TITLE = "Mon Bloc"       # ← Changer
    REFRESH_MS = 60_000            # ← Intervalle en ms (60s ici)
    MIN_WIDTH = 260
    MIN_HEIGHT = 160

    def fetch(self) -> dict:
        """
        Récupère les données. Peut appeler une API, lire un fichier, scraper...
        En cas d'erreur, lever une exception — elle sera catchée et affichée.

        Exemples :
          import requests; r = requests.get("https://..."); return r.json()
          import subprocess; result = subprocess.check_output(["..."]) ...
        """
        # ─── Ton code ici ────────────────────────────────────────────────────
        return {
            "valeur": "Hello !",
            "detail": "Tout fonctionne",
        }

    def render(self, data: dict):
        """
        Met à jour l'UI avec les données de fetch().
        Utilise self.add_row() et self.add_label() pour les layouts simples,
        ou self._content_layout.addWidget(mon_widget) pour les layouts custom.
        """
        # ─── Ton code ici ────────────────────────────────────────────────────
        self.add_row("Valeur", data["valeur"])
        self.add_label(data["detail"], size=11, color=THEME["text_dim"])
