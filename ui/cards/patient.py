from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt

def create_patient_card():
    card3 = QFrame()
    card3.setObjectName("card")
    card3_layout = QVBoxLayout(card3)

    # Area de foto y etiquetas con datos del paciente
    photo_and_info = QWidget()
    photo_info_layout = QHBoxLayout(photo_and_info)
    photo_info_layout.setContentsMargins(0, 0, 0, 0)
    photo_info_layout.setSpacing(8)

    photo_label = QLabel("Foto")
    photo_label.setFixedSize(120, 120)
    photo_label.setAlignment(Qt.AlignCenter)
    photo_label.setStyleSheet("background-color: #EDF9EE; border: 1px solid #CDE7D2; border-radius:8px; color:#07210F;")

    info_column = QWidget()
    info_col_layout = QVBoxLayout(info_column)
    info_col_layout.setContentsMargins(0, 0, 0, 0)
    info_col_layout.setSpacing(6)

    patient_nombre = QLabel("Nombre: —")
    patient_edad = QLabel("Edad: —")
    patient_sexo = QLabel("Sexo: —")
    patient_clave = QLabel("Clave: —")
    patient_style = "background-color: #F2FAF2; color: #07210F; padding:6px; border-radius:6px;"
    patient_nombre.setStyleSheet(patient_style)
    patient_edad.setStyleSheet(patient_style)
    patient_sexo.setStyleSheet(patient_style)
    patient_clave.setStyleSheet(patient_style)

    info_col_layout.addWidget(patient_nombre)
    info_col_layout.addWidget(patient_edad)
    info_col_layout.addWidget(patient_sexo)
    info_col_layout.addWidget(patient_clave)

    photo_info_layout.addWidget(photo_label)
    photo_info_layout.addWidget(info_column)

    title_card3 = QLabel("Datos del paciente")
    title_card3.setAlignment(Qt.AlignCenter)
    title_card3.setStyleSheet("font-weight: normal; font-size: 14px; color: #07210F;")
    card3_layout.addWidget(title_card3)

    select_row = QWidget()
    select_row_layout = QHBoxLayout(select_row)
    select_row_layout.setContentsMargins(0, 0, 0, 0)
    select_row_layout.setSpacing(8)
    select_label = QLabel("Seleccionar paciente:")
    patient_combo = QComboBox()
    patient_combo.setFixedHeight(24)
    patient_combo.setStyleSheet("""
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
    # Agregar pacientes (sin pre-seleccionar)
    patient_combo.addItem("")  # Item vacío por defecto
    patient_combo.addItem("Christopher Martin Jimenez Osorio")
    patient_combo.addItem("Paciente Clase B (TFR Exitosa)")
    patient_combo.addItem("Paciente Clase A (Recurrencia)")
    patient_combo.addItem("Paciente Clase C (Recurrencia Tardía)")
    select_row_layout.addWidget(select_label)
    select_row_layout.addStretch()
    select_row_layout.addWidget(patient_combo, 1)

    card3_layout.addWidget(photo_and_info)
    card3_layout.addWidget(select_row)

    widgets = {
        'photo_label': photo_label,
        'patient_nombre': patient_nombre,
        'patient_edad': patient_edad,
        'patient_clave': patient_clave,
        'patient_sexo': patient_sexo,
        'patient_combo': patient_combo,
    }
    return card3, widgets
