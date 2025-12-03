def create_info_panel(ax, patient_name, clinical_data, params, scenarios_data=None, projection_end=None):
    """
    Crea un panel informativo en la gráfica con interpretación según el autor
    """
    # Recolectar información básica
    clinical_months = [d[0] for d in clinical_data]
    last_month = clinical_months[-1] if clinical_months else 0

    # Calcular estadísticas del modelo para interpretación
    measurable_points = sum(1 for d in clinical_data if not (isinstance(d[1], str) and d[1].upper() == 'ND'))
    nd_points = len(clinical_data) - measurable_points

    # Texto principal
    info_text = f"📋 {patient_name}\n"
    info_text += "─" * 30 + "\n"
    info_text += f"• Datos: {len(clinical_data)} pts ({measurable_points} medibles)\n"

    # INTERPRETACIÓN SEGÚN EL AUTOR (puntos clave)
    info_text += "\n🔬 INTERPRETACIÓN (según Karg et al., 2022):\n"
    info_text += "─" * 30 + "\n"
    key_points = [
        "• Reducción escalonada de TKI antes del cese puede ↑ TFR",
        "• Duración total del tratamiento es clave para TFR",
        "• Dosis más bajas son suficientes para muchos pacientes",
        "• Sistema inmune controla enfermedad residual"
    ]
    for point in key_points:
        info_text += f"{point}\n"

    # Si hay escenarios aplicados, añadir nota específica
    if scenarios_data:
        total_dose_months = sum((end-start) * (dose/100) for start, end, dose in scenarios_data)
        full_dose_months = sum((end-start) for start, end, dose in scenarios_data)
        dose_reduction = (1 - total_dose_months/full_dose_months) * 100 if full_dose_months > 0 else 0
        info_text += f"\n💊 Reducción de dosis en escenarios:\n"
        info_text += f"  - Total: {dose_reduction:.1f}% menos TKI\n"
        # Evaluación del riesgo basada en parámetros del modelo
        if params and 'p_Z' in params:
            immune_strength = params.get('p_Z', 0)
            if immune_strength > 0.1:
                info_text += f"  - Sistema inmune: FUERTE (p_Z={immune_strength:.3f})\n"
                info_text += f"  → Buen candidato para reducción\n"
            else:
                info_text += f"  - Sistema inmune: DÉBIL (p_Z={immune_strength:.3f})\n"
                info_text += f"  → Precaución con reducción\n"

    # Calcular posición del cuadro (esquina superior derecha)
    x_pos = 0.98
    y_pos = 0.98

    # Crear cuadro de texto con fondo profesional
    ax.text(x_pos, y_pos, info_text, 
            transform=ax.transAxes,
            fontsize=8.5,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.5',
                     facecolor='white',
                     edgecolor='#2E86AB',
                     alpha=0.95,
                     linewidth=1.5),
            linespacing=1.3,
            fontfamily='monospace')
    return info_text
"""
Proyecciones y escenarios para CML
Funciones: Estrategias de dosificación, proyecciones, gráficas de escenarios
"""
import json
import math
import numpy as np
from scipy.integrate import odeint

# matplotlib se importa bajo demanda en funciones que lo necesitan

from ui.optimizer_core import (
    cml_model, get_initial_conditions, 
    simulate_model_with_variable_dosing,
    calculate_bcr_abl_ratio_decimal, DETECTION_LIMIT
)

# ========== DOSIS SCHEDULE ==========

