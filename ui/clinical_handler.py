"""Manejador de datos clínicos y pacientes"""
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush


class ClinicalDataHandler:
    """Maneja extracción y carga de datos clínicos"""
    
    @staticmethod
    def load_patient_data(patient_combo, table_widget):
        """Carga datos del paciente en la tabla de historial"""
        patient_name = patient_combo.currentText()
        historial_data = ClinicalDataHandler.get_patient_historial(patient_name)
        
        if not historial_data:
            table_widget.setRowCount(0)
            return
        
        table_widget.setRowCount(len(historial_data))
        for row, (month, bcr_abl, dosis) in enumerate(historial_data):
            # Mes
            item_mes = QTableWidgetItem(str(month))
            table_widget.setItem(row, 0, item_mes)
            
            # BCR-ABL (convertir a porcentaje si es decimal)
            bcr_display = 'ND' if (isinstance(bcr_abl, str) and bcr_abl.upper() == 'ND') else f"{float(bcr_abl) * 100:.2f}"
            item_bcr = QTableWidgetItem(bcr_display)
            table_widget.setItem(row, 1, item_bcr)
            
            # Dosis (convertir a porcentaje)
            dosis_display = f"{float(dosis) * 100:.1f}" if dosis else "0"
            item_dosis = QTableWidgetItem(dosis_display)
            table_widget.setItem(row, 2, item_dosis)
    
    @staticmethod
    def get_clinical_data_from_table(table_widget):
        """Extrae datos clínicos de la tabla para optimización"""
        clinical_data = []
        for row in range(table_widget.rowCount()):
            try:
                month = int(table_widget.item(row, 0).text())
                bcr_text = table_widget.item(row, 1).text().strip()
                dosis_text = table_widget.item(row, 2).text().strip()
                
                # BCR-ABL
                if bcr_text.upper() == 'ND':
                    bcr_abl = 'ND'
                else:
                    bcr_abl = float(bcr_text) / 100.0
                
                # Dosis
                dosis = float(dosis_text) / 100.0 if dosis_text else 0.0
                
                clinical_data.append((month, bcr_abl, dosis))
            except (ValueError, AttributeError):
                continue
        
        return clinical_data
    
    @staticmethod
    def get_patient_historial(patient_name):
        """Retorna datos clínicos precargados del paciente"""
        historial_data = {
            "Christopher Martin Jimenez Osorio": [
                (0, 0.28, 1.0), (3, 0.125, 0.5), 
            ],
            
            # Paciente Clase B: Sistema inmune fuerte - TFR exitosa
            # Alcanza remisión profunda y mantiene control sin droga
            "Paciente Clase B (TFR Exitosa)": [
                # Fase Inicial (Dosis 1.0)
                (0, 1.0, 1.0),          # Diagnóstico (100%)
                (3, 0.10, 1.0),         # Respuesta temprana
                (6, 0.01, 1.0),
                (12, 0.001, 1.0),       # MR3 alcanzado
                (18, 0.0001, 1.0),      # MR4
                (24, 0.00003, 1.0),
                (30, 'ND', 1.0),        # No Detectable
                (36, 0.00002, 1.0),     # Fin dosis completa
                
                # Fase Reducción DESTINY (Dosis 0.5)
                (39, 0.000025, 0.5),    # Leve fluctuación
                (42, 0.00002, 0.5),
                (45, 'ND', 0.5),
                (48, 0.00003, 0.5),     # Listo para parar
                
                # Fase Suspensión (Dosis 0.0)
                (50, 0.00005, 0.0),     # Pequeño rebote inmune
                (52, 0.00008, 0.0),
                (56, 0.00006, 0.0),     # Se estabiliza (Control Inmune)
                (60, 0.00005, 0.0),     # TFR exitosa
                (72, 0.00004, 0.0)
            ],
            
            # Paciente Clase A: Respuesta inmune insuficiente - Recurrencia predecible
            # Sube durante reducción (High Slope = predictor de fallo)
            "Paciente Clase A (Recurrencia)": [
                # Fase Inicial (Dosis 1.0)
                (0, 0.95, 1.0),
                (3, 0.15, 1.0),
                (6, 0.025, 1.0),
                (12, 0.002, 1.0),
                (24, 0.00008, 1.0),     # Buena respuesta inicial (MR4)
                (36, 0.00005, 1.0),
                
                # Fase Reducción DESTINY (Dosis 0.5)
                # NOTA: Sube durante la reducción (High Slope)
                (39, 0.00015, 0.5),     # Sube de 0.00005 a 0.00015
                (42, 0.00035, 0.5),
                (45, 0.0006, 0.5),
                (48, 0.0009, 0.5),      # Casi en fallo (0.1%) antes de parar
                
                # Fase Suspensión (Dosis 0.0)
                (50, 0.005, 0.0),       # Recurrencia inmediata > 0.1%
                (52, 0.02, 0.0),        # Crecimiento exponencial
                (54, 0.10, 0.0)         # Recaída clínica total
            ],
            
            # Paciente Clase C: Capacidad inmune límite - Recurrencia tardía
            # Parece estable durante reducción pero falla al suspender completamente
            "Paciente Clase C (Recurrencia Tardía)": [
                # Fase Inicial (Dosis 1.0)
                (0, 1.0, 1.0),
                (6, 0.005, 1.0),
                (12, 0.0005, 1.0),
                (24, 0.00004, 1.0),
                (36, 0.00002, 1.0),     # Muy buena respuesta profunda
                
                # Fase Reducción DESTINY (Dosis 0.5)
                (40, 0.00002, 0.5),     # Estable (diferente a Clase A)
                (44, 0.00003, 0.5),
                (48, 0.00003, 0.5),     # Parece seguro parar
                
                # Fase Suspensión (Dosis 0.0)
                (50, 0.0001, 0.0),      # Sube lento
                (54, 0.0004, 0.0),      # Sigue subiendo (inmune no frena suficiente)
                (58, 0.0009, 0.0),      # Acercándose al límite
                (60, 0.0015, 0.0),      # Recurrencia tardía (> 0.1%)
                (64, 0.005, 0.0)
            ],
        }
        return historial_data.get(patient_name, [])
