
import json
import math
import random
import numpy as np
from scipy.integrate import odeint
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMessageBox

# matplotlib se importa bajo demanda en funciones que lo necesitan

# ========== CONSTANTES DEL MODELO CML ==========
DETECTION_LIMIT = 0.0001  # Límite de detección BCR-ABL (0.01% en escala decimal)
K_Y = 1e6                  # Capacidad de carga del compartimiento Y (células leucémicas)
M = 1e-4                   # Tasa de muerte inducida por células inmunes
R_Z = 200                  # Tasa de renovación basal de células inmunes
A_Z = 2.0                  # Tasa de apoptosis de células inmunes

# Límites de búsqueda para cada parámetro a optimizar
GENE_BOUNDS = {
    'initLRATIO': (-2.0, 0.0),      # Ratio inicial logarítmico BCR-ABL
    'TKI_effect': (0.5, 3.0),       # Efectividad del tratamiento TKI
    'p_XY': (1e-10, 1.0),           # Tasa de diferenciación X → Y
    'p_YX': (1e-10, 1.0),           # Tasa de des-diferenciación Y → X
    'p_Y': (0.05, 10.0),            # Tasa de proliferación de células Y
    'K_Z': (10.0, 10**3.5),         # Constante de semi-saturación inmune
    'p_Z': (20.0, 12649111.0)       # Tasa de estimulación inmune por células Y
}


# ========== MODELO MATEMÁTICO CML ==========

def cml_model(y, t, params, dose_factor=1.0):
    """
    Sistema de ecuaciones diferenciales del modelo CML de 3 compartimientos.
    
    Compartimientos:
    - X: Células madre leucémicas (stem cells)
    - Y: Células leucémicas diferenciadas
    - Z: Células inmunes efectoras
    
    Parámetros:
        y: Vector [X, Y, Z] con el estado actual del sistema
        t: Tiempo en meses
        params: Diccionario con los 7 parámetros del modelo
        dose_factor: Factor de dosis del TKI (1.0=100%, 0.5=50%, 0.0=sin tratamiento)
    
    Retorna:
        [dX/dt, dY/dt, dZ/dt]: Derivadas del sistema
    """
    X, Y, Z = y
    
    # Validar que los valores sean físicamente posibles (no negativos)
    X = max(X, 0.0)
    Y = max(Y, 0.0)
    Z = max(Z, 0.0)
    
    # Extraer parámetros del modelo
    p_XY = params['p_XY']           # Tasa de diferenciación X → Y
    p_YX = params['p_YX']           # Tasa de des-diferenciación Y → X
    p_Y = params['p_Y']             # Tasa de proliferación de Y
    TKI_effect = params['TKI_effect']  # Efectividad del inhibidor TKI
    K_Z = params['K_Z']             # Semi-saturación de respuesta inmune
    p_Z = params['p_Z']             # Estimulación inmune

    # Ecuación para X: flujo entre compartimientos
    dX_dt = p_YX * Y - p_XY * X
    
    # Ecuación para Y: incluye proliferación, muerte inmune y efecto del TKI
    proliferation = p_Y * Y * (1 - Y / K_Y) if Y < K_Y * 10 else 0.0
    dY_dt = (p_XY * X - p_YX * Y + proliferation - M * Z * Y - dose_factor * TKI_effect * Y)
    
    # Ecuación para Z: respuesta inmune con saturación tipo Hill
    dZ_dt = (R_Z + p_Z * Z * Y / (K_Z**2 + Y**2) - A_Z * Z)
    
    return [dX_dt, dY_dt, dZ_dt]


def get_initial_conditions(params):
    """
    Calcula las condiciones iniciales [X0, Y0, Z0] basadas en el initLRATIO.
    
    El initLRATIO determina el porcentaje BCR-ABL inicial del paciente.
    A partir de este valor se calculan las poblaciones iniciales de cada compartimiento.
    
    Parámetros:
        params: Diccionario que debe contener 'initLRATIO', 'p_XY' y 'p_YX'
    
    Retorna:
        array([X0, Y0, Z0]): Condiciones iniciales del sistema
    """
    initLRATIO = params['initLRATIO']
    
    # Convertir de escala logarítmica a decimal
    R = 10.0 ** initLRATIO
    R = np.clip(R, 1e-12, 0.999999)
    
    # Calcular Y0 a partir del ratio BCR-ABL inicial
    Y0 = (2.0 * R * K_Y) / (1.0 + R)
    Y0 = min(Y0, K_Y * 0.99)
    
    # Calcular X0 asumiendo equilibrio entre transiciones X ↔ Y
    p_XY = max(params['p_XY'], 1e-12)
    p_YX = max(params['p_YX'], 1e-12)
    X0 = (p_YX / p_XY) * Y0
    
    # Z0 en estado estacionario basal (sin tumor)
    Z0 = R_Z / A_Z
    
    # Asegurar valores mínimos positivos
    X0 = max(X0, 1.0)
    Y0 = max(Y0, 1.0)
    Z0 = max(Z0, 1.0)
    
    return np.array([X0, Y0, Z0])