def generate_dose_schedule_tapering(months, dose_schedule=None, taper_interval=25, taper_rate=0.25):
    """
    Genera un calendario de dosis.

    Soporta dos modos de uso (compatibilidad hacia atrás):
    1) Nuevo (lista de intervalos):
       - `dose_schedule` es una lista de tuplas `(start, end, dose)`.
         Ejemplo: `[(0,24,0.5),(25,49,0.25),(50,120,0.0)]`.
    2) Antiguo (compatibilidad):
       - `dose_schedule` puede ser un número (float) que representa la `initial_dose`.
         En ese caso se aplica el comportamiento clásico: cada `taper_interval` meses
         se reduce `taper_rate` (fracción) de la dosis inicial.

    Si `dose_schedule` es `None`, se usa un patrón por defecto.
    """
    schedule = {}

    # Caso: se pasó una lista manual de intervalos (nuevo modo)
    if isinstance(dose_schedule, (list, tuple)):
        intervals = dose_schedule
    # Caso: se pasó una sola dosis (legacy)
    elif isinstance(dose_schedule, (int, float)):
        initial_dose = float(dose_schedule)
        intervals = []
        max_steps = int(math.ceil(1.0 / max(1e-9, taper_rate)))
        for step in range(0, max_steps + 1):
            start = step * taper_interval
            # CORREGIDO: Sin gaps - el end debe llegar hasta el siguiente start
            if step < max_steps:
                end = (step + 1) * taper_interval
            else:
                end = int(months)
            percentage_remaining = max(0.0, 1.0 - step * taper_rate)
            dose_val = percentage_remaining * initial_dose
            intervals.append((start, end, dose_val))
    # Caso: no se pasó nada -> patrón por defecto (sin gaps)
    else:
        intervals = [(0, 25, 0.5), (25, 50, 0.25), (50, int(months), 0.0)]

    # Llenar el calendario según los intervalos
    for month in range(0, int(months) + 1):
        assigned = False
        for start, end, dose in intervals:
            if start <= month <= end:
                schedule[month] = dose
                assigned = True
                break
        if not assigned:
            if intervals:
                schedule[month] = intervals[-1][2]
            else:
                schedule[month] = 0.0

    return schedule


# ========== PROYECCIONES CON ESTRATEGIAS ==========

def load_patient_parameters(patient_name):
    """Carga los parámetros guardados de un paciente"""
    filename = f"{patient_name.replace(' ', '_')}_optimization.json"
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data.get('parameters'), data.get('error')
    except FileNotFoundError:
        return None, None


def project_model_with_strategy(params, clinical_data, strategy_name="tapering", projection_months=60):
    """
    Proyecta el modelo BCR-ABL con diferentes estrategias de dosificación
    
    Estrategias:
    - 'tapering': Reduce dosis según intervalo manual
    - 'continuous': Mantiene dosis constante del último punto
    - 'increased': Aumenta dosis gradualmente
    """
    if not params or not clinical_data:
        return None, None
    
    # Extraer últimos datos clínicos
    last_month = clinical_data[-1][0]
    last_dose = clinical_data[-1][2]
    
    # Generar proyección a futuro
    projection_end = max(last_month + projection_months, last_month + 60)
    
    if strategy_name == "tapering":
        dose_schedule = generate_dose_schedule_tapering(projection_end, last_dose)
    elif strategy_name == "continuous":
        dose_schedule = {month: last_dose for month in range(int(projection_end) + 1)}
    elif strategy_name == "increased":
        dose_schedule = {}
        for month in range(int(projection_end) + 1):
            dose_schedule[month] = min(1.0, last_dose * (1.0 + 0.01 * month))
    else:
        dose_schedule = {month: last_dose for month in range(int(projection_end) + 1)}
    
    # CORREGIDO: Usar simulate_model_with_variable_dosing que es más robusto
    # Convertir dose_schedule a lista de (tiempo, dosis)
    time_dose_pairs = [(month, dose_schedule.get(month, last_dose)) 
                       for month in range(int(last_month), int(projection_end) + 1)]
    
    # Simular usando la función optimizada del core
    solution, time_points = simulate_model_with_variable_dosing(params, time_dose_pairs)
    
    # Verificar que la simulación fue exitosa
    if np.any(np.isnan(solution)):
        return None, None
    
    # Extraer resultados
    bcr_abl_projection = []
    for idx, (t, Y_val) in enumerate(zip(time_points, solution[:, 1])):
        bcr_ratio = calculate_bcr_abl_ratio_decimal(Y_val)
        bcr_abl_projection.append({
            'month': t,
            'bcr_abl': bcr_ratio,
            'dose': time_dose_pairs[idx][1]
        })
    
    return time_points, bcr_abl_projection


