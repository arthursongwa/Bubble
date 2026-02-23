"""
BaseBlock — Classe de base pour tous les blocs du dashboard.
Style : design Bubble — header mono uppercase, contenu épuré.
"""

from abc import abstractmethod
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QFrame
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from core.theme import THEME


class BaseBlock(QWidget):

    BLOCK_ID = "base"
    BLOCK_TITLE = "Bloc"
    REFRESH_MS = 60_000
    MIN_WIDTH = 280
    MIN_HEIGHT = 200

    data_updated = pyqtSignal(str, object)

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self._setup_base_ui()
        self._setup_timer()
        self._do_fetch()

    def _setup_base_ui(self):
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {THEME['card_bg']}; border: none;")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Header bloc : titre monospace uppercase
        self._header = self._build_header()
        self._main_layout.addWidget(self._header)

        # Zone contenu
        self._content_widget = QWidget()
        self._content_widget.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._main_layout.addWidget(self._content_widget)

        # Label erreur
        self._error_label = QLabel()
        self._error_label.setStyleSheet(f"color: {THEME['error']}; font-size: 11px; background: transparent; padding: 8px 16px;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        self._main_layout.addWidget(self._error_label)

    def _build_header(self):
        """Header avec titre + badge (optionnel) — style HTML."""
        header = QWidget()
        header.setFixedHeight(36)
        header.setStyleSheet(f"""
            background: {THEME['card_sub']};
            border-bottom: 1px solid {THEME['border_dim']};
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        title = QLabel(self.BLOCK_TITLE.upper())
        title.setFont(QFont(THEME['font_mono'], 9))
        title.setStyleSheet(f"color: {THEME['text_sub']}; letter-spacing: 3px; background: transparent;")

        layout.addWidget(title)
        layout.addStretch()

        # Badge (peut être mis à jour par les sous-classes via self._badge_label)
        self._badge_label = QLabel()
        self._badge_label.setFont(QFont(THEME['font_mono'], 8))
        self._badge_label.setStyleSheet(f"""
            color: {THEME['text_dim']};
            background: {THEME['card_bg']};
            border: 1px solid {THEME['border']};
            border-radius: 3px;
            padding: 1px 6px;
        """)
        self._badge_label.hide()
        layout.addWidget(self._badge_label)

        return header

    def set_badge(self, text, accent=False):
        """Affiche un badge dans le header (ex: '3 UNREAD')."""
        if text:
            self._badge_label.setText(text.upper())
            if accent:
                self._badge_label.setStyleSheet(f"""
                    color: {THEME['accent']};
                    background: {THEME['accent_bg']};
                    border: 1px solid {THEME['accent_border']};
                    border-radius: 3px;
                    padding: 1px 6px;
                    font-family: '{THEME['font_mono']}';
                    font-size: 8pt;
                """)
            else:
                self._badge_label.setStyleSheet(f"""
                    color: {THEME['text_sub']};
                    background: #1C1C1C;
                    border: 1px solid {THEME['border']};
                    border-radius: 3px;
                    padding: 1px 6px;
                    font-family: '{THEME['font_mono']}';
                    font-size: 8pt;
                """)
            self._badge_label.show()
        else:
            self._badge_label.hide()

    def _setup_timer(self):
        self._timer = QTimer(self)
        self._timer.setInterval(self.REFRESH_MS)
        self._timer.timeout.connect(self._do_fetch)
        self._timer.start()

    def _do_fetch(self):
        try:
            data = self.fetch()
            self._error_label.hide()
            self._clear_content()
            self.render(data)
            self.data_updated.emit(self.BLOCK_ID, data)
        except Exception as e:
            self._error_label.setText(f"⚠  {e}")
            self._error_label.show()

    def _clear_content(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def add_row(self, label, value, value_color=None):
        """Ligne label + valeur avec séparateur."""
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        rl = QVBoxLayout(row)
        rl.setContentsMargins(16, 10, 16, 10)
        rl.setSpacing(2)

        lbl = QLabel(label)
        lbl.setFont(QFont(THEME['font_mono'], 8))
        lbl.setStyleSheet(f"color: {THEME['text_ghost']}; background: transparent; letter-spacing: 1px;")

        val = QLabel(value)
        val.setFont(QFont(THEME['font_main'], 13, QFont.DemiBold))
        val.setStyleSheet(f"color: {value_color or THEME['text']}; background: transparent;")
        val.setWordWrap(True)

        rl.addWidget(lbl)
        rl.addWidget(val)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {THEME['border_dim']};")

        self._content_layout.addWidget(row)
        self._content_layout.addWidget(sep)

    def add_label(self, text, size=11, color=None, bold=False):
        lbl = QLabel(text)
        lbl.setFont(QFont(THEME['font_main'], size, QFont.Bold if bold else QFont.Normal))
        lbl.setStyleSheet(f"color: {color or THEME['text_sub']}; background: transparent; padding: 8px 16px;")
        lbl.setWordWrap(True)
        self._content_layout.addWidget(lbl)

    @abstractmethod
    def fetch(self):
        ...

    @abstractmethod
    def render(self, data):
        ...