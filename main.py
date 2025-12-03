"""
Aplicación CML - Main Window
Versión refactorizada y modular
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTableWidgetItem, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from ui.styles import STYLES
from ui.sidebar import Sidebar
from ui.helpers import add_shadow, create_card_title
from ui.clinical_handler import ClinicalDataHandler
# Lazy loading: importar bajo demanda en métodos específicos
# from ui.optimizer_core import (...)
# from ui.projection_scenarios import (...)
from ui.cards.simulation import create_simulation_card
from ui.cards.scenarios import create_scenarios_card
from ui.cards.projection import create_projection_card
from ui.cards.patient import create_patient_card
from ui.cards.history import create_history_card


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CML Optimization - Diseño con sidebar y cards")
        
        # Maximizar ventana
        from PySide6.QtCore import Qt as QtCore_Qt
        self.setWindowState(self.windowState() | QtCore_Qt.WindowMaximized)
        
        # Aplicar estilos
        try:
            self.setStyleSheet(STYLES)
        except Exception:
            pass
        
        # Thread de optimización
        self.optimization_thread = None
        
        # Construir UI
        self._build_ui()
        
        # Conectar señales
        self._connect_signals()
        
        # Cargar datos iniciales
        self._load_initial_data()
    
    def _build_ui(self):
        """Construye la interfaz gráfica"""
        # Widget central
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(10)
        self.setCentralWidget(central)
        
        # Sidebar
        sidebar = Sidebar()
        
        # Área principal
        area = QWidget()
        area_layout = QVBoxLayout(area)
        area_layout.setContentsMargins(0, 0, 0, 0)
        area_layout.setSpacing(10)
        
        # Crear cards
        self._setup_cards()
        
        # Agregar cards al área
        area_layout.addWidget(self._create_patient_row(), 1)
        area_layout.addWidget(self._create_projection_row(), 2)
        
        # Agregar al layout principal
        main_layout.addWidget(sidebar)
        main_layout.addWidget(area, 1)
    
    def _setup_cards(self):
        """Crea todas las cards"""
        # Escenarios de tratamiento (reemplaza simulación)
        self.card_scenarios, scenarios_w = create_scenarios_card()
        add_shadow(self.card_scenarios)
        
        # Proyección
        self.card_proj, proj_w = create_projection_card()
        add_shadow(self.card_proj)
        
        # Paciente
        self.card_patient, patient_w = create_patient_card()
        add_shadow(self.card_patient)
        
        # Historial
        self.card_hist, hist_w = create_history_card()
        add_shadow(self.card_hist)
        
        # Guardar referencias
        self._store_widget_refs(scenarios_w, proj_w, patient_w, hist_w)
        
        # Agregar títulos
        if self.card_scenarios.layout():
            self.card_scenarios.layout().insertWidget(0, create_card_title("Escenarios de Tratamiento"))
        if self.card_proj.layout():
            self.card_proj.layout().insertWidget(0, create_card_title("Proyección de respuesta (BCR-ABL)"))
    
    def _store_widget_refs(self, scenarios_w, proj_w, patient_w, hist_w):
        """Almacena referencias a widgets importantes"""
        # Escenarios de tratamiento
        self.scenarios_table = scenarios_w.get('table')
        self.mes_inicio_spin = scenarios_w.get('mes_inicio_spin')
        self.mes_fin_spin = scenarios_w.get('mes_fin_spin')
        self.dosis_spin = scenarios_w.get('dosis_spin')
        self.scenario_add_btn = scenarios_w.get('btn_add')
        self.scenario_update_btn = scenarios_w.get('btn_update')
        self.scenario_delete_btn = scenarios_w.get('btn_delete')
        self.strategy_combo = scenarios_w.get('strategy_combo')
        
        # Proyección
        self.btn_optimize = proj_w.get('btn_optimize')
        self.btn_project = proj_w.get('btn_project')
        self.view_optimize = proj_w.get('view_optimize')
        self.view_project = proj_w.get('view_project')
        self.start_btn = proj_w.get('start_btn')
        self.stop_btn = proj_w.get('stop_btn')
        self.sim_progress = proj_w.get('proj_progress')
        self.results_table = proj_w.get('results_table')
        self.restarts_spin = proj_w.get('restarts_spin')
        self.pop_spin = proj_w.get('pop_spin')
        self.gens_spin = proj_w.get('gens_spin')
        self.project_btn = proj_w.get('project_btn')
        self.plot_opt_btn = proj_w.get('plot_opt_btn')
        self.actions_widget = proj_w.get('actions_widget')
        self.actions_layout = proj_w.get('actions_layout')
        self.actions_widget = proj_w.get('actions_widget')
        self.actions_layout = proj_w.get('actions_layout')
        
        # Paciente
        self.patient_nombre = patient_w.get('patient_nombre')
        self.patient_edad = patient_w.get('patient_edad')
        self.patient_clave = patient_w.get('patient_clave')
        self.patient_sexo = patient_w.get('patient_sexo')
        self.patient_combo = patient_w.get('patient_combo')
        
        # Historial
        self.tabla = hist_w.get('tabla')
        self.mes_input = hist_w.get('mes_input')
        self.dosis_input = hist_w.get('dosis_input')
        self.porc_input = hist_w.get('porc_input')
        self.hist_add_btn = hist_w.get('add_btn')
        self.hist_update_btn = hist_w.get('update_btn')
        self.hist_del_btn = hist_w.get('del_btn')
    
    def _create_patient_row(self):
        """Crea fila con cards de paciente e historial"""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.card_patient, 1)
        layout.addWidget(self.card_hist, 2)
        return row
    
    def _create_projection_row(self):
        """Crea fila con cards de escenarios y proyección"""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.card_scenarios, 1)
        layout.addWidget(self.card_proj, 2)
        return row
    
    def _connect_signals(self):
        """Conecta todas las señales"""
        # Botones de optimización
        self.start_btn.clicked.connect(self._on_start_optimization)
        self.stop_btn.clicked.connect(self._on_stop_optimization)
        self.project_btn.clicked.connect(self._on_projection_button_clicked)
        self.plot_opt_btn.clicked.connect(self._on_show_optimization_plots)
        
        # Tab widget de proyección (no necesita conexión)
        
        # Pacientes
        self.patient_combo.currentIndexChanged.connect(self._on_patient_selected)
        
        # Historial
        self.hist_add_btn.clicked.connect(self._on_add_history_row)
        self.hist_update_btn.clicked.connect(self._on_update_history_row)
        self.hist_del_btn.clicked.connect(self._on_delete_history_row)
        self.tabla.itemSelectionChanged.connect(self._on_history_selection)
        
        # Escenarios
        self.scenario_add_btn.clicked.connect(self._on_add_scenario_row)
        self.scenario_update_btn.clicked.connect(self._on_update_scenario_row)
        self.scenario_delete_btn.clicked.connect(self._on_delete_scenario_row)
        self.scenarios_table.itemSelectionChanged.connect(self._on_scenario_selection)
        self.strategy_combo.currentIndexChanged.connect(self._on_apply_strategy)
    
    def _load_initial_data(self):
        """Carga datos iniciales"""
        # No pre-seleccionar paciente, dejar combobox vacío
        pass
    
    def _show_warning_red(self, title, message):
        """Muestra un QMessageBox warning con texto en rojo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet("QMessageBox { background-color: white; } QLabel { background-color: white; }")
        
        # Aplicar color rojo al texto
        label = msg_box.findChild(QLabel)
        if label:
            label.setStyleSheet("color: red; font-weight: bold; background-color: white;")
        
        msg_box.exec()
    
    # ========== OPTIMIZACIÓN ==========
    def _start_optimization(self):
        """Inicia la optimización genética"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.sim_progress.setValue(0)
        self.actions_widget.setVisible(False)
        
        # Extraer datos clínicos
        clinical_data = ClinicalDataHandler.get_clinical_data_from_table(self.tabla)
        
        if not clinical_data:
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self._show_warning_red("Advertencia", "⚠️ Sin datos clínicos para optimizar.\n\nPor favor, carga datos en el historial de medicación.")
            return
        
        # Obtener nombre del paciente
        patient_name = self.patient_combo.currentText()
        
        # Obtener parámetros GA
        restarts = self.restarts_spin.value()
        pop_size = self.pop_spin.value()
        generations = self.gens_spin.value()
        
        # Importar bajo demanda
        from ui.optimizer_core import OptimizationThread
        
        # Crear thread de optimización
        self.optimization_thread = OptimizationThread(
            clinical_data, 
            patient_name,
            restarts=restarts,
            pop_size=pop_size,
            generations=generations
        )
        self.optimization_thread.progress.connect(self._on_optimization_progress)
        self.optimization_thread.status_update.connect(self._on_optimization_status)
        self.optimization_thread.finished.connect(self._on_optimization_finished)
        self.optimization_thread.error.connect(self._on_optimization_error)
        self.optimization_thread.start()        
        msg_box_obj = QMessageBox(self)
        msg_box_obj.setWindowTitle("Optimización Iniciada")
        msg_box_obj.setText(f"✓ Optimización iniciada para {patient_name}\n\nRestarts: {restarts}\nPoblación: {pop_size}\nGeneraciones: {generations}\nDatos: {len(clinical_data)} puntos")
        msg_box_obj.setIcon(QMessageBox.Information)
        msg_box_obj.setStyleSheet("QMessageBox { background-color: white; } QLabel { background-color: white; }")
        msg_box_obj.exec()
        
        print(f"✓ Optimización iniciada para {patient_name}")
        print(f"  Restarts: {restarts}, Población: {pop_size}, Generaciones: {generations}")
        print(f"  Datos: {len(clinical_data)} puntos")
    
    def _on_optimization_progress(self, progress):
        """Actualiza progreso"""
        self.sim_progress.setValue(progress)
    
    def _on_optimization_status(self, status_msg):
        """Actualiza estado"""
        print(f"  {status_msg}")
    
    def _on_optimization_finished(self, solution, fitness, history):
        """Maneja fin de optimización"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.sim_progress.setValue(100)
        
        # Guardar referencia a datos de optimización para gráficas
        self.best_solution = solution
        self.best_fitness = fitness
        self.best_history = history
        self.clinical_data_optimization = ClinicalDataHandler.get_clinical_data_from_table(self.tabla)
        
        # Mostrar resultados en tabla
        self.results_table.setRowCount(0)
        
        # Agregar parámetros
        params_to_show = [
            'initLRATIO', 'TKI_effect', 'p_XY', 'p_YX', 'p_Y', 'K_Z', 'p_Z'
        ]
        
        row = 0
        for param in params_to_show:
            if param in solution:
                value = solution[param]
                if param in ['p_XY', 'p_YX', 'K_Z', 'p_Z']:
                    value_str = f"{value:.6e}"
                else:
                    value_str = f"{value:.6f}"
                
                self.results_table.insertRow(row)
                item_param = QTableWidgetItem(param)
                item_value = QTableWidgetItem(value_str)
                self.results_table.setItem(row, 0, item_param)
                self.results_table.setItem(row, 1, item_value)
                row += 1
        
        # Agregar fitness
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem("Fitness"))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"{fitness:.6e}"))
        row += 1
        
        # Agregar error
        error_val = -fitness if fitness is not None else 0
        self.results_table.insertRow(row)
        self.results_table.setItem(row, 0, QTableWidgetItem("Error"))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"{error_val:.6e}"))
        
        # Agregar botones de acciones
        self._add_action_buttons_to_results()
        
        # Mostrar mensaje de éxito
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Optimización Completada")
        msg_box.setText(f"✓ Optimización completada exitosamente\n\nFitness: {fitness:.6e}\nError: {error_val:.6e}\n\nPuedes ver las gráficas o guardar los resultados.")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet("QMessageBox { background-color: white; } QLabel { background-color: white; }")
        msg_box.exec()
        
        print("✓ Optimización completada")
        print(f"  Fitness: {fitness:.6e}")
    
    def _add_action_buttons_to_results(self):
        """Agrega botones de acciones visibles al lado de la barra de progreso"""
        # Limpiar layout anterior
        while self.actions_layout.count():
            child = self.actions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Botón Ver Gráficas
        btn_plots = QPushButton("Ver Gráficas")
        btn_plots.setFixedHeight(28)
        btn_plots.setMinimumWidth(110)
        btn_plots.setStyleSheet("""
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
        btn_plots.clicked.connect(self._on_show_plots)
        
        # Botón Guardar JSON
        btn_save = QPushButton("Guardar JSON")
        btn_save.setFixedHeight(28)
        btn_save.setMinimumWidth(110)
        btn_save.setStyleSheet("""
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
        btn_save.clicked.connect(self._on_save_results)
        
        # Agregar botones al layout con stretch al inicio
        self.actions_layout.insertStretch(0)
        self.actions_layout.addWidget(btn_plots)
        self.actions_layout.addWidget(btn_save)
        
        # Mostrar el widget de acciones
        self.actions_widget.setVisible(True)
    
    def _on_show_plots(self):
        """Muestra gráficas de optimización"""
        if hasattr(self, 'best_solution') and self.best_solution:
            try:
                from ui.optimizer_core import plot_optimization_results
                plot_optimization_results(self.best_solution, self.clinical_data_optimization)
            except Exception as e:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Error al Mostrar Gráficas")
                msg_box.setText(f"✗ Error: {str(e)}")
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setStyleSheet("QMessageBox { background-color: white; } QLabel { background-color: white; }")
                msg_box.exec()
                print(f"✗ Error al mostrar gráficas: {str(e)}")
        else:
            self._show_warning_red("Advertencia", "⚠️ No hay resultados de optimización para mostrar gráficas.")
    
    def _on_save_results(self):
        """Guarda resultados con confirmación"""
        if hasattr(self, 'best_solution') and self.best_solution:
            from ui.optimizer_core import save_optimization_results
            patient_name = self.patient_combo.currentText()
            save_optimization_results(self.best_solution, self.best_fitness, patient_name)
        else:
            self._show_warning_red("Advertencia", "⚠️ No hay resultados de optimización para guardar.")
    
    def _on_optimization_error(self, error_msg):
        """Maneja errores de optimización"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.sim_progress.setValue(0)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error en Optimización")
        msg_box.setText(f"✗ Error: {error_msg}")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStyleSheet("QMessageBox { background-color: white; } QLabel { background-color: white; }")
        msg_box.exec()
        print(f"✗ Error: {error_msg}")
    
    def _on_start_optimization(self):
        """Inicia la optimización (botón)"""
        self._start_optimization()
    
    def _on_stop_optimization(self):
        """Detiene la optimización"""
        if self.optimization_thread and self.optimization_thread.isRunning():
            self.optimization_thread.stop()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.sim_progress.setValue(0)
        print("⊛ Optimización detenida")
    
    def _on_projection_button_clicked(self):
        """Maneja proyección con estrategias"""
        from ui.projection_scenarios import load_patient_parameters, plot_projection_with_strategies
        
        patient_name = self.patient_combo.currentText()
        
        if not patient_name:
            self._show_warning_red("Advertencia", "⚠️ Por favor, selecciona un paciente.")
            return
        
        # Verificar si existen parámetros guardados
        params, error = load_patient_parameters(patient_name)
        
        if not params:
            self._show_warning_red("Advertencia", f"⚠️ No se encontraron parámetros optimizados para {patient_name}.\n\nPor favor, ejecuta primero una optimización.")
            return
        
        # Obtener datos clínicos de la tabla
        clinical_data = ClinicalDataHandler.get_clinical_data_from_table(self.tabla)
        
        if not clinical_data:
            self._show_warning_red("Advertencia", "⚠️ No hay datos clínicos para proyectar.")
            return
        
        # Obtener escenarios de la tabla de escenarios
        scenarios_data = []
        for row in range(self.scenarios_table.rowCount()):
            mes_inicio_item = self.scenarios_table.item(row, 0)
            mes_fin_item = self.scenarios_table.item(row, 1)
            dosis_item = self.scenarios_table.item(row, 2)
            
            if mes_inicio_item and mes_fin_item and dosis_item:
                mes_inicio = int(mes_inicio_item.text())
                mes_fin = int(mes_fin_item.text())
                dosis_text = dosis_item.text().replace("%", "")
                dosis = float(dosis_text)
                scenarios_data.append((mes_inicio, mes_fin, dosis))
        
        # Determinar qué estrategias mostrar
        strategy_map = {
            0: ['tapering'],  # Solo Tapering
        }
        strategies = strategy_map.get(self.strategy_combo.currentIndex(), ['tapering'])
        
        # Mostrar gráficas pasando los escenarios
        success, message = plot_projection_with_strategies(patient_name, clinical_data, strategies, scenarios_data=scenarios_data if scenarios_data else None)
        
        if success:
            print(f"✓ Proyección mostrada para {patient_name}")
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Error al Mostrar Proyección")
            msg_box.setText(f"✗ {message}")
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setStyleSheet("QMessageBox { background-color: white; } QLabel { background-color: white; }")
            msg_box.exec()
    
    # ========== PACIENTES ==========
    def _display_parameters_in_table(self, params, error):
        """Muestra parámetros optimizados en la tabla de resultados"""
        self.results_table.setRowCount(0)
        
        # Agregar parámetros
        params_to_show = [
            'initLRATIO', 'TKI_effect', 'p_XY', 'p_YX', 'p_Y', 'K_Z', 'p_Z'
        ]
        
        row = 0
        for param in params_to_show:
            if param in params:
                value = params[param]
                if param in ['p_XY', 'p_YX', 'K_Z', 'p_Z']:
                    value_str = f"{value:.6e}"
                else:
                    value_str = f"{value:.6f}"
                
                self.results_table.insertRow(row)
                item_param = QTableWidgetItem(param)
                item_value = QTableWidgetItem(value_str)
                self.results_table.setItem(row, 0, item_param)
                self.results_table.setItem(row, 1, item_value)
                row += 1
        
        # Agregar error si existe
        if error is not None:
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QTableWidgetItem("Error"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{error:.6e}"))
    
    def _on_show_optimization_plots(self):
        """Muestra gráficas de optimización del paciente actual"""
        patient_name = self.patient_combo.currentText()
        
        if not patient_name:
            self._show_warning_red("Advertencia", "⚠️ Por favor, selecciona un paciente.")
            return
        
        from ui.projection_scenarios import load_patient_parameters
        params, error = load_patient_parameters(patient_name)
        
        if not params:
            self._show_warning_red("Advertencia", "⚠️ No hay parámetros optimizados para este paciente.")
            return
        
        # Obtener datos clínicos
        clinical_data = ClinicalDataHandler.get_clinical_data_from_table(self.tabla)
        
        if not clinical_data:
            self._show_warning_red("Advertencia", "⚠️ No hay datos clínicos para mostrar gráficas.")
            return
        
        try:
            from ui.optimizer_core import plot_optimization_results
            plot_optimization_results(params, clinical_data)
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Error al Mostrar Gráficas")
            msg_box.setText(f"✗ Error: {str(e)}")
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setStyleSheet("QMessageBox { background-color: white; } QLabel { background-color: white; }")
            msg_box.exec()
            print(f"✗ Error al mostrar gráficas: {str(e)}")
    
    # ========== PACIENTES ==========
    def _on_patient_selected(self, index):
        """Carga datos del paciente seleccionado"""
        from ui.projection_scenarios import load_patient_parameters
        
        patient_name = self.patient_combo.currentText()
        
        # Si está vacío, limpiar datos
        if not patient_name:
            self.tabla.setRowCount(0)
            self.patient_nombre.setText("Nombre: —")
            self.patient_edad.setText("Edad: —")
            self.patient_clave.setText("Clave: —")
            self.patient_sexo.setText("Sexo: —")
            self.results_table.setRowCount(0)
            return
        
        # Cargar datos del paciente
        ClinicalDataHandler.load_patient_data(self.patient_combo, self.tabla)
        
        # Datos de pacientes
        patient_data = {
            "Christopher Martin Jimenez Osorio": {'edad': '23', 'clave': '517259', 'sexo': 'Masculino'},
            "Paciente Clase B (TFR Exitosa)": {'edad': '45', 'clave': 'CLASS-B', 'sexo': 'Femenino'},
            "Paciente Clase A (Recurrencia)": {'edad': '52', 'clave': 'CLASS-A', 'sexo': 'Masculino'},
            "Paciente Clase C (Recurrencia Tardía)": {'edad': '38', 'clave': 'CLASS-C', 'sexo': 'Femenino'},
        }
        
        data = patient_data.get(patient_name, {'edad': '—', 'clave': '—', 'sexo': '—'})
        self.patient_nombre.setText(f"Nombre: {patient_name}")
        self.patient_edad.setText(f"Edad: {data['edad']}")
        self.patient_clave.setText(f"Clave: {data['clave']}")
        self.patient_sexo.setText(f"Sexo: {data['sexo']}")
        
        # Cargar parámetros optimizados si existen
        params, error = load_patient_parameters(patient_name)
        if params:
            self._display_parameters_in_table(params, error)
        else:
            self.results_table.setRowCount(0)
    
    # ========== HISTORIAL ==========
    def _on_add_history_row(self):
        """Agrega fila al historial"""
        from PySide6.QtWidgets import QTableWidgetItem
        
        mes = str(int(self.mes_input.value()))
        dosis = str(self.dosis_input.value())
        porc = str(self.porc_input.value())
        
        if mes == "0" and dosis == "0.0" and porc == "0.0":
            self._show_warning_red("Campos Vacíos", "⚠️ Por favor, completa al menos un campo (Mes, Dosis o BCR-ABL%).")
            return
        
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        self.tabla.setItem(row, 0, QTableWidgetItem(mes))
        self.tabla.setItem(row, 1, QTableWidgetItem(porc))
        self.tabla.setItem(row, 2, QTableWidgetItem(dosis))
        
        # Limpiar campos
        self.mes_input.setValue(0)
        self.dosis_input.setValue(0)
        self.porc_input.setValue(0)
    
    def _on_update_history_row(self):
        """Actualiza fila del historial"""
        from PySide6.QtWidgets import QTableWidgetItem
        
        row = self.tabla.currentRow()
        if row < 0:
            self._show_warning_red("Advertencia", "⚠️ Por favor, selecciona una fila para actualizar.")
            return
        
        mes = str(int(self.mes_input.value()))
        dosis = str(self.dosis_input.value())
        porc = str(self.porc_input.value())
        
        self.tabla.setItem(row, 0, QTableWidgetItem(mes))
        self.tabla.setItem(row, 1, QTableWidgetItem(porc))
        self.tabla.setItem(row, 2, QTableWidgetItem(dosis))
    
    def _on_delete_history_row(self):
        """Elimina fila del historial"""
        row = self.tabla.currentRow()
        if row >= 0:
            self.tabla.removeRow(row)
        else:
            self._show_warning_red("Advertencia", "⚠️ Por favor, selecciona una fila para eliminar.")
    
    def _on_history_selection(self):
        """Carga datos de fila seleccionada en campos de entrada"""
        row = self.tabla.currentRow()
        if row < 0:
            return
        
        mes_item = self.tabla.item(row, 0)
        porc_item = self.tabla.item(row, 1)
        dosis_item = self.tabla.item(row, 2)
        
        if mes_item:
            self.mes_input.setValue(int(mes_item.text()))
        if porc_item:
            self.porc_input.setValue(float(porc_item.text()))
        if dosis_item:
            self.dosis_input.setValue(float(dosis_item.text()))
    
    # ========== ESCENARIOS ==========
    def _on_add_scenario_row(self):
        """Agrega fila al tabla de escenarios"""
        mes_inicio = int(self.mes_inicio_spin.value())
        mes_fin = int(self.mes_fin_spin.value())
        dosis = self.dosis_spin.value()
        
        if mes_fin < mes_inicio:
            self._show_warning_red("Error", "⚠️ Mes Fin debe ser mayor o igual a Mes Inicio.")
            return
        
        row = self.scenarios_table.rowCount()
        self.scenarios_table.insertRow(row)
        self.scenarios_table.setItem(row, 0, QTableWidgetItem(str(mes_inicio)))
        self.scenarios_table.setItem(row, 1, QTableWidgetItem(str(mes_fin)))
        self.scenarios_table.setItem(row, 2, QTableWidgetItem(f"{dosis}%"))
    
    def _on_update_scenario_row(self):
        """Actualiza fila del tabla de escenarios"""
        row = self.scenarios_table.currentRow()
        if row < 0:
            self._show_warning_red("Advertencia", "⚠️ Por favor, selecciona una fila para actualizar.")
            return
        
        mes_inicio = int(self.mes_inicio_spin.value())
        mes_fin = int(self.mes_fin_spin.value())
        dosis = self.dosis_spin.value()
        
        if mes_fin < mes_inicio:
            self._show_warning_red("Error", "⚠️ Mes Fin debe ser mayor o igual a Mes Inicio.")
            return
        
        self.scenarios_table.setItem(row, 0, QTableWidgetItem(str(mes_inicio)))
        self.scenarios_table.setItem(row, 1, QTableWidgetItem(str(mes_fin)))
        self.scenarios_table.setItem(row, 2, QTableWidgetItem(f"{dosis}%"))
    
    def _on_delete_scenario_row(self):
        """Elimina fila del tabla de escenarios"""
        row = self.scenarios_table.currentRow()
        if row >= 0:
            self.scenarios_table.removeRow(row)
        else:
            self._show_warning_red("Advertencia", "⚠️ Por favor, selecciona una fila para eliminar.")
    
    def _on_scenario_selection(self):
        """Carga datos de fila seleccionada de escenarios en campos de entrada"""
        row = self.scenarios_table.currentRow()
        if row < 0:
            return
        
        mes_inicio_item = self.scenarios_table.item(row, 0)
        mes_fin_item = self.scenarios_table.item(row, 1)
        dosis_item = self.scenarios_table.item(row, 2)
        
        if mes_inicio_item:
            self.mes_inicio_spin.setValue(int(mes_inicio_item.text()))
        if mes_fin_item:
            self.mes_fin_spin.setValue(int(mes_fin_item.text()))
        if dosis_item:
            # Remover el símbolo % y convertir a float
            dosis_text = dosis_item.text().replace("%", "")
            self.dosis_spin.setValue(float(dosis_text))
    
    def _on_apply_strategy(self):
        """Aplica la estrategia seleccionada del combobox a la tabla de escenarios"""
        strategy_index = self.strategy_combo.currentIndex()
        strategy_name = self.strategy_combo.currentText()
        
        # Limpiar tabla actual
        self.scenarios_table.setRowCount(0)
        
        # Definir escenarios según estrategia
        scenarios = []
        
        if strategy_index == 0:
            # Opción vacía - no hacer nada
            return
        
        elif strategy_index == 1:
            # Manual - no hacer nada, usuario define
            return
        
        elif strategy_index == 2:
            # MR4+36M (Control - Dosis completa)
            # 36 meses a dosis completa después de MR4
            scenarios = [
                (0, 36, 100.0),
                (37, 120, 0.0)  # Suspensión
            ]
        
        elif strategy_index == 3:
            # MR4+24M+12M50% (DESTINY estándar)
            # 24 meses completa + 12 meses al 50%
            scenarios = [
                (0, 24, 100.0),
                (25, 36, 50.0),
                (37, 120, 0.0)
            ]
        
        elif strategy_index == 4:
            # MR4+24M+12M25% (DESTINY 25%)
            # 24 meses completa + 12 meses al 25%
            scenarios = [
                (0, 24, 100.0),
                (25, 36, 25.0),
                (37, 120, 0.0)
            ]
        
        elif strategy_index == 5:
            # MR4+12M+12M50%+12M25% (Escalonada - PROPUESTA NOVEDOSA)
            # 12 meses completa + 12 al 50% + 12 al 25%
            # Usa solo 58% de la droga total
            scenarios = [
                (0, 12, 100.0),
                (13, 24, 50.0),
                (25, 36, 25.0),
                (37, 120, 0.0)
            ]
        
        elif strategy_index == 6:
            # MR4+12M+24M50% (Reducción prolongada)
            # Solo 12 meses completa + 24 meses reducida
            scenarios = [
                (0, 12, 100.0),
                (13, 36, 50.0),
                (37, 120, 0.0)
            ]
        
        elif strategy_index == 7:
            # MR4+36M50% (Reducción inmediata 50%)
            # Reducir al 50% inmediatamente después de MR4
            scenarios = [
                (0, 36, 50.0),
                (37, 120, 0.0)
            ]
        
        elif strategy_index == 8:
            # MR4+36M25% (Reducción inmediata 25%)
            # Reducir al 25% inmediatamente después de MR4
            scenarios = [
                (0, 36, 25.0),
                (37, 120, 0.0)
            ]
        
        # Llenar tabla con escenarios
        for mes_inicio, mes_fin, dosis in scenarios:
            row = self.scenarios_table.rowCount()
            self.scenarios_table.insertRow(row)
            self.scenarios_table.setItem(row, 0, QTableWidgetItem(str(mes_inicio)))
            self.scenarios_table.setItem(row, 1, QTableWidgetItem(str(mes_fin)))
            self.scenarios_table.setItem(row, 2, QTableWidgetItem(f"{dosis}%"))
        
        print(f"✓ Estrategia aplicada: {strategy_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