def simulate_model_with_variable_dosing(params, time_dose_pairs):
    """
    Simula el modelo CML con un calendario de dosis variable en el tiempo.
    
    Permite modelar escenarios como: dosis completa → reducción → cesación.
    
    Parámetros:
        params: Diccionario con los parámetros del modelo
        time_dose_pairs: Lista de tuplas (tiempo_meses, fraccion_dosis)
                         Ejemplo: [(0, 1.0), (12, 0.5), (24, 0.0)]
    
    Retorna:
        solution: Array de shape (n_tiempos, 3) con valores de [X, Y, Z]
        time_points: Lista de tiempos donde se evaluó la solución
    """
    # Ordenar por tiempo
    time_dose_pairs = sorted(time_dose_pairs, key=lambda x: x[0])
    time_points = [t for (t, d) in time_dose_pairs]

    # Función auxiliar que aplica la dosis correspondiente a cada tiempo
    def model_with_variable_dosing(y, t):
        current_dose = 1.0
        # Encontrar la dosis vigente en el tiempo t
        for tv, dv in time_dose_pairs:
            if tv <= t:
                current_dose = dv
            else:
                break
        return cml_model(y, t, params, current_dose)

    # Obtener condiciones iniciales
    y0 = get_initial_conditions(params)
    
    # Integrar el sistema de ecuaciones diferenciales
    try:
        sol = odeint(model_with_variable_dosing, y0, time_points, 
                     rtol=1e-6, atol=1e-8, mxstep=10000)
        return sol, time_points
    except Exception as e:
        print(f"Error en simulación: {e}")
        return np.full((len(time_points), 3), np.nan), time_points


def calculate_lratio(Y):
    """
    Calcula el logaritmo (base 10) del ratio BCR-ABL a partir de Y.
    
    Fórmula: ratio = Y / (Y + 2*(K_Y - Y))
             lratio = log10(ratio)
    
    Esta es la medida clínica estándar usada para evaluar la respuesta molecular.
    
    Parámetros:
        Y: Número de células leucémicas diferenciadas
    
    Retorna:
        lratio: log10 del ratio BCR-ABL (valor negativo, ej: -2.0 = 1%, -4.0 = 0.01%)
    """
    eps = 1e-12
    denom = Y + 2.0 * (K_Y - Y)
    
    if denom <= 0:
        ratio_decimal = eps
    else:
        ratio_decimal = Y / denom
    
    ratio_decimal = np.clip(ratio_decimal, eps, 1.0)
    return np.log10(ratio_decimal)


def calculate_bcr_abl_ratio_decimal(Y):
    """
    Calcula el ratio BCR-ABL en escala decimal (0 a 1) a partir de Y.
    
    Parámetros:
        Y: Número de células leucémicas diferenciadas
    
    Retorna:
        ratio: Ratio BCR-ABL en escala decimal (ej: 0.01 = 1%, 0.0001 = 0.01%)
    """
    denom = Y + 2.0 * (K_Y - Y)
    if denom <= 0:
        return 1e-12
    return max(Y / denom, 1e-12)


# ========== FUNCIONES DE FITNESS (EVALUACIÓN DE CALIDAD) ==========

