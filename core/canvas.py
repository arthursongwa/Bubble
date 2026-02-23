"""
DashboardCanvas — Grille drag & drop, style Bubble.
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QScrollArea, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.theme import THEME
from core.draggable_container import DraggableContainer


class DropZone(QWidget):
    def __init__(self, row, col, on_drop_callback, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self._on_drop = on_drop_callback
        self.setAcceptDrops(True)
        self.setMinimumSize(200, 256)  # min-h-[16rem] comme dans le HTML
        self._set_idle()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self._icon = QLabel("+")
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setFont(QFont(THEME['font_main'], 28))
        self._icon.setStyleSheet(f"color: {THEME['text_ghost']}; background: transparent;")
        layout.addWidget(self._icon)

    def _set_idle(self):
        self.setStyleSheet(f"""
            DropZone {{
                background: transparent;
                border: 2px dashed #262626;
                border-radius: 4px;
            }}
            DropZone:hover {{
                border-color: #404040;
            }}
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            print(f"[DropZone ({self.row},{self.col})] dragEnter '{event.mimeData().text()}'")
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                DropZone {{
                    background: #111111;
                    border: 2px dashed {THEME['accent']};
                    border-radius: 4px;
                }}
            """)
            self._icon.setStyleSheet(f"color: {THEME['accent']}; background: transparent;")

    def dragLeaveEvent(self, event):
        self._set_idle()
        self._icon.setStyleSheet(f"color: {THEME['text_ghost']}; background: transparent;")

    def dropEvent(self, event):
        if event.mimeData().hasText():
            block_id = event.mimeData().text()
            print(f"[DropZone ({self.row},{self.col})] DROP '{block_id}'")
            event.acceptProposedAction()
            self._set_idle()
            self._icon.setStyleSheet(f"color: {THEME['text_ghost']}; background: transparent;")
            self._on_drop(block_id, self.row, self.col)


class DashboardCanvas(QScrollArea):

    COLUMNS = 3
    CELL_SPACING = 24   # gap-6 = 24px

    def __init__(self, config, on_position_changed, parent=None):
        super().__init__(parent)
        self._config = config
        self._on_position_changed = on_position_changed
        self._containers = {}
        self._block_positions = {}
        self._drop_succeeded = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._inner = QWidget()
        self._inner.setStyleSheet(f"background: {THEME['bg']};")
        self._grid = QGridLayout(self._inner)
        self._grid.setSpacing(self.CELL_SPACING)
        self._grid.setContentsMargins(24, 24, 24, 24)
        for col in range(self.COLUMNS):
            self._grid.setColumnStretch(col, 1)

        self.setWidget(self._inner)

    def _place_widget(self, widget, row, col):
        existing = self._grid.itemAtPosition(row, col)
        if existing and existing.widget() and existing.widget() is not widget:
            old = existing.widget()
            self._grid.removeWidget(old)
            old.hide()
        self._grid.addWidget(widget, row, col)
        widget.show()

    def add_block(self, block_widget, block_id, row, col):
        print(f"[Canvas] add_block '{block_id}' -> ({row},{col})")
        container = DraggableContainer(block_widget, block_id)
        container.setObjectName(block_id)
        container.block_drag_started.connect(self._on_drag_started)
        container.block_drag_ended.connect(self._on_drag_ended)
        container.dropEvent = lambda e, cid=block_id: self._on_container_drop(e, cid)
        self._containers[block_id] = container
        self._block_positions[block_id] = (row, col)
        self._place_widget(container, row, col)

    def _on_drag_started(self, block_id):
        print(f"[Canvas] drag started '{block_id}'")
        if block_id not in self._block_positions:
            return
        self._drop_succeeded[block_id] = False
        row, col = self._block_positions[block_id]
        container = self._containers.get(block_id)
        if not container:
            return
        container.setVisible(False)
        drop = DropZone(row, col, self._handle_drop)
        drop.setObjectName(f"__temp__{block_id}")
        self._place_widget(drop, row, col)

    def _on_drag_ended(self, block_id, success):
        print(f"[Canvas] drag ended '{block_id}' drop_succeeded={self._drop_succeeded.get(block_id)}")
        if self._drop_succeeded.get(block_id, False):
            self._drop_succeeded.pop(block_id, None)
            return
        print(f"[Canvas] restauration '{block_id}'")
        container = self._containers.get(block_id)
        row, col = self._block_positions.get(block_id, (0, 0))
        self._remove_temp_dropzone(block_id)
        if container:
            self._place_widget(container, row, col)
        self._drop_succeeded.pop(block_id, None)

    def _handle_drop(self, block_id, target_row, target_col):
        print(f"[Canvas] _handle_drop '{block_id}' -> ({target_row},{target_col})")
        container = self._containers.get(block_id)
        if not container:
            return
        old_row, old_col = self._block_positions.get(block_id, (target_row, target_col))
        displaced_id = self._get_block_at(target_row, target_col)
        self._remove_temp_dropzone(block_id)

        if displaced_id and displaced_id != block_id:
            displaced = self._containers[displaced_id]
            self._block_positions[displaced_id] = (old_row, old_col)
            self._place_widget(displaced, old_row, old_col)
            self._on_position_changed(displaced_id, old_row, old_col)
        else:
            drop = DropZone(old_row, old_col, self._handle_drop)
            self._place_widget(drop, old_row, old_col)

        self._block_positions[block_id] = (target_row, target_col)
        self._place_widget(container, target_row, target_col)
        self._on_position_changed(block_id, target_row, target_col)
        self._drop_succeeded[block_id] = True
        print(f"[Canvas] '{block_id}' maintenant en ({target_row},{target_col})")

    def _on_container_drop(self, event, target_id):
        if not event.mimeData().hasText():
            event.ignore()
            return
        src_id = event.mimeData().text()
        if src_id == target_id:
            event.ignore()
            return
        print(f"[Canvas] swap '{src_id}' <-> '{target_id}'")
        event.acceptProposedAction()
        src_c = self._containers.get(src_id)
        tgt_c = self._containers.get(target_id)
        pos_src = self._block_positions.get(src_id)
        pos_tgt = self._block_positions.get(target_id)
        if not all([src_c, tgt_c, pos_src, pos_tgt]):
            return
        self._remove_temp_dropzone(src_id)
        src_c.setVisible(True)
        self._block_positions[src_id] = pos_tgt
        self._block_positions[target_id] = pos_src
        self._place_widget(src_c, pos_tgt[0], pos_tgt[1])
        self._place_widget(tgt_c, pos_src[0], pos_src[1])
        self._on_position_changed(src_id, pos_tgt[0], pos_tgt[1])
        self._on_position_changed(target_id, pos_src[0], pos_src[1])
        self._drop_succeeded[src_id] = True

    def _remove_temp_dropzone(self, block_id):
        name = f"__temp__{block_id}"
        for i in range(self._grid.count()):
            item = self._grid.itemAt(i)
            if item and item.widget() and item.widget().objectName() == name:
                w = item.widget()
                self._grid.removeWidget(w)
                w.deleteLater()
                print(f"[Canvas] DropZone temp '{name}' supprimee")
                return

    def _get_block_at(self, row, col):
        for bid, (r, c) in self._block_positions.items():
            if r == row and c == col:
                return bid
        return None

    def populate_empty_cells(self, max_rows=3):
        occupied = set(self._block_positions.values())
        for r in range(max_rows):
            for c in range(self.COLUMNS):
                if (r, c) not in occupied and not self._grid.itemAtPosition(r, c):
                    drop = DropZone(r, c, self._handle_drop)
                    self._grid.addWidget(drop, r, c)

    def find_free_cell(self, max_rows=5):
        occupied = set(self._block_positions.values())
        for r in range(max_rows):
            for c in range(self.COLUMNS):
                if (r, c) not in occupied:
                    return (r, c)
        return (max_rows, 0)

    def remove_block(self, block_id):
        print(f"[Canvas] remove_block '{block_id}'")
        container = self._containers.pop(block_id, None)
        if not container:
            return
        pos = self._block_positions.pop(block_id, None)
        self._grid.removeWidget(container)
        container.deleteLater()
        if pos:
            drop = DropZone(pos[0], pos[1], self._handle_drop)
            self._place_widget(drop, pos[0], pos[1])