def evaluate_recurrence_risk(params, clinical_data, projection_months=24):
    """Evalúa el riesgo de recurrencia sin tratamiento"""
    try:
        last_clinical_month = clinical_data[-1][0]
        
        # Simular con cesación completa
        projection_end = last_clinical_month + projection_months
        time_points = np.linspace(last_clinical_month, projection_end, 
                                 int(projection_end - last_clinical_month) + 1)
        
        # CORREGIDO: Obtener estado final del período clínico correctamente
        # Simular período clínico completo desde t=0
        clinical_time_dose = [(t, dose) for (t, val, dose) in clinical_data]
        clinical_solution, clinical_times = simulate_model_with_variable_dosing(params, clinical_time_dose)
        
        # Verificar simulación válida y usar último estado
        if np.any(np.isnan(clinical_solution)):
            # Si falla, usar condiciones iniciales
            y0 = get_initial_conditions(params)
        else:
            # Usar el estado que corresponde al último mes clínico
            y0 = clinical_solution[-1]
        
        # Simular proyección sin tratamiento
        def model_no_treatment(y, t):
            return cml_model(y, t, params, dose_factor=0.0)
        
        solution = odeint(model_no_treatment, y0, time_points, rtol=1e-6, atol=1e-8, mxstep=10000)
        Y_proj = solution[:, 1]
        
        # Calcular BCR-ABL durante proyección
        bcr_abl_proj = [calculate_bcr_abl_ratio_decimal(y) * 100 for y in Y_proj]
        
        # Evaluar riesgo
        max_bcr_abl = max(bcr_abl_proj)
        time_above_mr3 = sum(1 for ratio in bcr_abl_proj if ratio > 0.1)
        risk_score = min(1.0, max_bcr_abl / 10.0)
        
        risk_level = "Alto" if risk_score > 0.5 else "Moderado" if risk_score > 0.2 else "Bajo"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'max_bcr_abl': max_bcr_abl,
            'months_above_mr3': time_above_mr3,
            'projection_data': list(zip(time_points, bcr_abl_proj))
        }
        
    except Exception as e:
        print(f"Error en evaluación de riesgo: {e}")
        return None


# ========== GRÁFICAS DE PROYECCIÓN ==========