def fitness_function_with_dosing(params, clinical_data_with_dosing, detection_limit=DETECTION_LIMIT):
    """
    Calcula el fitness (calidad del ajuste) de un conjunto de parámetros.
    
    Compara la simulación del modelo con los datos clínicos reales del paciente.
    Fitness más alto (menos negativo) = mejor ajuste.
    
    Parámetros:
        params: Diccionario con los 7 parámetros del modelo
        clinical_data_with_dosing: Lista de tuplas (tiempo, valor_BCR_ABL, dosis)
        detection_limit: Límite bajo el cual BCR-ABL se considera "No Detectable"
    
    Retorna:
        fitness: Valor negativo (más cercano a 0 = mejor ajuste)
    """
    # Preparar datos para la simulación
    time_dose_pairs = [(t, dose) for (t, val, dose) in clinical_data_with_dosing]
    solution, time_points_sim = simulate_model_with_variable_dosing(params, time_dose_pairs)
    
    # Verificar que la simulación sea válida
    if np.any(np.isnan(solution)):
        return -1e12
    
    # Extraer valores de Y y calcular lratio para cada punto
    Y_sim = solution[:, 1]
    lratio_simulated_dict = {t: calculate_lratio(y) for t, y in zip(time_points_sim, Y_sim)}
    
    total_error = 0.0
    measured_points = 0
    
    # Comparar simulación con cada punto clínico
    for t, clinical_val, dose in clinical_data_with_dosing:
        if t not in lratio_simulated_dict:
            continue
        lratio_sim = lratio_simulated_dict[t]
        
        # Caso 1: Punto "No Detectable" (ND)
        if isinstance(clinical_val, str) and clinical_val.upper() == 'ND':
            target_lratio = np.log10(max(detection_limit, 1e-12))
            if lratio_sim > target_lratio:
                # Penalizar: la simulación predice valor detectable cuando debería ser ND
                total_error += (lratio_sim - target_lratio) ** 2 * 2.0
        else:
            # Caso 2: Punto con valor medible
            try:
                clinical_float = float(clinical_val)
                clinical_lratio = np.log10(max(clinical_float, 1e-12))
                
                # Asignar peso según la dosis (fase de tratamiento)
                if dose == 1.0:
                    weight = 2.0  # Dosis completa: peso mayor
                elif dose == 0.5:
                    weight = 1.5  # Media dosis
                else:
                    weight = 1.0  # Otras dosis
                
                total_error += (lratio_sim - clinical_lratio) ** 2 * weight
                measured_points += 1
            except Exception:
                continue
    
    # Si no hay puntos válidos, fitness muy malo
    if measured_points == 0:
        return -1e12
    
    # Retornar error promedio negativo (minimizamos error)
    return -(total_error / measured_points)


def calculate_fitness(params, clinical_data_with_dosing, detection_limit=DETECTION_LIMIT):
    """
    Función principal de fitness con normalización por pesos y penalizaciones adaptativas.
    
    Esta es la función más completa que usa el algoritmo genético.
    Mejoras sobre fitness_function_with_dosing:
    - Penalización 3x para puntos ND que están sobre el límite (error crítico)
    - Normalización correcta por suma de pesos (no solo conteo de puntos)
    - Pesos adaptativos según fase de tratamiento
    - Peso mayor (2.5x) en fase post-cesación (dosis=0)
    - Validaciones físicas del modelo
    
    Parámetros:
        params: Diccionario con los parámetros del modelo
        clinical_data_with_dosing: Lista de tuplas (tiempo, valor_BCR_ABL, dosis)
        detection_limit: Límite de detección del BCR-ABL
    
    Retorna:
        fitness: Valor negativo normalizado (más cercano a 0 = mejor)
    """
    try:
        time_dose_pairs = [(t, dose) for (t, val, dose) in clinical_data_with_dosing]
        solution, time_points_sim = simulate_model_with_variable_dosing(params, time_dose_pairs)
        
        # Verificar solución válida
        if np.any(np.isnan(solution)) or np.any(np.isinf(solution)):
            return -1e12
        
        Y_sim = solution[:, 1]
        
        # Verificar valores físicamente válidos
        if np.any(Y_sim < 0) or np.any(Y_sim > K_Y * 100):
            return -1e12
            
        lratio_simulated_dict = {t: calculate_lratio(y) for t, y in zip(time_points_sim, Y_sim)}
        
        total_error = 0.0
        measured_points = 0
        weights_sum = 0.0
        
        for t, clinical_val, dose in clinical_data_with_dosing:
            if t not in lratio_simulated_dict:
                continue
                
            lratio_sim = lratio_simulated_dict[t]
            
            # Verificar que lratio_sim es válido
            if np.isnan(lratio_sim) or np.isinf(lratio_sim):
                continue
            
            # Peso base según fase de tratamiento
            if dose == 1.0:  # Dosis completa
                base_weight = 2.0
            elif dose == 0.5:  # Reducción 50%
                base_weight = 1.5
            elif dose == 0.25:  # Reducción 25%
                base_weight = 1.3
            elif dose == 0.0:  # Post-cesación
                base_weight = 2.5  # Mayor peso después de parar
            else:
                base_weight = 1.0
                
            # Procesar punto ND (No Detectable)
            if isinstance(clinical_val, str) and clinical_val.upper() == 'ND':
                target_lratio = np.log10(max(detection_limit, 1e-12))
                
                # Si la simulación está SOBRE el límite de detección, es un ERROR
                if lratio_sim > target_lratio:
                    error = (lratio_sim - target_lratio) ** 2
                    # PENALIZAR MÁS (no menos) - multiplicador 3.0
                    penalty_weight = base_weight * 3.0
                    total_error += error * penalty_weight
                    weights_sum += penalty_weight
                    measured_points += 1
                else:
                    # Simulación correcta (bajo límite), pequeña recompensa
                    # Aún contamos el punto para normalización
                    bonus_weight = base_weight * 0.1
                    weights_sum += bonus_weight
                    measured_points += 1
                    
            # Procesar punto con valor medible
            else:
                try:
                    clinical_float = float(clinical_val)
                    
                    # Validar valor clínico
                    if clinical_float <= 0 or clinical_float > 100:
                        continue
                        
                    clinical_lratio = np.log10(max(clinical_float, 1e-12))
                    
                    # Error cuadrático ponderado
                    error = (lratio_sim - clinical_lratio) ** 2
                    
                    # Peso adicional para valores muy bajos (remisión profunda)
                    if clinical_float < 0.01:  # MR4 o mejor
                        final_weight = base_weight * 1.5
                    else:
                        final_weight = base_weight
                    
                    total_error += error * final_weight
                    weights_sum += final_weight
                    measured_points += 1
                    
                except (ValueError, TypeError):
                    continue
        
        # Sin puntos válidos = fitness pésimo
        if measured_points == 0 or weights_sum == 0:
            return -1e12
        
        # Normalizar por suma de pesos (no solo por número de puntos)
        normalized_error = total_error / weights_sum
        
        # Penalización adicional si hay muy pocos puntos ajustados
        if measured_points < 3:
            normalized_error *= (5.0 / measured_points)
        
        return -normalized_error
        
    except Exception as e:
        print(f"Error en fitness function: {e}")
        return -1e12


