"""
Card de Escenarios de Tratamiento
Permite definir y gestionar escenarios de dosificación personalizados
Estructura: inputs arriba + tabla abajo
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QSpinBox, QDoubleSpinBox, QLabel, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt


def create_scenarios_card():
    """Crea la card de Escenarios de Tratamiento"""
    card = QFrame()
    card.setObjectName('card')
    main_layout = QVBoxLayout(card)
    main_layout.setContentsMargins(8, 4, 8, 4)
    main_layout.setSpacing(15)
    
    # ========== COMBOBOX DE ESCENARIOS (ARRIBA) ==========
    strategy_row = QHBoxLayout()
    strategy_row.setContentsMargins(0, 0, 0, 0)
    strategy_row.setSpacing(6)
    
    strategy_combo = QComboBox()
    # Estrategias basadas en el paper científico
    strategy_combo.addItem("")  # Opción vacía por defecto
    strategy_combo.addItem("Manual (Tabla personalizada)")
    strategy_combo.addItem("MR4+36M (Control - Dosis completa)")
    strategy_combo.addItem("MR4+24M+12M50% (DESTINY estándar)")
    strategy_combo.addItem("MR4+24M+12M25% (DESTINY 25%)")
    strategy_combo.addItem("MR4+12M+12M50%+12M25% (Escalonada)")
    strategy_combo.addItem("MR4+12M+24M50% (Reducción prolongada)")
    strategy_combo.addItem("MR4+36M50% (Reducción inmediata 50%)")
    strategy_combo.addItem("MR4+36M25% (Reducción inmediata 25%)")
    strategy_combo.setFixedHeight(24)
    strategy_combo.setStyleSheet("""
        QComboBox {
            background-color: #C8E6C9;
            color: #000000;
            border: 1px solid #A5D6A7;
            border-radius: 6px;
            padding: 2px 4px;
            font-size: 12px;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            width: 0px;
        }
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #000000;
            selection-background-color: #78C08F;
            border: 1px solid #A5D6A7;
        }
    """)
    
    strategy_row.addWidget(QLabel("Escenarios:"))
    strategy_row.addWidget(strategy_combo, 1)
    strategy_row.addStretch()
    main_layout.addLayout(strategy_row)
    
    # ========== PANEL SUPERIOR CON INPUTS ==========
    # Fila 1: Mes Inicio
    row1 = QHBoxLayout()
    row1.setContentsMargins(0, 0, 0, 0)
    row1.setSpacing(3)
    lbl1 = QLabel("Mes Inicio:")
    lbl1.setStyleSheet("font-size: 12px; min-width: 60px;")
    mes_inicio_spin = QSpinBox()
    mes_inicio_spin.setMinimum(0)
    mes_inicio_spin.setMaximum(1000)
    mes_inicio_spin.setValue(0)
    mes_inicio_spin.setFixedHeight(28)
    mes_inicio_spin.setMaximumWidth(100)
    mes_inicio_spin.setButtonSymbols(QSpinBox.UpDownArrows)
    mes_inicio_spin.setStyleSheet("""
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
    row1.addWidget(lbl1)
    row1.addWidget(mes_inicio_spin)
    row1.addSpacing(15)
    
    # Fila 1b: Mes Fin
    lbl2 = QLabel("Mes Fin:")
    lbl2.setStyleSheet("font-size: 12px; min-width: 60px;")
    mes_fin_spin = QSpinBox()
    mes_fin_spin.setMinimum(0)
    mes_fin_spin.setMaximum(1000)
    mes_fin_spin.setValue(24)
    mes_fin_spin.setFixedHeight(28)
    mes_fin_spin.setMaximumWidth(100)
    mes_fin_spin.setButtonSymbols(QSpinBox.UpDownArrows)
    mes_fin_spin.setStyleSheet("""
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
    row1.addWidget(lbl2)
    row1.addWidget(mes_fin_spin)
    row1.addSpacing(15)
    
    # Fila 1c: Dosis (%)
    lbl3 = QLabel("Dosis (%):")
    lbl3.setStyleSheet("font-size: 12px; min-width: 60px;")
    dosis_spin = QDoubleSpinBox()
    dosis_spin.setMinimum(0)
    dosis_spin.setMaximum(100)
    dosis_spin.setValue(50)
    dosis_spin.setSingleStep(5)
    dosis_spin.setDecimals(1)
    dosis_spin.setFixedHeight(28)
    dosis_spin.setMaximumWidth(100)
    dosis_spin.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
    dosis_spin.setStyleSheet("""
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
    row1.addWidget(lbl3)
    row1.addWidget(dosis_spin)
    row1.addStretch()
    main_layout.addLayout(row1)
    
    # ========== BOTONES DE ACCIÓN (FILA HORIZONTAL) ==========
    button_layout = QHBoxLayout()
    button_layout.setContentsMargins(0, 0, 0, 0)
    button_layout.setSpacing(8)
    
    # Botón Agregar
    btn_add = QPushButton("Agregar")
    btn_add.setFixedHeight(28)
    btn_add.setMinimumWidth(90)
    btn_add.setStyleSheet("""
        QPushButton {
            background-color: #C8E6C9;
            color: #2E7D32;
            border: none;
            border-radius: 6px;
            padding: 4px 10px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #A5D6A7;
        }
        QPushButton:pressed {
            background-color: #81C784;
        }
    """)
    
    # Botón Actualizar
    btn_update = QPushButton("Actualizar")
    btn_update.setFixedHeight(28)
    btn_update.setMinimumWidth(90)
    btn_update.setStyleSheet("""
        QPushButton {
            background-color: #BBDEFB;
            color: #1565C0;
            border: none;
            border-radius: 6px;
            padding: 4px 10px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #90CAF9;
        }
        QPushButton:pressed {
            background-color: #64B5F6;
        }
    """)
    
    # Botón Eliminar
    btn_delete = QPushButton("Borrar")
    btn_delete.setFixedHeight(28)
    btn_delete.setMinimumWidth(90)
    btn_delete.setStyleSheet("""
        QPushButton {
            background-color: #FFCCCC;
            color: #C62828;
            border: none;
            border-radius: 6px;
            padding: 4px 10px;
            font-weight: bold;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #EF9A9A;
        }
        QPushButton:pressed {
            background-color: #E57373;
        }
    """)
    
    button_layout.addWidget(btn_add)
    button_layout.addWidget(btn_update)
    button_layout.addWidget(btn_delete)
    button_layout.addStretch()
    main_layout.addLayout(button_layout)
    
    # ========== TABLA DE ESCENARIOS (ABAJO) ==========
    table = QTableWidget(0, 3)
    table.setHorizontalHeaderLabels(["Mes Inicio", "Mes Fin", "Dosis (%)"])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setObjectName("scenarios_table")
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(28)
    table.setMinimumHeight(150)
    table.setMaximumHeight(250)
    table.setStyleSheet("""
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
    main_layout.addWidget(table, 1)
    
    # Retornar referencia a la card y widgets importantes
    return card, {
        'table': table,
        'mes_inicio_spin': mes_inicio_spin,
        'mes_fin_spin': mes_fin_spin,
        'dosis_spin': dosis_spin,
        'btn_add': btn_add,
        'btn_update': btn_update,
        'btn_delete': btn_delete,
        'strategy_combo': strategy_combo,
    }

