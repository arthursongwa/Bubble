"""
MainWindow — Fenêtre principale, design Bubble.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase

from core.theme import THEME, GLOBAL_STYLESHEET
from core.canvas import DashboardCanvas
from core import config_manager, registry


def _load_fonts():
    """Charge Inter et JetBrains Mono si disponibles système, sinon fallback."""
    # PyQt5 utilise les polices système directement — pas besoin de les charger
    # si elles sont installées. Sinon on tombe sur Segoe UI / Consolas.
    pass


class TitleBar(QWidget):
    def __init__(self, parent_window, parent=None):
        super().__init__(parent)
        self._parent_window = parent_window
        self._drag_pos = None
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            TitleBar {{
                background-color: {THEME['bg']};
                border-bottom: 1px solid {THEME['border']};
            }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(0)

        # ── Logo + titre ──────────────────────────────────────────────────────
        logo_group = QWidget()
        logo_group.setStyleSheet("background: transparent;")
        logo_layout = QHBoxLayout(logo_group)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(8)

        # Carré "B"
        logo_box = QLabel("B")
        logo_box.setFixedSize(20, 20)
        logo_box.setAlignment(Qt.AlignCenter)
        logo_box.setFont(QFont(THEME['font_main'], 9, QFont.Medium))
        logo_box.setStyleSheet(f"""
            background: {THEME['text']};
            color: {THEME['bg']};
            border-radius: 3px;
        """)

        title_lbl = QLabel("DASHBOARD")
        title_lbl.setFont(QFont(THEME['font_main'], 9, QFont.Medium))
        title_lbl.setStyleSheet(f"color: {THEME['text_dim']}; letter-spacing: 3px; background: transparent;")

        logo_layout.addWidget(logo_box)
        logo_layout.addWidget(title_lbl)

        # ── Séparateur + statut ───────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(16)
        sep.setStyleSheet(f"color: {THEME['border']}; background: {THEME['border']}; border: none;")

        status_group = QWidget()
        status_group.setStyleSheet("background: transparent;")
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(16, 0, 0, 0)
        status_layout.setSpacing(8)

        dot = QLabel("●")
        dot.setFont(QFont(THEME['font_mono'], 7))
        dot.setStyleSheet(f"color: {THEME['accent2']}; background: transparent;")

        status_lbl = QLabel("System Active")
        status_lbl.setFont(QFont(THEME['font_main'], 11))
        status_lbl.setStyleSheet(f"color: {THEME['text_dim']}; background: transparent;")

        status_layout.addWidget(dot)
        status_layout.addWidget(status_lbl)

        layout.addWidget(logo_group)
        layout.addWidget(sep)
        layout.addWidget(status_group)
        layout.addStretch()

        # ── Boutons fenêtre ───────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(16)

        for symbol, action, hover_color in [
            ("─", self._parent_window.showMinimized, THEME['text']),
            ("□", self._toggle_maximize, THEME['text']),
            ("✕", QApplication.quit, THEME['error']),
        ]:
            btn = QPushButton(symbol)
            btn.setFixedSize(20, 20)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {THEME['text_dim']};
                    border: none;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    color: {hover_color};
                }}
            """)
            btn.clicked.connect(action)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

    def _toggle_maximize(self):
        self._parent_window.showNormal() if self._parent_window.isMaximized() else self._parent_window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self._parent_window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self._drag_pos:
            self._parent_window.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class SidebarToggle(QPushButton):
    """Bouton toggle d'un bloc dans la sidebar."""

    ICONS = {
        "clock":   "🕐",
        "emails":  "✉",
        "jobs":    "💼",
        "movies":  "🎬",
        "weather": "☁",
    }

    def __init__(self, block_id, label, enabled, on_toggle, parent=None):
        super().__init__(parent)
        self._block_id = block_id
        self._label = label
        self._on_toggle = on_toggle
        self.setCheckable(True)
        self.setChecked(enabled)
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        icon = self.ICONS.get(block_id, "◈")
        self.setText(f"  {icon}   {label}")
        self.setFont(QFont(THEME['font_main'], 12))
        self._apply_style(enabled)
        self.toggled.connect(self._toggled)

    def _apply_style(self, enabled):
        if enabled:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: #1C1C1C;
                    color: {THEME['text']};
                    border: 1px solid {THEME['border']};
                    border-radius: 4px;
                    text-align: left;
                    padding: 0 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: #222222;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {THEME['text_dim']};
                    border: 1px solid transparent;
                    border-radius: 4px;
                    text-align: left;
                    padding: 0 12px;
                }}
                QPushButton:hover {{
                    color: {THEME['text_sub']};
                    background: #111111;
                }}
            """)

    def _toggled(self, checked):
        self._apply_style(checked)
        self._on_toggle(self._block_id, checked)


class Sidebar(QWidget):
    def __init__(self, config, on_toggle_block, parent=None):
        super().__init__(parent)
        self._config = config
        self._on_toggle = on_toggle_block
        self._buttons = {}
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            Sidebar {{
                background-color: {THEME['bg']};
                border-right: 1px solid {THEME['border']};
            }}
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)

        # Label section
        section = QLabel("BLOCS")
        section.setFont(QFont(THEME['font_mono'], 9))
        section.setStyleSheet(f"color: {THEME['text_ghost']}; letter-spacing: 3px; background: transparent;")
        layout.addWidget(section)
        layout.addSpacing(8)

        all_blocks = registry.all_blocks()
        for block_cfg in self._config.get("blocks", []):
            bid = block_cfg["id"]
            enabled = block_cfg.get("enabled", False)
            label = all_blocks[bid].BLOCK_TITLE if bid in all_blocks else bid.capitalize()
            btn = SidebarToggle(bid, label, enabled, self._on_toggle)
            self._buttons[bid] = btn
            layout.addWidget(btn)

        layout.addStretch()

        hint = QLabel("Cliquez pour activer ou\ndésactiver un module.")
        hint.setFont(QFont(THEME['font_main'], 10))
        hint.setStyleSheet(f"color: {THEME['text_ghost']}; background: transparent; line-height: 1.5;")
        hint.setWordWrap(True)
        layout.addWidget(hint)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._config = config_manager.load()
        self._active_widgets = {}
        self._build_window()
        self._load_blocks()

    def _build_window(self):
        win_cfg = self._config.get("window", {})
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(f"QMainWindow {{ background: {THEME['bg']}; }}")
        self.setGeometry(
            win_cfg.get("x", 50), win_cfg.get("y", 50),
            win_cfg.get("width", 1200), win_cfg.get("height", 750),
        )
        self.setWindowOpacity(win_cfg.get("opacity", 0.98))

        central = QWidget()
        central.setStyleSheet(f"background: {THEME['bg']};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(TitleBar(self))

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self._sidebar = Sidebar(config=self._config, on_toggle_block=self._on_toggle_block)
        body_layout.addWidget(self._sidebar)

        self._canvas = DashboardCanvas(config=self._config, on_position_changed=self._on_block_moved)
        body_layout.addWidget(self._canvas)

        root.addWidget(body)

    def _load_blocks(self):
        all_cls = registry.all_blocks()
        for block_cfg in config_manager.get_enabled_blocks(self._config):
            bid = block_cfg["id"]
            if bid not in all_cls:
                continue
            widget = all_cls[bid](config=block_cfg.get("config", {}))
            self._active_widgets[bid] = widget
            self._canvas.add_block(widget, bid,
                                   row=block_cfg.get("grid_row", 0),
                                   col=block_cfg.get("grid_col", 0))
        self._canvas.populate_empty_cells(max_rows=3)

    def _on_toggle_block(self, block_id, enabled):
        all_cls = registry.all_blocks()
        block_cfg = None
        for b in self._config.get("blocks", []):
            if b["id"] == block_id:
                b["enabled"] = enabled
                block_cfg = b
                break

        if enabled:
            if block_id not in all_cls or block_id in self._active_widgets:
                return
            cfg = block_cfg.get("config", {}) if block_cfg else {}
            widget = all_cls[block_id](config=cfg)
            self._active_widgets[block_id] = widget
            row, col = self._canvas.find_free_cell(max_rows=5)
            if block_cfg:
                block_cfg["grid_row"] = row
                block_cfg["grid_col"] = col
            self._canvas.add_block(widget, block_id, row=row, col=col)
        else:
            self._active_widgets.pop(block_id, None)
            self._canvas.remove_block(block_id)

        config_manager.save(self._config)

    def _on_block_moved(self, block_id, row, col):
        config_manager.update_block_position(self._config, block_id, row, col)

    def closeEvent(self, event):
        geo = self.geometry()
        self._config["window"].update({"x": geo.x(), "y": geo.y(),
                                        "width": geo.width(), "height": geo.height()})
        config_manager.save(self._config)
        event.accept()