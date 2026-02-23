"""
DraggableContainer — DragBar style Bubble dashboard.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QFont
from core.theme import THEME


# Identifiants courts pour la dragbar (style HTML : CLK-01, EML-02...)
BLOCK_CODES = {
    "clock":   "CLK-01",
    "emails":  "EML-02",
    "jobs":    "JOB-03",
    "movies":  "MOV-04",
    "weather": "WTH-05",
}


class DragBar(QWidget):
    drag_started = pyqtSignal(str)

    def __init__(self, block_id, parent=None):
        super().__init__(parent)
        self.block_id = block_id
        self._drag_start_pos = None
        self.setFixedHeight(32)
        self.setCursor(Qt.OpenHandCursor)
        self.setStyleSheet(f"""
            DragBar {{
                background-color: {THEME['card_header']};
                border-bottom: 1px solid {THEME['border']};
            }}
            DragBar:hover {{
                background-color: #111111;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # Icône grip (⠿ remplacé par ··· plus lisible)
        grip_icon = QLabel("· · ·")
        grip_icon.setFont(QFont(THEME['font_mono'], 10))
        grip_icon.setStyleSheet(f"color: {THEME['text_ghost']}; background: transparent; letter-spacing: 2px;")

        # Label DRAG · CODE
        code = BLOCK_CODES.get(block_id, block_id.upper()[:6])
        drag_label = QLabel(f"DRAG · {code}")
        drag_label.setFont(QFont(THEME['font_mono'], 9))
        drag_label.setStyleSheet(f"color: {THEME['text_ghost']}; background: transparent; letter-spacing: 2px;")

        layout.addWidget(grip_icon)
        layout.addWidget(drag_label)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            print(f"[DragBar] press '{self.block_id}'")

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton) or self._drag_start_pos is None:
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < 6:
            return
        self._drag_start_pos = None
        print(f"[DragBar] drag_started '{self.block_id}'")
        self.drag_started.emit(self.block_id)

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        self.setCursor(Qt.OpenHandCursor)


class DraggableContainer(QWidget):

    block_drag_started = pyqtSignal(str)
    block_drag_ended = pyqtSignal(str, bool)

    def __init__(self, block_widget, block_id, parent=None):
        super().__init__(parent)
        self.block_widget = block_widget
        self.block_id = block_id
        self.setAcceptDrops(True)
        self.setObjectName(block_id)
        self._setup_ui()

    def _setup_ui(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Style carte — border-radius 4px, bordure subtile
        self.setStyleSheet(f"""
            DraggableContainer {{
                background: {THEME['card_bg']};
                border: 1px solid {THEME['border']};
                border-radius: 4px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._drag_bar = DragBar(self.block_id)
        self._drag_bar.drag_started.connect(self._start_drag)
        layout.addWidget(self._drag_bar)
        layout.addWidget(self.block_widget)

    def _start_drag(self, block_id):
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(block_id)
        drag.setMimeData(mime)

        pixmap = self.grab()
        ghost = QPixmap(pixmap.size())
        ghost.fill(Qt.transparent)
        p = QPainter(ghost)
        p.setOpacity(0.45)
        p.drawPixmap(0, 0, pixmap)
        p.end()
        drag.setPixmap(ghost)
        drag.setHotSpot(pixmap.rect().center())

        self.block_drag_started.emit(block_id)
        result = drag.exec_(Qt.MoveAction)
        self.block_drag_ended.emit(block_id, result == Qt.MoveAction)
        print(f"[DraggableContainer] drag ended '{block_id}' result={result}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() != self.block_id:
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                DraggableContainer {{
                    background: {THEME['card_bg']};
                    border: 1px solid {THEME['accent']};
                    border-radius: 4px;
                }}
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"""
            DraggableContainer {{
                background: {THEME['card_bg']};
                border: 1px solid {THEME['border']};
                border-radius: 4px;
            }}
        """)

    def dropEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() != self.block_id:
            event.acceptProposedAction()
            self.dragLeaveEvent(event)
        else:
            event.ignore()