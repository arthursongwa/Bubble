"""
Thème Bubble — Traduction fidèle du design HTML vers PyQt5.
Palette : noir profond, neutres, accent indigo.
Polices : Inter (principal) + JetBrains Mono (monospace/labels).
"""

THEME = {
    # Fonds
    "bg":           "#0A0A0A",   # Fond fenêtre principal
    "card_bg":      "#121212",   # Fond des blocs
    "card_header":  "#0D0D0D",   # DragBar + sous-header blocs
    "card_sub":     "#101010",   # Header secondaire dans les blocs

    # Bordures
    "border":       "#262626",   # Bordure standard (neutral-800)
    "border_dim":   "#1A1A1A",   # Bordure très subtile

    # Accents
    "accent":       "#6366F1",   # Indigo-500 (notifications, badges actifs)
    "accent_bg":    "#6366F110", # Indigo fond badge
    "accent_border":"#6366F133", # Indigo bordure badge
    "accent2":      "#10B981",   # Emerald — status actif

    # Textes
    "text":         "#E5E5E5",   # neutral-200 — texte principal
    "text_sub":     "#A3A3A3",   # neutral-400 — texte secondaire
    "text_dim":     "#737373",   # neutral-500 — texte tertiaire
    "text_ghost":   "#404040",   # neutral-700 — très discret

    # États
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "error":        "#EF4444",

    # Hover
    "hover_bg":     "#1C1C1C",   # neutral-900/50 hover

    # Polices
    "font_main":    "Inter",
    "font_mono":    "JetBrains Mono",
}

GLOBAL_STYLESHEET = f"""
    QWidget {{
        background-color: {THEME['bg']};
        color: {THEME['text']};
        font-family: '{THEME['font_main']}';
        font-size: 13px;
    }}

    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        border-radius: 3px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {THEME['border']};
        border-radius: 3px;
        min-height: 24px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: #404040;
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
        background: none;
    }}

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QToolTip {{
        background: {THEME['card_bg']};
        color: {THEME['text_sub']};
        border: 1px solid {THEME['border']};
        padding: 4px 8px;
        font-size: 11px;
        border-radius: 4px;
    }}
"""