def calculate_fitness_simple(params, clinical_data_with_dosing, detection_limit=DETECTION_LIMIT):
    """
    Versión alternativa simplificada de la función de fitness.
    
    Usa un esquema de pesos más simple:
    - Peso 2x para puntos en post-cesación (dosis=0)
    - Peso 1x para el resto
    - Penalización 2x para puntos ND sobre el límite
    
    Útil como función de respaldo o para comparaciones.
    """
    try:
        time_dose_pairs = [(t, dose) for (t, val, dose) in clinical_data_with_dosing]
        solution, time_points_sim = simulate_model_with_variable_dosing(params, time_dose_pairs)
        
        if np.any(np.isnan(solution)) or np.any(np.isinf(solution)):
            return -1e12
        
        Y_sim = solution[:, 1]
        
        # Verificar valores físicamente válidos
        if np.any(Y_sim < 0) or np.any(Y_sim > K_Y * 100):
            return -1e12
            
        lratio_simulated_dict = {t: calculate_lratio(y) for t, y in zip(time_points_sim, Y_sim)}
        
        errors = []
        
        for t, clinical_val, dose in clinical_data_with_dosing:
            if t not in lratio_simulated_dict:
                continue
            
            lratio_sim = lratio_simulated_dict[t]
            
            # Verificar valor válido
            if np.isnan(lratio_sim) or np.isinf(lratio_sim):
                continue
            
            # Peso simple: post-cesación pesa el doble
            weight = 2.0 if dose == 0.0 else 1.0
            
            if isinstance(clinical_val, str) and clinical_val.upper() == 'ND':
                target_lratio = np.log10(detection_limit)
                if lratio_sim > target_lratio:
                    # Penalizar proporcionalmente a qué tan lejos está
                    error = (lratio_sim - target_lratio) ** 2 * weight * 2.0
                    errors.append(error)
                # Si está bajo el límite, no agregamos error (es bueno)
            else:
                try:
                    clinical_float = float(clinical_val)
                    if clinical_float <= 0 or clinical_float > 100:
                        continue
                    clinical_lratio = np.log10(max(clinical_float, 1e-12))
                    error = (lratio_sim - clinical_lratio) ** 2 * weight
                    errors.append(error)
                except (ValueError, TypeError):
                    continue
        
        if len(errors) == 0:
            return -1e12
        
        # MSE simple
        return -np.mean(errors)
        
    except Exception as e:
        return -1e12


# ========== ALGORITMO GENÉTICO ==========

