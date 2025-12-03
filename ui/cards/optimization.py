from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, 
    QProgressBar, QLabel, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


def create_optimization_card():
    card = QFrame()
    card.setObjectName('card')
    card_layout = QVBoxLayout(card)
    
    title = QLabel("Optimización")
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("font-weight: normal; font-size: 14px; color: #07210F;")
    card_layout.addWidget(title)
    
    # Layout horizontal: botones a la izquierda, lista de variables a la derecha
    content_layout = QHBoxLayout()
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(12)
    
    # Panel izquierdo: botones y progress bar
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(8)
    
    # Botón Iniciar
    start_btn = QPushButton("Iniciar")
    start_btn.setFixedHeight(36)
    start_btn.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """)
    
    # Botón Detener
    stop_btn = QPushButton("Detener")
    stop_btn.setFixedHeight(36)
    stop_btn.setEnabled(False)
    stop_btn.setStyleSheet("""
        QPushButton {
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover:enabled {
            background-color: #da190b;
        }
        QPushButton:pressed:enabled {
            background-color: #c41c3b;
        }
        QPushButton:disabled {
            background-color: #ccc;
            color: #999;
        }
    """)
    
    # Progress bar
    progress_bar = QProgressBar()
    progress_bar.setFixedHeight(24)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 3px;
            text-align: center;
            background-color: #f0f0f0;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
        }
    """)
    
    # Botón Terminal
    terminal_btn = QPushButton("Terminal")
    terminal_btn.setFixedHeight(36)
    terminal_btn.setStyleSheet("""
        QPushButton {
            background-color: #FF9800;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #F57C00;
        }
        QPushButton:pressed {
            background-color: #E65100;
        }
    """)
    
    left_layout.addWidget(start_btn)
    left_layout.addWidget(stop_btn)
    left_layout.addWidget(progress_bar)
    left_layout.addWidget(terminal_btn)
    left_layout.addStretch()
    
    # Panel derecho: parámetros de medicación
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(12)
    
    medication_label = QLabel("Parámetros de Medicación:")
    medication_label.setStyleSheet("font-weight: bold; font-size: 11px;")
    right_layout.addWidget(medication_label)
    
    # ===== Mes Inicio =====
    row1 = QHBoxLayout()
    row1.setContentsMargins(0, 0, 0, 0)
    row1.setSpacing(6)
    
    lbl_inicio = QLabel("Mes Inicio:")
    lbl_inicio.setStyleSheet("font-size: 12px; min-width: 80px;")
    
    mes_inicio_spin = QSpinBox()
    mes_inicio_spin.setMinimum(0)
    mes_inicio_spin.setMaximum(1000)
    mes_inicio_spin.setValue(0)
    mes_inicio_spin.setFixedHeight(32)
    mes_inicio_spin.setMinimumWidth(150)
    mes_inicio_spin.setStyleSheet("""
        QSpinBox {
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            padding: 4px;
            color: #000000;
        }
    """)
    
    row1.addWidget(lbl_inicio)
    row1.addWidget(mes_inicio_spin, 1)
    right_layout.addLayout(row1)
    
    # ===== Mes Fin =====
    row2 = QHBoxLayout()
    row2.setContentsMargins(0, 0, 0, 0)
    row2.setSpacing(6)
    
    lbl_fin = QLabel("Mes Fin:")
    lbl_fin.setStyleSheet("font-size: 12px; min-width: 80px;")
    
    mes_fin_spin = QSpinBox()
    mes_fin_spin.setMinimum(0)
    mes_fin_spin.setMaximum(1000)
    mes_fin_spin.setValue(24)
    mes_fin_spin.setFixedHeight(32)
    mes_fin_spin.setMinimumWidth(150)
    mes_fin_spin.setStyleSheet("""
        QSpinBox {
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            padding: 4px;
            color: #000000;
        }
    """)
    
    row2.addWidget(lbl_fin)
    row2.addWidget(mes_fin_spin, 1)
    right_layout.addLayout(row2)
    
    # ===== Dosis (%) =====
    row3 = QHBoxLayout()
    row3.setContentsMargins(0, 0, 0, 0)
    row3.setSpacing(6)
    
    lbl_dosis = QLabel("Dosis (%):")
    lbl_dosis.setStyleSheet("font-size: 12px; min-width: 80px;")
    
    dosis_spin = QDoubleSpinBox()
    dosis_spin.setMinimum(0)
    dosis_spin.setMaximum(100)
    dosis_spin.setValue(100)
    dosis_spin.setSingleStep(5)
    dosis_spin.setDecimals(1)
    dosis_spin.setFixedHeight(32)
    dosis_spin.setMinimumWidth(150)
    dosis_spin.setStyleSheet("""
        QDoubleSpinBox {
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            padding: 4px;
            color: #000000;
        }
    """)
    
    row3.addWidget(lbl_dosis)
    row3.addWidget(dosis_spin, 1)
    right_layout.addLayout(row3)
    
    right_layout.addStretch()
    
    # Agregar paneles al layout horizontal
    content_layout.addWidget(left_panel, 0)
    content_layout.addWidget(right_panel, 1)
    
    content_widget = QWidget()
    content_widget.setLayout(content_layout)
    card_layout.addWidget(content_widget, 1)
    
    widgets = {
        'start_btn': start_btn,
        'stop_btn': stop_btn,
        'progress_bar': progress_bar,
        'terminal_btn': terminal_btn,
        'mes_inicio_spin': mes_inicio_spin,
        'mes_fin_spin': mes_fin_spin,
        'dosis_spin': dosis_spin,
    }
    
    return card, widgets
