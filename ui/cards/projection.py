from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, 
    QProgressBar, QLabel, QTableWidget, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt

def create_projection_card():
    """Crea card de proyección con botones para cambiar entre Optimizar y Proyectar"""
    card4 = QFrame()
    card4.setObjectName("card")
    card4_layout = QVBoxLayout(card4)
    card4_layout.setContentsMargins(4, 4, 4, 4)
    card4_layout.setSpacing(8)

    # Botones de navegación estilo underline/tab
    nav_widget = QWidget()
    nav_layout = QHBoxLayout(nav_widget)
    nav_layout.setContentsMargins(0, 0, 0, 0)
    nav_layout.setSpacing(20)
    
    btn_optimize = QPushButton("Optimizar")
    btn_optimize.setCheckable(True)
    btn_optimize.setChecked(True)
    btn_optimize.setCursor(Qt.PointingHandCursor)
    btn_optimize.setMinimumWidth(120)
    btn_optimize.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: #9E9E9E;
            border: none;
            border-bottom: 3px solid transparent;
            padding: 8px 12px;
            font-size: 15px;
            font-weight: normal;
        }
        QPushButton:checked {
            color: #2E7D32;
            border-bottom: 3px solid #4CAF50;
            font-weight: bold;
        }
        QPushButton:hover:!checked {
            color: #616161;
        }
    """)
    
    btn_project = QPushButton("Proyectar")
    btn_project.setCheckable(True)
    btn_project.setCursor(Qt.PointingHandCursor)
    btn_project.setMinimumWidth(120)
    btn_project.setStyleSheet(btn_optimize.styleSheet())
    
    nav_layout.addWidget(btn_optimize)
    nav_layout.addWidget(btn_project)
    nav_layout.addStretch()
    
    card4_layout.addWidget(nav_widget)
    
    # ========== VISTA OPTIMIZAR ==========
    view_optimize = QWidget()
    view_optimize_layout = QVBoxLayout(view_optimize)
    view_optimize_layout.setContentsMargins(0, 8, 0, 0)
    view_optimize_layout.setSpacing(8)
    
    card4_layout.addWidget(view_optimize)
    
    # Parámetros
    params_widget = QWidget()
    params_layout = QHBoxLayout(params_widget)
    params_layout.setContentsMargins(0, 0, 0, 0)
    params_layout.setSpacing(8)
    
    # Restarts
    restarts_spin = QSpinBox()
    restarts_spin.setMinimum(1)
    restarts_spin.setMaximum(20)
    restarts_spin.setValue(3)
    restarts_spin.setFixedWidth(50)
    restarts_spin.setFixedHeight(24)
    restarts_spin.setStyleSheet("""
        QSpinBox {
            background-color: white;
            color: black;
            border: 1px solid #CCCCCC;
            border-radius: 3px;
            padding: 2px;
        }
    """)
    
    # Población
    pop_spin = QSpinBox()
    pop_spin.setMinimum(10)
    pop_spin.setMaximum(500)
    pop_spin.setValue(60)
    pop_spin.setFixedWidth(60)
    pop_spin.setFixedHeight(24)
    pop_spin.setStyleSheet(restarts_spin.styleSheet())
    
    # Generaciones
    gens_spin = QSpinBox()
    gens_spin.setMinimum(10)
    gens_spin.setMaximum(500)
    gens_spin.setValue(80)
    gens_spin.setFixedWidth(60)
    gens_spin.setFixedHeight(24)
    gens_spin.setStyleSheet(restarts_spin.styleSheet())
    
    params_layout.addWidget(QLabel("Restarts:"))
    params_layout.addWidget(restarts_spin)
    params_layout.addWidget(QLabel("Población:"))
    params_layout.addWidget(pop_spin)
    params_layout.addWidget(QLabel("Generaciones:"))
    params_layout.addWidget(gens_spin)
    params_layout.addStretch()
    
    view_optimize_layout.addWidget(params_widget)
    
    # Botones de optimización
    opt_buttons = QWidget()
    opt_buttons_layout = QHBoxLayout(opt_buttons)
    opt_buttons_layout.setContentsMargins(0, 0, 0, 0)
    opt_buttons_layout.setSpacing(6)
    
    start_btn = QPushButton("▶ Iniciar")
    start_btn.setFixedHeight(28)
    start_btn.setStyleSheet("""
        QPushButton {
            background-color: #C8E6C9;
            color: #2E7D32;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #A5D6A7;
        }
        QPushButton:pressed {
            background-color: #81C784;
        }
    """)
    
    stop_btn = QPushButton("⏹ Detener")
    stop_btn.setEnabled(False)
    stop_btn.setFixedHeight(28)
    stop_btn.setStyleSheet("""
        QPushButton {
            background-color: #FFCDD2;
            color: #C62828;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover:enabled {
            background-color: #EF9A9A;
        }
        QPushButton:pressed:enabled {
            background-color: #E57373;
        }
        QPushButton:disabled {
            background-color: #F0F0F0;
            color: #AAAAAA;
        }
    """)
    
    opt_buttons_layout.addWidget(start_btn)
    opt_buttons_layout.addWidget(stop_btn)
    opt_buttons_layout.addStretch()
    
    view_optimize_layout.addWidget(opt_buttons)
    
    # Barra de progreso
    proj_progress = QProgressBar()
    proj_progress.setFixedHeight(20)
    proj_progress.setValue(0)
    proj_progress.setStyleSheet("""
        QProgressBar {
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            background-color: #F5F5F5;
            text-align: center;
            font-size: 11px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 3px;
        }
    """)
    
    view_optimize_layout.addWidget(proj_progress)
    
    # Widget de acciones (botones después de optimización)
    actions_widget = QWidget()
    actions_widget.setVisible(False)
    actions_layout = QHBoxLayout(actions_widget)
    actions_layout.setContentsMargins(0, 6, 0, 0)
    actions_layout.setSpacing(6)
    
    view_optimize_layout.addWidget(actions_widget)
    view_optimize_layout.addStretch()
    
    # ========== VISTA PROYECTAR ==========
    view_project = QWidget()
    view_project_layout = QVBoxLayout(view_project)
    view_project_layout.setContentsMargins(0, 8, 0, 0)
    view_project_layout.setSpacing(8)
    view_project.setVisible(False)
    
    card4_layout.addWidget(view_project)
    
    # Botones
    proj_buttons = QWidget()
    proj_buttons_layout = QHBoxLayout(proj_buttons)
    proj_buttons_layout.setContentsMargins(0, 0, 0, 0)
    proj_buttons_layout.setSpacing(6)
    
    project_btn = QPushButton("Proyectar")
    project_btn.setFixedHeight(28)
    project_btn.setStyleSheet("""
        QPushButton {
            background-color: #FFE082;
            color: #F57C00;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #FFD54F;
        }
        QPushButton:pressed {
            background-color: #FFC107;
        }
    """)
    
    plot_opt_btn = QPushButton("Ver Gráficas")
    plot_opt_btn.setFixedHeight(28)
    plot_opt_btn.setStyleSheet("""
        QPushButton {
            background-color: #BBDEFB;
            color: #1565C0;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #90CAF9;
        }
        QPushButton:pressed {
            background-color: #64B5F6;
        }
    """)
    
    proj_buttons_layout.addWidget(project_btn)
    proj_buttons_layout.addWidget(plot_opt_btn)
    proj_buttons_layout.addStretch()
    
    view_project_layout.addWidget(proj_buttons)
    view_project_layout.addStretch()
    
    # Conectar botones usando lambda para evitar funciones anidadas
    btn_optimize.clicked.connect(lambda: (
        btn_optimize.setChecked(True),
        btn_project.setChecked(False),
        view_optimize.setVisible(True),
        view_project.setVisible(False)
    ))
    
    btn_project.clicked.connect(lambda: (
        btn_optimize.setChecked(False),
        btn_project.setChecked(True),
        view_optimize.setVisible(False),
        view_project.setVisible(True)
    ))
    
    # Tabla de resultados
    results_table = QTableWidget(0, 2)
    results_table.setHorizontalHeaderLabels(["Parámetro", "Valor"])
    results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    results_table.setObjectName("results_table")
    results_table.verticalHeader().setVisible(False)
    results_table.verticalHeader().setDefaultSectionSize(28)
    results_table.setStyleSheet("""
        QTableWidget {
            border: none;
        }
        QTableWidget::item {
            padding: 4px;
            border-bottom: 1px solid #F0F0F0;
            border-right: none;
        }
        QHeaderView::section {
            background-color: #C8E6C9;
            padding: 4px;
            border: none;
            font-weight: bold;
            color: #000000;
        }
    """)
    card4_layout.addWidget(results_table, 1)

    # Exportar widgets
    widgets = {
        'btn_optimize': btn_optimize,
        'btn_project': btn_project,
        'view_optimize': view_optimize,
        'view_project': view_project,
        'start_btn': start_btn,
        'stop_btn': stop_btn,
        'proj_progress': proj_progress,
        'results_table': results_table,
        'restarts_spin': restarts_spin,
        'pop_spin': pop_spin,
        'gens_spin': gens_spin,
        'project_btn': project_btn,
        'plot_opt_btn': plot_opt_btn,
        'actions_widget': actions_widget,
        'actions_layout': actions_layout,
    }

    return card4, widgets