def create_initial_population(size):
    """
    Crea la población inicial de individuos con parámetros aleatorios.
    
    Cada individuo es un diccionario con los 7 parámetros del modelo.
    Los valores se generan aleatoriamente dentro de los rangos permitidos (GENE_BOUNDS).
    
    Parámetros:
        size: Número de individuos en la población
    
    Retorna:
        population: Lista de diccionarios, cada uno representa un individuo
    """
    population = []
    for _ in range(size):
        individual = {}
        for gene, (lower, upper) in GENE_BOUNDS.items():
            # Parámetros en escala logarítmica
            if gene in ['p_XY', 'p_YX', 'K_Z', 'p_Z']:
                individual[gene] = 10 ** random.uniform(np.log10(lower), np.log10(upper))
            # initLRATIO: rango completo [-2.0, 0.0]
            elif gene == 'initLRATIO':
                individual[gene] = random.uniform(-2.0, 0.0)
            # TKI_effect: rango común [0.8, 2.5]
            elif gene == 'TKI_effect':
                individual[gene] = random.uniform(0.8, 2.5)
            # p_Y: rango común [0.5, 5.0]
            elif gene == 'p_Y':
                individual[gene] = random.uniform(0.5, 5.0)
            else:
                individual[gene] = random.uniform(lower, upper)
        population.append(individual)
    return population


def selection(population, fitnesses, tournament_size=3):
    """
    Selección por comparación: elige los mejores individuos para reproducirse.
    
    En cada comparación se seleccionan aleatoriamente 'tournament_size' individuos
    y se escoge el mejor (mayor fitness) como padre.
    
    Parámetros:
        population: Lista de individuos (diccionarios de parámetros)
        fitnesses: Lista de fitness correspondiente a cada individuo
        tournament_size: Número de competidores por torneo
    
    Retorna:
        selected: Nueva población de padres seleccionados
    """
    selected = []
    for _ in range(len(population)):
        # Seleccionar competidores aleatorios
        contestants = random.sample(range(len(population)), tournament_size)
        # Elegir el ganador (mejor fitness)
        winner = max(contestants, key=lambda i: fitnesses[i])
        selected.append(population[winner].copy())
    return selected


def crossover(parent1, parent2):
    """
    Cruzamiento (reproducción) de dos padres para crear dos hijos.
    
    Combina los genes de ambos padres usando interpolación:
    - Parámetros logarítmicos: cruce en escala log
    - Otros parámetros: cruce lineal
    
    Parámetros:
        parent1, parent2: Diccionarios con parámetros de los padres
    
    Retorna:
        child1, child2: Dos nuevos individuos (hijos)
    """
    child1, child2 = {}, {}
    for gene in parent1.keys():
        # Genes en escala logarítmica
        if gene in ['p_XY', 'p_YX', 'K_Z', 'p_Z']:
            l1, l2 = np.log10(parent1[gene]), np.log10(parent2[gene])
            alpha = random.uniform(0.1, 0.9)
            c1_log = alpha * l1 + (1 - alpha) * l2
            c2_log = alpha * l2 + (1 - alpha) * l1
            lower, upper = GENE_BOUNDS[gene]
            c1 = 10 ** np.clip(c1_log, np.log10(lower), np.log10(upper))
            c2 = 10 ** np.clip(c2_log, np.log10(lower), np.log10(upper))
        # Genes en escala lineal
        else:
            alpha = random.uniform(0.3, 0.7)
            c1 = alpha * parent1[gene] + (1 - alpha) * parent2[gene]
            c2 = alpha * parent2[gene] + (1 - alpha) * parent1[gene]
            lower, upper = GENE_BOUNDS[gene]
            c1 = np.clip(c1, lower, upper)
            c2 = np.clip(c2, lower, upper)
        child1[gene], child2[gene] = c1, c2
    return child1, child2


