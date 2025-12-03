"""Componente Sidebar"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class Sidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName('sidebar')
        self.setFixedWidth(220)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Título
        title = QLabel("CML Simulator")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Botón Inicio únicamente
        self.buttons = {}
        btn = QPushButton("Inicio")
        btn.setFixedHeight(36)
        layout.addWidget(btn)
        self.buttons["Inicio"] = btn
        
        layout.addStretch()
