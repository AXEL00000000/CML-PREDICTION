# Extracted stylesheet for the application
STYLES = """
/* Fondo principal */
QMainWindow {
    background-color: #E6FCF8;
}

/* Sidebar y cards */
QFrame#sidebar {
    background-color: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E0E0E0;
}
QFrame#card {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #D0D0D0;
}

/* Tabla dentro de la card: fondo blanco para legibilidad */
QFrame#card QTableWidget, QTableWidget#tabla {
    background-color: #FFFFFF;
    color: #0B2E13; /* texto oscuro para contraste */
    border-radius: 8px;
}
/* Encabezados de la tabla: pistacho claro */
QHeaderView::section {
    background-color: #CFEAD2; /* pistacho muy claro */
    color: #07210F; /* texto oscuro */
    padding: 6px;
    border: none;
}
/* Fila seleccionada en la tabla */
QTableWidget::item:selected {
    background-color: #76C893; /* pistacho medio */
    color: #FFFFFF;
}

/* Botón de esquina (corner button) de la tabla */
QTableCornerButton::section {
    background-color: #78C08F; /* pistacho */
    color: #ffffff;
    border: none;
}
QTableCornerButton::section:hover {
    background-color: #5FB57A;
}
QTableCornerButton::section:pressed {
    background-color: #4A9B64;
}

/* Scrollbars para la tabla (vertical y horizontal) */
QTableWidget QScrollBar:vertical, QTableWidget#tabla QScrollBar:vertical {
    background: #EAF6EC; /* fondo suave */
    width: 12px;
    margin: 0px 0px 0px 0px;
    border-radius: 6px;
}
QTableWidget QScrollBar::handle:vertical, QTableWidget#tabla QScrollBar::handle:vertical {
    background: #78C08F; /* pistacho */
    min-height: 20px;
    border-radius: 6px;
}
QTableWidget QScrollBar::handle:vertical:hover, QTableWidget#tabla QScrollBar::handle:vertical:hover {
    background: #5FB57A;
}
QTableWidget QScrollBar::add-line:vertical, QTableWidget QScrollBar::sub-line:vertical,
QTableWidget#tabla QScrollBar::add-line:vertical, QTableWidget#tabla QScrollBar::sub-line:vertical {
    background: none;
    height: 0px;
}

QTableWidget QScrollBar:horizontal, QTableWidget#tabla QScrollBar:horizontal {
    background: #EAF6EC;
    height: 12px;
    border-radius: 6px;
}
QTableWidget QScrollBar::handle:horizontal, QTableWidget#tabla QScrollBar::handle:horizontal {
    background: #78C08F;
    min-width: 20px;
    border-radius: 6px;
}
QTableWidget QScrollBar::handle:horizontal:hover, QTableWidget#tabla QScrollBar::handle:horizontal:hover {
    background: #5FB57A;
}

/* Campos del formulario dentro de la card */
QFrame#card QLineEdit, QFrame#card QWidget QLineEdit {
    background-color: #F4F9F4; /* gris verdoso muy claro */
    border: 1px solid #CDE7D2;
    border-radius: 6px;
    padding: 6px;
    color: #0B2E13;
}

/* SpinBoxes dentro de la card - sin estilos automáticos */
QFrame#card QSpinBox, QFrame#card QDoubleSpinBox {
    /* Los estilos se aplicarán individualmente en cada card */
}

/* Combo dentro de la card: pistacho con texto blanco (como botones) */
QFrame#card QComboBox {
    background-color: #78C08F;
    color: #ffffff;
    border: none;
    padding: 6px 10px;
    border-radius: 8px;
    min-height: 28px;
}
QFrame#card QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: none;
}
QFrame#card QComboBox::down-arrow {
    image: none;
    border: none;
    width: 0;
    height: 0;
}
/* El popup (lista) de opciones: fondo blanco y texto oscuro */
QFrame#card QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #07210F;
    selection-background-color: #76C893;
    selection-color: #FFFFFF;
}

/* Botones dentro de la card: pistacho con texto blanco */
QFrame#card QPushButton {
    background-color: #78C08F; /* pistacho */
    color: #ffffff;
    border: none;
    padding: 8px 10px;
    border-radius: 8px;
    font-weight: 600;
}
QFrame#card QPushButton:hover {
    background-color: #5FB57A;
}
QFrame#card QPushButton:pressed {
    background-color: #4A9B64;
}

/* Botones del sidebar: mismo estilo que los botones dentro de las cards */
QFrame#sidebar QPushButton {
    background-color: #78C08F; /* pistacho */
    color: #ffffff;
    border: none;
    padding: 8px 10px;
    border-radius: 8px;
    font-weight: 700; /* texto en negrita */
    min-height: 36px;
}
QFrame#sidebar QPushButton:hover {
    background-color: #5FB57A;
}
QFrame#sidebar QPushButton:pressed {
    background-color: #4A9B64;
}

/* Etiquetas (labels) */
QLabel {
    font-size: 16px;
    color: #1A2C42;
}
"""