def mutate(individual, mutation_rate=0.25):
    """
    Mutación: introduce variabilidad aleatoria en un individuo.
    
    Cada gen tiene 'mutation_rate' probabilidad de mutar.
    La mutación añade ruido gaussiano al valor del gen.
    
    Parámetros:
        individual: Diccionario con parámetros
        mutation_rate: Probabilidad de mutación por gen (0.25 = 25%)
    
    Retorna:
        mutated: Nuevo individuo con mutaciones aplicadas
    """
    mutated = individual.copy()
    for gene, (lower, upper) in GENE_BOUNDS.items():
        if random.random() < mutation_rate:
            # Parámetros logarítmicos: mutar en escala log
            if gene in ['p_XY', 'p_YX', 'K_Z', 'p_Z']:
                current_log = np.log10(mutated[gene])
                new_log = current_log + random.gauss(0, 0.2)
                mutated[gene] = 10 ** np.clip(new_log, np.log10(lower), np.log10(upper))
            # initLRATIO: mutación más pequeña (parámetro sensible)
            elif gene == 'initLRATIO':
                mutation_size = 0.15  # Desviación reducida para estabilidad
                mutated[gene] += random.gauss(0, mutation_size)
                mutated[gene] = np.clip(mutated[gene], lower, upper)
            # TKI_effect: mutación 5% del rango
            elif gene == 'TKI_effect':
                mutation_size = (upper - lower) * 0.05
                mutated[gene] += random.gauss(0, mutation_size)
                mutated[gene] = np.clip(mutated[gene], lower, upper)
            # Otros parámetros: mutación 10% del rango
            else:
                mutation_size = (upper - lower) * 0.1
                mutated[gene] += random.gauss(0, mutation_size)
                mutated[gene] = np.clip(mutated[gene], lower, upper)
    return mutated


def genetic_algorithm(clinical_data, population_size=60, generations=80, progress_callback=None, stop_check=None):
    """
    Algoritmo genético principal para optimizar los parámetros del modelo CML.
    
    Proceso iterativo:
    1. Crear población inicial aleatoria
    2. Evaluar fitness de cada individuo
    3. Seleccionar los mejores (selección por torneo)
    4. Cruzar padres para crear hijos
    5. Mutar hijos para introducir variabilidad
    6. Mantener elitismo (conservar el mejor individuo)
    7. Repetir por 'generations' iteraciones
    
    Parámetros:
        clinical_data: Datos clínicos [(tiempo, BCR_ABL, dosis), ...]
        population_size: Tamaño de la población (60 por defecto)
        generations: Número de generaciones (80 por defecto)
        progress_callback: Función para reportar progreso (opcional)
        stop_check: Función que retorna False si se debe detener (opcional)
    
    Retorna:
        best_individual: Mejor conjunto de parámetros encontrado
        best_history: Historial de mejor individuo por generación
    """
    population = create_initial_population(population_size)
    best_history = []

    for gen in range(generations):
        # Verificar si se debe detener
        if stop_check and not stop_check():
            break
            
        # Evaluar fitness de todos los individuos usando la función principal
        fitnesses = [calculate_fitness(ind, clinical_data) for ind in population]
        
        # Encontrar el mejor individuo de esta generación
        best_idx = int(np.argmax(fitnesses))
        best_individual = population[best_idx]
        best_fitness = fitnesses[best_idx]
        best_history.append((best_individual.copy(), best_fitness))

        # Reportar progreso si se proporcionó callback
        if progress_callback:
            progress_callback(gen, generations, best_individual, best_fitness)

        # Selección: elegir padres por torneo
        selected = selection(population, fitnesses)
        
        # Reproducción: crear nueva generación
        new_population = []
        for i in range(0, len(selected), 2):
            p1 = selected[i]
            p2 = selected[i+1] if i+1 < len(selected) else selected[0]
            c1, c2 = crossover(p1, p2)
            new_population.extend([mutate(c1), mutate(c2)])

        # Elitismo: conservar los mejores individuos
        if len(new_population) >= 2:
            new_population[0] = best_individual  # Mejor actual
            if len(best_history) > 1:
                new_population[1] = best_history[-2][0]  # Mejor previo

        population = new_population

    return best_history[-1][0], best_history


# ========== THREAD DE OPTIMIZACIÓN (EJECUCIÓN EN SEGUNDO PLANO) ==========

