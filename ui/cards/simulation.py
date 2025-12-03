from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget, QHBoxLayout, QComboBox, QTableWidget, QHeaderView, QLabel
from PySide6.QtCore import Qt

def create_simulation_card():
    card2 = QFrame()
    card2.setObjectName("card")
    card2_layout = QVBoxLayout(card2)
    card2_layout.setContentsMargins(8, 8, 8, 8)
    card2_layout.setSpacing(12)

    # Combo box para seleccionar escenario
    controls = QWidget()
    controls_layout = QHBoxLayout(controls)
    controls_layout.setContentsMargins(0, 0, 0, 0)
    controls_layout.setSpacing(8)
    
    combo_sim = QComboBox()
    combo_sim.addItem("Simulación")
    combo_sim.setFixedHeight(24)
    combo_sim.setStyleSheet("""
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
            border-radius: 4px;
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
            border-radius: 6px;
        }
    """)
    
    controls_layout.addWidget(QLabel("Escenario:"))
    controls_layout.addWidget(combo_sim, 1)
    controls_layout.addStretch()
    card2_layout.addWidget(controls)

    # Tabla para mostrar datos del escenario
    scenarios_table = QTableWidget(0, 2)
    scenarios_table.setHorizontalHeaderLabels(["Parámetro", "Valor"])
    scenarios_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    scenarios_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    scenarios_table.setObjectName("scenarios_table")
    scenarios_table.verticalHeader().setVisible(False)
    scenarios_table.verticalHeader().setDefaultSectionSize(28)
    card2_layout.addWidget(scenarios_table, 1)

    # return card and widget refs
    widgets = {
        'combo_sim': combo_sim,
        'scenarios_table': scenarios_table,
    }
    return card2, widgets
