from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QProgressBar, QDialog, QTextEdit, QListWidget, QListWidgetItem, QSpinBox, QDoubleSpinBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

def create_history_card():
    card = QFrame()
    card.setObjectName('card')
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(8, 4, 8, 4)
    title = QLabel("Historial de medicación")
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("font-weight: normal; font-size: 14px; color: #07210F; margin: 0px; padding: 0px;")
    card_layout.addWidget(title)

    # Spinners para mes
    mes_input = QSpinBox()
    mes_input.setMinimum(0)
    mes_input.setMaximum(1000)
    mes_input.setValue(0)
    mes_input.setFixedHeight(28)
    mes_input.setMaximumWidth(100)
    mes_input.setButtonSymbols(QSpinBox.UpDownArrows)
    mes_input.setStyleSheet("""
        QSpinBox {
            background-color: white;
            color: #333;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 2px 2px 2px 4px;
        }
        QSpinBox::up-button {
            background-color: #A5D6A7;
            border: none;
            border-radius: 2px;
            width: 16px;
            margin: 0px;
        }
        QSpinBox::down-button {
            background-color: #A5D6A7;
            border: none;
            border-radius: 2px;
            width: 16px;
            margin: 0px;
        }
        QSpinBox::up-button:hover {
            background-color: #81C784;
        }
        QSpinBox::up-button:pressed {
            background-color: #66BB6A;
        }
        QSpinBox::down-button:hover {
            background-color: #81C784;
        }
        QSpinBox::down-button:pressed {
            background-color: #66BB6A;
        }
    """)
    
    # DoubleSpinBox para BCR-ABL%
    porc_input = QDoubleSpinBox()
    porc_input.setMinimum(0)
    porc_input.setMaximum(100)
    porc_input.setValue(0)
    porc_input.setSingleStep(0.1)
    porc_input.setDecimals(2)
    porc_input.setFixedHeight(28)
    porc_input.setMaximumWidth(100)
    porc_input.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
    porc_input.setStyleSheet("""
        QDoubleSpinBox {
            background-color: white;
            color: #333;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 2px 2px 2px 4px;
        }
        QDoubleSpinBox::up-button {
            background-color: #A5D6A7;
            border: none;
            border-radius: 2px;
            width: 16px;
            margin: 0px;
        }
        QDoubleSpinBox::down-button {
            background-color: #A5D6A7;
            border: none;
            border-radius: 2px;
            width: 16px;
            margin: 0px;
        }
        QDoubleSpinBox::up-button:hover {
            background-color: #81C784;
        }
        QDoubleSpinBox::up-button:pressed {
            background-color: #66BB6A;
        }
        QDoubleSpinBox::down-button:hover {
            background-color: #81C784;
        }
        QDoubleSpinBox::down-button:pressed {
            background-color: #66BB6A;
        }
    """)
    
    # DoubleSpinBox para Dosis
    dosis_input = QDoubleSpinBox()
    dosis_input.setMinimum(0)
    dosis_input.setMaximum(1000)
    dosis_input.setValue(0)
    dosis_input.setSingleStep(0.1)
    dosis_input.setDecimals(2)
    dosis_input.setFixedHeight(28)
    dosis_input.setMaximumWidth(100)
    dosis_input.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
    dosis_input.setStyleSheet("""
        QDoubleSpinBox {
            background-color: white;
            color: #333;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 2px 2px 2px 4px;
        }
        QDoubleSpinBox::up-button {
            background-color: #A5D6A7;
            border: none;
            border-radius: 2px;
            width: 16px;
            margin: 0px;
        }
        QDoubleSpinBox::down-button {
            background-color: #A5D6A7;
            border: none;
            border-radius: 2px;
            width: 16px;
            margin: 0px;
        }
        QDoubleSpinBox::up-button:hover {
            background-color: #81C784;
        }
        QDoubleSpinBox::up-button:pressed {
            background-color: #66BB6A;
        }
        QDoubleSpinBox::down-button:hover {
            background-color: #81C784;
        }
        QDoubleSpinBox::down-button:pressed {
            background-color: #66BB6A;
        }
    """)

    # Botones para agregar/editar/borrar
    add_btn = QPushButton("Agregar")
    edit_btn = QPushButton("Actualizar")
    del_btn = QPushButton("Borrar")
    
    # Establecer colores pastel
    add_btn.setStyleSheet("""
        QPushButton {
            background-color: #C8E6C9;
            color: #2E7D32;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #A5D6A7;
        }
        QPushButton:pressed {
            background-color: #81C784;
        }
    """)
    
    edit_btn.setStyleSheet("""
        QPushButton {
            background-color: #BBDEFB;
            color: #1565C0;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #90CAF9;
        }
        QPushButton:pressed {
            background-color: #64B5F6;
        }
    """)
    
    del_btn.setStyleSheet("""
        QPushButton {
            background-color: #FFCCCC;
            color: #C62828;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #EF9A9A;
        }
        QPushButton:pressed {
            background-color: #E57373;
        }
    """)
    
    add_btn.setFixedHeight(32)
    edit_btn.setFixedHeight(32)
    del_btn.setFixedHeight(32)
    add_btn.setMaximumWidth(120)
    edit_btn.setMaximumWidth(120)
    del_btn.setMaximumWidth(120)
    
    # Tabla del historial (3 columnas) - izquierda
    tabla = QTableWidget(0, 3)
    tabla.setHorizontalHeaderLabels(["Mes", "BCR-ABL%", "Dosis"])
    tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    tabla.setObjectName("history_table")
    tabla.verticalHeader().setVisible(False)
    tabla.verticalHeader().setDefaultSectionSize(28)
    tabla.setStyleSheet("""
        QTableWidget {
            border: none;
        }
        QTableWidget::item {
            border-right: none;
        }
        QHeaderView::section {
            background-color: #C8E6C9;
            color: #2E7D32;
            padding: 6px;
            border: none;
            font-weight: bold;
        }
    """)
    tabla.setMinimumHeight(300)
    tabla.setMaximumHeight(400)

    # Panel derecho con inputs y botones
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(8, 0, 0, 0)
    right_layout.setSpacing(8)
    
    # Fila 1: Mes
    row1 = QVBoxLayout()
    row1.setContentsMargins(0, 0, 0, 0)
    row1.setSpacing(2)
    lbl1 = QLabel("Mes:")
    lbl1.setStyleSheet("font-size: 12px;")
    row1.addWidget(lbl1, 0)
    row1.addWidget(mes_input, 0)
    
    # Fila 2: BCR-ABL%
    row2 = QVBoxLayout()
    row2.setContentsMargins(0, 0, 0, 0)
    row2.setSpacing(2)
    lbl2 = QLabel("BCR-ABL%:")
    lbl2.setStyleSheet("font-size: 12px;")
    row2.addWidget(lbl2, 0)
    row2.addWidget(porc_input, 0)
    
    # Fila 3: Dosis
    row3 = QVBoxLayout()
    row3.setContentsMargins(0, 0, 0, 0)
    row3.setSpacing(2)
    lbl3 = QLabel("Dosis:")
    lbl3.setStyleSheet("font-size: 12px;")
    row3.addWidget(lbl3, 0)
    row3.addWidget(dosis_input, 0)
    
    # Fila 4: Botones
    buttons_layout = QVBoxLayout()
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    buttons_layout.setSpacing(6)
    buttons_layout.addWidget(add_btn)
    buttons_layout.addWidget(edit_btn)
    buttons_layout.addWidget(del_btn)
    
    right_layout.addLayout(row1)
    right_layout.addLayout(row2)
    right_layout.addLayout(row3)
    right_layout.addSpacing(8)
    right_layout.addLayout(buttons_layout)
    right_layout.addStretch()

    # Layout horizontal: tabla (izquierda) + panel derecho
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(12)
    content_layout.addWidget(tabla, 1)
    content_layout.addWidget(right_panel, 0)
    
    content_widget = QWidget()
    content_widget.setLayout(content_layout)
    card_layout.addWidget(content_widget, 1)

    widgets = {
        'tabla': tabla,
        'fecha_input': mes_input,
        'mes_input': mes_input,
        'porc_input': porc_input,
        'dosis_input': dosis_input,
        'add_btn': add_btn,
        'update_btn': edit_btn,
        'del_btn': del_btn,
    }
    return card, widgets