class OptimizationThread(QThread):
    """
    Thread para ejecutar la optimización genética en segundo plano.
    
    Permite que la interfaz gráfica siga respondiendo mientras se ejecuta
    el algoritmo genético, que puede tomar varios minutos.
    
    Características:
    - Múltiples restarts para mejorar resultados
    - Reporta progreso en tiempo real
    - Puede ser detenido por el usuario
    - Retorna el mejor resultado de todos los restarts
    
    Señales:
        progress: Emite porcentaje de avance (0-100)
        status_update: Emite mensajes de estado
        finished: Emite mejor solución, fitness e historial
        error: Emite mensaje de error si algo falla
    """
    progress = Signal(int)         # Progreso (0-100)
    status_update = Signal(str)    # Mensajes de estado
    finished = Signal(dict, float, list)  # (mejor_solución, fitness, historial)
    error = Signal(str)            # Mensajes de error

    def __init__(self, clinical_data, patient_name, restarts=3, pop_size=60, generations=80):
        """
        Inicializa el thread de optimización.
        
        Parámetros:
            clinical_data: Datos clínicos [(tiempo, BCR_ABL, dosis), ...]
            patient_name: Nombre del paciente
            restarts: Número de ejecuciones independientes del GA (3 por defecto)
            pop_size: Tamaño de la población (60 por defecto)
            generations: Generaciones por restart (80 por defecto)
        """
        super().__init__()
        self.clinical_data = clinical_data
        self.patient_name = patient_name
        self.restarts = restarts
        self.pop_size = pop_size
        self.generations = generations
        self.is_running = True
        self.results = []
        self.best_solution = None
        self.best_fitness = None
        self.best_history = None

    def run(self):
        """
        Ejecuta la optimización genética con múltiples restarts.
        
        Estrategia multi-restart:
        - Ejecuta el GA 'restarts' veces independientemente
        - Cada restart puede encontrar un óptimo diferente
        - Al final se selecciona el mejor resultado de todos
        - Mejora robustez y evita mínimos locales
        """
        try:
            total_steps = self.restarts * self.generations
            steps_done = 0

            for r in range(self.restarts):
                if not self.is_running:
                    break

                # Callback para reportar progreso de cada generación
                def progress_cb(gen, gens_total, best_ind, best_fit):
                    nonlocal steps_done
                    steps_done += 1
                    progress_val = int((steps_done / total_steps) * 100)
                    self.progress.emit(progress_val)
                    
                    # Reportar cada 10% de las generaciones
                    if gen % max(1, gens_total // 10) == 0 or gen == gens_total - 1:
                        error = -best_fit if best_fit is not None else 0
                        msg = f"Restart {r+1}/{self.restarts} Gen {gen+1}/{gens_total} Fitness={best_fit:.3e} Error={error:.3e}"
                        self.status_update.emit(msg)

                # Ejecutar GA
                best, history = genetic_algorithm(
                    self.clinical_data,
                    population_size=self.pop_size,
                    generations=self.generations,
                    progress_callback=progress_cb,
                    stop_check=lambda: self.is_running
                )
                
                # Solo agregar resultados si no se canceló
                if self.is_running:
                    # Calcular fitness final
                    fit = calculate_fitness(best, self.clinical_data)
                    self.results.append((best, history, fit))

            # Solo emitir resultados si no fue cancelado
            if self.is_running and self.results:
                # Ordenar resultados por fitness (mejor primero)
                self.results = sorted(self.results, key=lambda x: x[2], reverse=True)
                self.best_solution, self.best_history, self.best_fitness = self.results[0]
                
                self.progress.emit(100)
                self.finished.emit(self.best_solution, self.best_fitness, self.best_history)
            elif not self.is_running:
                # No hacer nada si fue cancelado
                pass
            else:
                self.error.emit("No se encontró solución")

        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

    def stop(self):
        """Cancela la optimización de forma segura."""
        self.is_running = False


# ========== VISUALIZACIÓN DE RESULTADOS ==========

def plot_optimization_results(best_solution, clinical_data):
    """
    Genera gráficas de los resultados de la optimización.
    
    Crea 4 subplots:
    1. BCR-ABL vs Tiempo (escala logarítmica)
    2. BCR-ABL vs Tiempo (escala lineal)
    3. Dinámica de células inmunes (Z)
    4. Parámetros optimizados (tabla de texto)
    
    Parámetros:
        best_solution: Diccionario con los mejores parámetros encontrados
        clinical_data: Datos clínicos [(tiempo, BCR_ABL, dosis), ...]
    """
    import matplotlib.pyplot as plt  # Importar bajo demanda
    
    time_dose_pairs = sorted([(t, dose) for (t, val, dose) in clinical_data], key=lambda x: x[0])
    t_min = time_dose_pairs[0][0]
    t_max = time_dose_pairs[-1][0]
    time_dense = np.linspace(t_min, t_max, 1000)

    def model_with_variable_dosing(y, t):
        current_dose = 1.0
        for tv, dv in time_dose_pairs:
            if tv <= t:
                current_dose = dv
            else:
                break
        return cml_model(y, t, best_solution, dose_factor=current_dose)

    y0 = get_initial_conditions(best_solution)
    sol_dense = odeint(model_with_variable_dosing, y0, time_dense, rtol=1e-6, atol=1e-8, mxstep=10000)
    Ys = sol_dense[:, 1]
    Zs = sol_dense[:, 2]
    bcr_abl_sim_dense = [100 * calculate_bcr_abl_ratio_decimal(y) for y in Ys]

    clinical_times = []
    clinical_values = []
    nd_times = []
    
    for t, val, dose in clinical_data:
        if isinstance(val, str) and val.upper() == 'ND':
            nd_times.append(t)
        else:
            clinical_times.append(t)
            clinical_values.append(100 * float(val))
    
    # Debug: Mostrar cuántos puntos se están graficando
    print(f"\n📊 Puntos clínicos a graficar:")
    print(f"   - Puntos medibles: {len(clinical_times)} {clinical_times}")
    print(f"   - Puntos ND: {len(nd_times)} {nd_times}")
    print(f"   - Total: {len(clinical_data)} puntos\n")

    # Crear 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Gráfica 1: BCR-ABL en el Tiempo
    ax1 = axes[0, 0]
    ax1.semilogy(time_dense, bcr_abl_sim_dense, label='Simulación', linewidth=2, color='#2E7D32')
    if clinical_times:
        ax1.semilogy(clinical_times, clinical_values, 'ro', label='Datos clínicos', markersize=8)
    detection_limit_percent = 100 * DETECTION_LIMIT
    if nd_times:
        ax1.semilogy(nd_times, [detection_limit_percent] * len(nd_times), 'g^', label='ND', markersize=8)
    ax1.axhline(y=detection_limit_percent, linestyle='--', color='gray', alpha=0.5, label=f'Límite ({detection_limit_percent:.3f}%)')
    ax1.set_xlabel('Tiempo (meses)', fontsize=11)
    ax1.set_ylabel('BCR-ABL (%)', fontsize=11)
    ax1.set_ylim(1e-2, 1e2)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('BCR-ABL en el tiempo', fontsize=12, fontweight='bold')
    
    # Gráfica 2: Simulación en escala lineal
    ax2 = axes[0, 1]
    ax2.plot(time_dense, bcr_abl_sim_dense, label='Simulación', linewidth=2, color='#2E7D32')
    if clinical_times:
        ax2.plot(clinical_times, clinical_values, 'ro', label='Datos clínicos', markersize=8)
    ax2.axhline(y=detection_limit_percent, linestyle='--', color='gray', alpha=0.5)
    ax2.set_xlabel('Tiempo (meses)', fontsize=11)
    ax2.set_ylabel('BCR-ABL (%)', fontsize=11)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_title('BCR-ABL (Escala Lineal)', fontsize=12, fontweight='bold')
    
    # Gráfica 3: Dinámica Z (Immune cells)
    ax3 = axes[1, 0]
    ax3.plot(time_dense, Zs, label='Células inmunes (Z)', linewidth=2, color='#1565C0')
    ax3.set_xlabel('Tiempo (meses)', fontsize=11)
    ax3.set_ylabel('Z (células inmunes)', fontsize=11)
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_title('Dinámica de Células Inmunes', fontsize=12, fontweight='bold')
    
    # Gráfica 4: Parámetros del modelo
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Mostrar parámetros
    params_text = "Parámetros Optimizados:\n\n"
    for key in sorted(best_solution.keys()):
        val = best_solution[key]
        if key in ['p_XY', 'p_YX', 'K_Z', 'p_Z']:
            params_text += f"{key}: {val:.4e}\n"
        else:
            params_text += f"{key}: {val:.6f}\n"
    
    ax4.text(0.1, 0.9, params_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))
    
    plt.tight_layout()
    plt.show()


def save_optimization_results(best_solution, best_fitness, patient_name):
    """
    Guarda los resultados de la optimización en un archivo JSON.
    
    El archivo incluye:
    - Nombre del paciente
    - Parámetros optimizados
    - Fitness obtenido
    - Error (valor negativo del fitness)
    
    Pide confirmación al usuario antes de guardar.
    
    Parámetros:
        best_solution: Diccionario con parámetros optimizados
        best_fitness: Valor de fitness alcanzado
        patient_name: Nombre del paciente
    
    Retorna:
        True si se guardó exitosamente, False si se canceló o hubo error
    """
    result = {
        'patient': patient_name,
        'parameters': best_solution,
        'fitness': float(best_fitness),
        'error': float(-best_fitness) if best_fitness is not None else None,
    }
    
    filename = f"{patient_name.replace(' ', '_')}_optimization.json"
    
    # Confirmar antes de guardar
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Guardar Optimización")
    msg_box.setText(f"¿Estás seguro de guardar los resultados en '{filename}'?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)
    
    if msg_box.exec() == QMessageBox.Yes:
        try:
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            QMessageBox.information(None, "Éxito", f"Archivo guardado: {filename}")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al guardar: {str(e)}")
            return False
    return False
