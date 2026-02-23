"""
Bridge — Objet Python exposé à JavaScript via QWebChannel.

Côté JS, on appelle :
    window.bridge.getData("emails", function(result) {
        const data = JSON.parse(result);
        // màj le DOM
    });

Côté Python, on reçoit l'appel, on fetch les données, on répond via callback JS.
"""

import json
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWebChannel import QWebChannel


class Bridge(QObject):
    """
    Cet objet est directement accessible depuis JavaScript sous window.bridge.
    Chaque méthode décorée @pyqtSlot peut être appelée depuis JS.
    """

    # Signal émis vers JS pour pousser une mise à jour en temps réel
    dataReady = pyqtSignal(str, str)  # (block_id, json_data)

    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend

        # Canal WebChannel — relie Python et JS
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self)

    # ── API appelée depuis JavaScript ─────────────────────────────────────────

    @pyqtSlot(str, result=str)
    def getData(self, block_id: str) -> str:
        """
        Appelé depuis JS : window.bridge.getData("clock")
        Retourne un JSON string avec les données du bloc.
        Synchrone pour les blocs rapides (clock, config).
        """
        print(f"[Bridge] getData('{block_id}')")
        try:
            data = self.backend.get_sync(block_id)
            return json.dumps({"ok": True, "data": data})
        except Exception as e:
            print(f"[Bridge] Erreur getData('{block_id}'): {e}")
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(str)
    def requestData(self, block_id: str):
        """
        Appelé depuis JS pour déclencher un fetch asynchrone.
        Le résultat est poussé via le signal dataReady → JS reçoit via bridge.dataReady.connect()
        """
        print(f"[Bridge] requestData('{block_id}')")
        self.backend.fetch_async(block_id, self._on_data_ready)

    def _on_data_ready(self, block_id: str, data: dict):
        """Callback Python → pousse les données vers JS via signal."""
        payload = json.dumps({"ok": True, "data": data})
        print(f"[Bridge] dataReady emit '{block_id}'")
        self.dataReady.emit(block_id, payload)

    @pyqtSlot(str, result=str)
    def getConfig(self, key: str) -> str:
        """Retourne un paramètre de config (pour que JS connaisse les blocs actifs)."""
        try:
            val = self.backend.config.get(key)
            return json.dumps(val)
        except Exception as e:
            return json.dumps(None)

    @pyqtSlot(str, str)
    def saveConfig(self, key: str, value: str):
        """Sauvegarde un paramètre depuis JS (ex: position d'un bloc)."""
        try:
            self.backend.config[key] = json.loads(value)
            self.backend.save_config()
            print(f"[Bridge] saveConfig '{key}' = {value[:60]}")
        except Exception as e:
            print(f"[Bridge] Erreur saveConfig: {e}")

    @pyqtSlot(str)
    def minimize(self, _=""):
        """Minimise la fenêtre depuis JS."""
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            w.showMinimized()

    @pyqtSlot(str)
    def close(self, _=""):
        """Ferme l'app depuis JS."""
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()

    @pyqtSlot(str)
    def maximize(self, _=""):
        """Maximise/restaure depuis JS."""
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            if w.isMaximized():
                w.showNormal()
            else:
                w.showMaximized()

    @pyqtSlot(int, int)
    def moveWindow(self, dx: int, dy: int):
        """Déplace la fenêtre (appelé pendant le drag de la titlebar)."""
        from PyQt5.QtWidgets import QApplication
        for w in QApplication.topLevelWidgets():
            pos = w.pos()
            w.move(pos.x() + dx, pos.y() + dy)