def plot_projection_with_strategies(patient_name, clinical_data, strategies=['tapering'], scenarios_data=None):
    """
    Crea gráficas de proyección con puntos reales y curva completa desde inicio
    Respeta la dosis real del último punto clínico
    
    scenarios_data: lista de escenarios de la tabla [(mes_inicio, mes_fin, dosis), ...]
    """
    params, error = load_patient_parameters(patient_name)
    
    if not params:
        return False, "No se encontraron parámetros optimizados para este paciente"
    
    try:
        # CARGAR HISTORIAL COMPLETO PARA GRAFICAR PUNTOS Y DOSIS REALES
        from ui.clinical_handler import ClinicalDataHandler
        full_historial = ClinicalDataHandler.get_patient_historial(patient_name)
        
        # IMPORTANTE: Para que la proyección coincida con la optimización,
        # debemos usar las MISMAS dosis que se usaron al optimizar los parámetros
        if full_historial:
            # Usar historial completo con SUS dosis originales para simulación
            clinical_data_for_simulation = full_historial
            clinical_data_for_plotting = full_historial
            print(f"✓ Usando historial completo: {len(full_historial)} puntos")
            print(f"✓ Dosis desde historial (mismas que optimización)")
        else:
            # Si no hay historial, usar tabla
            clinical_data_for_simulation = clinical_data
            clinical_data_for_plotting = clinical_data
            print(f"⚠ Usando datos de tabla: {len(clinical_data)} puntos")
        
        # Datos clínicos para graficación (todos los puntos)
        clinical_months = [d[0] for d in clinical_data_for_plotting]
        # Manejar valores 'ND' correctamente
        clinical_bcr_percent = []
        for d in clinical_data_for_plotting:
            if isinstance(d[1], str) and d[1].upper() == 'ND':
                clinical_bcr_percent.append(DETECTION_LIMIT * 100)  # Usar límite de detección
            else:
                clinical_bcr_percent.append(d[1] * 100)
        
        # Usar la primera estrategia como principal
        main_strategy = strategies[0]
        
        # CORREGIDO: Pre-construir schedule completo de dosis desde t=0
        # IMPORTANTE: Usar dosis del HISTORIAL (mismas que optimización)
        last_clinical_month = clinical_months[-1]
        last_clinical_dose = clinical_data_for_simulation[-1][2]  # Dosis del historial
        
        # Determinar el fin de proyección basado en escenarios
        if scenarios_data:
            # Con escenarios: proyectar hasta el mes final del último escenario
            max_scenario_month = max([mes_fin for _, mes_fin, _ in scenarios_data])
            projection_end = max(max_scenario_month, int(last_clinical_month))
        else:
            # Sin escenarios: NO proyectar, solo graficar hasta último historial clínico
            projection_end = int(last_clinical_month)
        
        # Construir diccionario de dosis clínicas (step function)
        # Interpretación: La dosis en mes M se aplica DESDE el mes M hasta el siguiente cambio
        # Ejemplo: Mes 0=100%, Mes 3=50% → Meses 0,1,2 usan 100%, Mes 3+ usa 50%
        clinical_dose_dict = {}
        sorted_clinical = sorted(clinical_data_for_simulation, key=lambda x: x[0])
        
        for i in range(len(sorted_clinical)):
            t_current, val_current, dose_current = sorted_clinical[i]
            t_current_int = int(t_current)
            
            if i < len(sorted_clinical) - 1:
                # No es el último punto: aplicar esta dosis hasta el siguiente punto
                t_next = int(sorted_clinical[i+1][0])
                for month in range(t_current_int, t_next):
                    clinical_dose_dict[month] = dose_current
            else:
                # Último punto: aplicar esta dosis desde aquí en adelante
                for month in range(t_current_int, int(last_clinical_month) + 1):
                    clinical_dose_dict[month] = dose_current
        
        # Generar schedule de proyección según estrategia
        projection_dose_dict = {}
        if scenarios_data:
            # Con escenarios: aplicar desde mes 0 hasta projection_end
            # Los escenarios pueden sobreescribir incluso el período clínico
            for month in range(0, int(projection_end) + 1):
                assigned = False
                for mes_inicio, mes_fin, dosis_pct in scenarios_data:
                    if mes_inicio <= month <= mes_fin:
                        projection_dose_dict[month] = dosis_pct / 100.0
                        assigned = True
                        break
                if not assigned:
                    # Si no hay escenario para este mes, usar dosis clínica si existe
                    if month <= last_clinical_month:
                        # Usar dosis del historial clínico
                        projection_dose_dict[month] = clinical_dose_dict.get(month, last_clinical_dose)
                    else:
                        # Después del historial, mantener última dosis clínica
                        projection_dose_dict[month] = last_clinical_dose
        else:
            # Sin escenarios: usar solo datos clínicos (no proyectar)
            projection_dose_dict = {}
        
        # Usar projection_dose_dict si hay escenarios, sino usar clinical_dose_dict
        if scenarios_data:
            full_dose_dict = projection_dose_dict
        else:
            full_dose_dict = clinical_dose_dict
        
        # MENSAJE INFORMATIVO: Interpretación de dosis
        print("\n" + "="*70)
        print("📋 INFORMACIÓN IMPORTANTE: Interpretación de Dosis Clínicas")
        print("="*70)
        print("La dosis en cada punto de medición se aplica HASTA ese momento.")
        print("")
        print("✅ Ejemplo CORRECTO para cambio de dosis:")
        print("   Mes 0:  BCR-ABL=45%, Dosis=100%")
        print("   Mes 12: BCR-ABL=5%,  Dosis=100% ← Última medición con 100%")
        print("   Mes 23: BCR-ABL=2%,  Dosis=100% ← Aún con 100%")
        print("   Mes 24: BCR-ABL=1%,  Dosis=50%  ← Cambió a 50% después del mes 23")
        print("")
        print("⚠️  Si solo tienes 2 puntos con diferentes dosis, el sistema asume")
        print("   que la dosis cambió después del primer punto.")
        print("")
        print("📊 Escenarios de proyección:")
        if scenarios_data:
            print(f"   - Usando {len(scenarios_data)} escenarios definidos en la tabla")
            print(f"   - Proyección hasta mes {projection_end}")
            print(f"   - Gaps sin escenarios: mantienen última dosis ({last_clinical_dose*100:.0f}%)")
        else:
            print(f"   - Sin escenarios: NO hay proyección")
            print(f"   - Graficando solo hasta último dato clínico (mes {int(last_clinical_month)})")
        print("="*70 + "\n")
        
        # Convertir a lista de (tiempo, dosis) para simulate_model_with_variable_dosing
        time_dose_pairs = [(month, full_dose_dict[month]) for month in range(int(projection_end) + 1)]
        
        # USAR FUNCIÓN ROBUSTA DEL CORE
        solution, time_points = simulate_model_with_variable_dosing(params, time_dose_pairs)
        
        # Verificar simulación exitosa
        if np.any(np.isnan(solution)):
            return False, "Error: La simulación produjo valores inválidos"
        
        # Extraer resultados
        complete_months = list(time_points)
        complete_X = solution[:, 0]
        complete_Y = solution[:, 1]
        complete_Z = solution[:, 2]
        complete_doses = [full_dose_dict[int(m)] for m in complete_months]
        complete_bcr = [calculate_bcr_abl_ratio_decimal(y) * 100 for y in complete_Y]
        
        # Crear figura (importar bajo demanda)
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(14, 9))
        

        # ========== GRÁFICA 1: BCR-ABL logarítmico con zonas de dosis ========== 
        ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2)

        # Crear zonas sombreadas para diferentes dosis
        dose_intervals = []
        tolerance = 0.001
        current_dose = round(complete_doses[0], 3)
        start_idx = 0
        for i in range(1, len(complete_doses)):
            rounded_dose = round(complete_doses[i], 3)
            if abs(rounded_dose - current_dose) > tolerance:
                dose_intervals.append((complete_months[start_idx], complete_months[i], current_dose))
                current_dose = rounded_dose
                start_idx = i
        dose_intervals.append((complete_months[start_idx], complete_months[-1], current_dose))
        for idx, (start_time, end_time, dose_val) in enumerate(dose_intervals):
            shade = 0.9 - 0.2 * (idx % 4)
            ax1.axvspan(start_time, end_time, facecolor=(shade, shade, shade), alpha=0.25, edgecolor='none')
            xm = (start_time + end_time) / 2.0
            dose_percent = dose_val * 100
            if dose_percent % 1 < 0.1 or dose_percent % 1 > 0.9:
                label = f'Dose={dose_percent:.0f}%'
            else:
                label = f'Dose={dose_percent:.1f}%'
            ax1.text(xm, 0.95, label, ha='center', va='top', fontsize=9, 
                    fontweight='bold', transform=ax1.get_xaxis_transform())

        # (El panel informativo de paciente se elimina para dejar solo el panel general en ax3)

        # Graficar curva completa
        ax1.semilogy(complete_months, complete_bcr, color='blue', label='Simulación', linewidth=2)
        
        # Separar puntos ND de puntos medibles
        clinical_times_measured = []
        clinical_values_measured = []
        nd_times = []
        
        # USAR DATOS COMPLETOS PARA GRAFICAR (clinical_data_for_plotting)
        for i, (t, d) in enumerate(zip(clinical_months, clinical_data_for_plotting)):
            if isinstance(d[1], str) and d[1].upper() == 'ND':
                nd_times.append(t)
            else:
                clinical_times_measured.append(t)
                clinical_values_measured.append(clinical_bcr_percent[i])
        
        # Debug: Mostrar cuántos puntos se están graficando
        print(f"\n📊 Puntos clínicos a graficar en proyección:")
        print(f"   - Puntos medibles: {len(clinical_times_measured)} {clinical_times_measured}")
        print(f"   - Puntos ND: {len(nd_times)} {nd_times}")
        print(f"   - Total: {len(clinical_data_for_plotting)} puntos\n")
        
        # Graficar puntos medibles (círculos rojos)
        if clinical_times_measured:
            ax1.semilogy(clinical_times_measured, clinical_values_measured, 'ro', markersize=7, label='Datos clínicos', linewidth=2)
            
            # Anotar puntos medibles
            for tc, vc in zip(clinical_times_measured, clinical_values_measured):
                ax1.annotate(f'{vc:.2f}%', xy=(tc, vc), xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Graficar puntos ND (triángulos verdes)
        if nd_times:
            nd_values = [DETECTION_LIMIT * 100] * len(nd_times)
            ax1.semilogy(nd_times, nd_values, 'g^', markersize=8, label='ND (No Detectable)', linewidth=2)
            
            # Anotar puntos ND
            for tc in nd_times:
                ax1.annotate('ND', xy=(tc, DETECTION_LIMIT * 100), xytext=(5, 5), textcoords='offset points', fontsize=8, color='green')
        
        # Líneas de referencia
        ax1.axhline(DETECTION_LIMIT * 100, linestyle='--', color='gray', alpha=0.5, label=f'Detection ({DETECTION_LIMIT * 100:.3f}%)')
        ax1.axhline(0.1, linestyle='--', color='r', alpha=0.7, label='MR3 (0.1%)')
        ax1.axhline(0.01, linestyle='--', color='b', alpha=0.7, label='MR4 (0.01%)')
        
        low = max(min(complete_bcr) * 0.5, 0.01)
        high = max(max(complete_bcr) * 1.2, 100.0)
        ax1.set_ylim(low, high)
        
        ax1.set_xlabel('Tiempo (meses)', fontsize=11)
        ax1.set_ylabel('% Leucemia', fontsize=11)
        ax1.set_title('Proyección de % Leucemia', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=9, loc='best')
        
        # ========== GRÁFICA 2: Células (X, Y, Z) ==========
        ax2 = plt.subplot2grid((3, 2), (1, 0))
        ax2.semilogy(complete_months, complete_X, label='X (quiesc.)', linewidth=2)
        ax2.semilogy(complete_months, complete_Y, label='Y (prolif.)', linewidth=2)
        ax2.semilogy(complete_months, complete_Z, label='Z (inmunes)', linewidth=2)
        ax2.set_xlabel('Tiempo (meses)', fontsize=10)
        ax2.set_ylabel('Número células', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=9)
        
        # ========== PANEL RESUMIDO DE INTERPRETACIÓN GENERAL (tabla concreta) ========== 
        ax3 = plt.subplot2grid((3, 2), (1, 1))
        ax3.axis('off')
        # Datos clave para la tabla
        total_points = len(clinical_data_for_plotting)
        measurable_points = sum(1 for d in clinical_data_for_plotting if not (isinstance(d[1], str) and d[1].upper() == 'ND'))
        nd_points = total_points - measurable_points
        last_bcr = clinical_data_for_plotting[-1][1] if total_points > 0 else None
        last_month = clinical_data_for_plotting[-1][0] if total_points > 0 else None
        # Dosis reducción si hay escenarios
        dose_reduction = None
        if scenarios_data:
            total_dose_months = sum((end-start) * (dose/100) for start, end, dose in scenarios_data)
            full_dose_months = sum((end-start) for start, end, dose in scenarios_data)
            dose_reduction = (1 - total_dose_months/full_dose_months) * 100 if full_dose_months > 0 else 0
        # Tabla de resumen (sin sistema inmune, con indicación MR4)
        # Calcular si se alcanza TFR: dosis 0 y % leucemia bajo por >=12 meses consecutivos
        tfr_achieved = False
        min_months = 12
        threshold_mr3 = 0.1
        threshold_mr4 = 0.01
        consecutive = 0
        for dose, bcr in zip(complete_doses, complete_bcr):
            if dose == 0 and (bcr <= threshold_mr3 or bcr <= threshold_mr4):
                consecutive += 1
            else:
                consecutive = 0
            if consecutive >= min_months:
                tfr_achieved = True
                break
        tfr_text = "Sí" if tfr_achieved else "No"
        if tfr_achieved:
            tfr_reason = "Leucemia baja y sin TKI ≥12m"
        else:
            tfr_reason = "No: leucemia o TKI >12m"
        table_data = [
            ["Paciente", str(patient_name)],
            ["Puntos clínicos", f"{total_points} ({measurable_points} medibles, {nd_points} ND)"],
            ["Último mes", f"{last_month}" if last_month is not None else "-"],
            ["Último % Leucemia", f"{last_bcr:.3%}" if last_bcr is not None and not (isinstance(last_bcr, str) and last_bcr.upper() == 'ND') else "ND"],
        ]
        table_data.append(["Meta clínica", "MR3, MR4 (>12m)"])
        table_data.append(["Remisión", "% leucemia bajo >12m"])
        table_data.append(["X/Y/Z", "X: reserva, Y: actividad, Z: defensa"])
        table_data.append(["TFR alcanzado", tfr_text])
        table_data.append(["Motivo TFR", tfr_reason])
        # Mostrar tabla
        ax3.table(cellText=table_data, colLabels=["Dato", "Valor"], loc='center', cellLoc='left', colLoc='left', bbox=[0, 0, 1, 1])
        tabla = ax3.table(cellText=table_data, colLabels=["Dato", "Valor"], loc='center', cellLoc='left', colLoc='left', bbox=[0, 0, 1, 1])
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(10)
        # Colorear encabezado 'Dato' de gris oscuro
        for (row, col), cell in tabla.get_celld().items():
            if row == 0:
                cell.set_facecolor('#444444')
                cell.set_text_props(color='white', weight='bold')
        tabla.scale(1.1, 1.8)
        ax3.set_title("INTERPRETACIÓN GENERAL DE LA PROYECCIÓN", fontsize=14, fontweight='bold', pad=22)
        
        # ========== GRÁFICA 4: log10(Ratio) ==========
        ax4 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
        log_ratio = np.log10(np.maximum(complete_bcr, 1e-12))
        ax4.plot(complete_months, log_ratio, label='log10(Ratio %)', linewidth=2, color='blue')
        ax4.axhline(np.log10(0.1), linestyle='--', color='r', alpha=0.7, label='MR3')
        ax4.axhline(np.log10(0.01), linestyle='--', color='b', alpha=0.7, label='MR4')
        ax4.set_xlabel('Tiempo (meses)', fontsize=10)
        ax4.set_ylabel('log10(Ratio %)', fontsize=10)
        ax4.grid(True, alpha=0.3)
        ax4.legend(fontsize=9)
        
        plt.tight_layout()
        plt.show()
        return True, "Gráfica mostrada exitosamente"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"Error al generar gráfica: {str(e)}"


def plot_multiple_scenarios(patient_name, clinical_data, scenario_names=None):
    """
    Compara múltiples escenarios en una sola figura
    scenario_names: lista de nombres de estrategias a comparar
    """
    if scenario_names is None:
        scenario_names = ['tapering', 'continuous']
    
    params, error = load_patient_parameters(patient_name)
    if not params:
        return False, "No se encontraron parámetros optimizados"
    
    try:
        import matplotlib.pyplot as plt  # Importar bajo demanda
        
        clinical_months = [d[0] for d in clinical_data]
        clinical_bcr_percent = [d[1] * 100 for d in clinical_data]
        
        fig, axes = plt.subplots(1, len(scenario_names), figsize=(15, 5))
        if len(scenario_names) == 1:
            axes = [axes]
        
        for idx, scenario in enumerate(scenario_names):
            proj_time, proj_data = project_model_with_strategy(params, clinical_data, scenario)
            
            if proj_data:
                proj_months = [d['month'] for d in proj_data]
                proj_bcr = [d['bcr_abl'] * 100 for d in proj_data]
                
                ax = axes[idx]
                ax.semilogy(proj_months, proj_bcr, label=scenario, linewidth=2, color='blue')
                ax.semilogy(clinical_months, clinical_bcr_percent, 'ro', markersize=7, label='Datos clínicos')
                ax.axhline(0.1, linestyle='--', color='r', alpha=0.5, label='MR3')
                ax.axhline(0.01, linestyle='--', color='b', alpha=0.5, label='MR4')
                
                ax.set_xlabel('Tiempo (meses)', fontsize=10)
                ax.set_ylabel('% Leucemia', fontsize=10)
                ax.set_title(f'Escenario: {scenario}', fontsize=11, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(fontsize=8)
        
        plt.tight_layout()
        plt.show()
        return True, "Escenarios mostrados"
        
    except Exception as e:
        return False, f"Error: {str(e)}"
