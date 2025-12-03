"""Utilidades para la interfaz gráfica"""
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QLabel
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


def add_shadow(widget, blur_radius=10, offset=2):
    """Agrega sombra a un widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(QColor(0, 0, 0, 80))
    shadow.setOffset(offset, offset)
    widget.setGraphicsEffect(shadow)


def create_card_title(text):
    """Crea un label de título estandarizado"""
    label = QLabel(text)
    label.setStyleSheet("font-weight: normal; font-size: 14px; color: #07210F;")
    label.setAlignment(Qt.AlignCenter)
    return label
