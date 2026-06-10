import time
import math
import csv
import os
import psutil
import statistics
from datetime import datetime
from Shor import Shor


# ═══════════════════════════════════════════════════════════════════════════════
# ───────────────────────────── Funciones generales ─────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

 # Todos los semiprimos en el intervalo [15,55]. No hay mayores a 55 porque los simuladores no pueden paasar los 21 qubits de circuito
VALORES_N_DEFECTO = [15, 21, 33, 35, 39, 51, 55]  


def calcular_qubits(N):
    n = math.ceil(math.log2(N))
    nQ = 2 * n
    return nQ


def _generar_ruta_fichero(nombre_fichero):
    """
    Le da el nombre final al fichero (con la ruta incluida)

    Args:
        nombre_fichero (str): El nombre base del fichero.
    """
    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resultados")
    os.makedirs(carpeta, exist_ok=True)

    nombre            = os.path.basename(nombre_fichero)
    raiz, extension   = os.path.splitext(nombre)
    fecha             = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return os.path.join(carpeta, f"{raiz}_{fecha}{extension}")


# ═══════════════════════════════════════════════════════════════════════════════
# ─────────────────────────────── Test de Tiempo ────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def _ejecutar_y_medir_tiempo(N, nQ, repeticiones, simulador):
    """
    Ejecuta el algoritmo de Shor una vez y devuelve el tiempo de ejecución de este en segundos.

    Args:
        N (int): Número que debe factorizar el simulador.
        nQ (int): Número de qubits para la entrada de la exponencial modular.
        repeticiones (int): Número de veces que se ejecuta el simulador.
        simulador (list): Simulador que se usa para la factorización.
    """
    try:
        t0 = time.perf_counter()
        Shor(N, nQ, 3, repeticiones, simulador).shor()
        return round(time.perf_counter() - t0, 4)
    except Exception as e:
        print(f"ERROR → {e}")
        return -1


def medir_tiempos(repQiskit, repQsimov, muestras=5,
                  valores_N=None,
                  fichero_salida="resultados_tiempo.csv"):
    """
    Funcion que automatiza las pruebas de Tiempo de ejecución.

    Args:
        repQiskit (int): Repeticiones del circuito cuántico para Qiskit.
        repQsimov (int): Repeticiones del circuito cuántico para Qsimov.
        muestras (int): Ejecuciones por N sobre las que se calcula la media.
        valores_N (list): Valores de N a probar. Si None, usa VALORES_N_DEFECTO.
        fichero_salida (str): Nombre base del fichero CSV.
    """
    if repQiskit == repQsimov:
        raise ValueError("repQiskit y repQsimov deben ser distintos entre sí.")

    if valores_N is None:
        valores_N = VALORES_N_DEFECTO

    ruta_final = _generar_ruta_fichero(fichero_salida)
    print(f"Guardando resultados en '{ruta_final}'\n")

    cabecera = ["N", "Qubits",
                "TiempoMedioQiskit", "StdQiskit", "RepQiskit",
                "TiempoMedioQsimov", "StdQsimov", "RepQsimov"]

    with open(ruta_final, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(cabecera)

        for N in valores_N:
            nQ     = calcular_qubits(N)
            qubits = (3 * nQ) // 2

            print(f"{'='*55}")
            print(f"  N={N}  |  nQ={nQ}  |  Qubits del circuito={qubits}")
            print(f"{'='*55}")

            # ── Qiskit ────────────────────────────────────────────────────
            tiempos_qiskit = []
            for i in range(muestras):
                print(f"  [Qiskit] muestra {i+1}/{muestras} ...", end=" ", flush=True)
                t = _ejecutar_y_medir_tiempo(N, nQ, repQiskit, "qiskit")
                print(f"{t:.4f} s" if t != -1 else "FALLO")
                if t != -1:
                    tiempos_qiskit.append(t)

            tiempo_medio_qiskit = (round(statistics.mean(tiempos_qiskit), 4)
                                   if tiempos_qiskit else -1)
            std_qiskit          = (round(statistics.stdev(tiempos_qiskit), 4)
                                   if len(tiempos_qiskit) >= 2 else -1)

            # ── Qsimov ────────────────────────────────────────────────────
            tiempos_qsimov = []
            for i in range(muestras):
                print(f"  [Qsimov] muestra {i+1}/{muestras} ...", end=" ", flush=True)
                t = _ejecutar_y_medir_tiempo(N, nQ, repQsimov, "qsimov")
                print(f"{t:.4f} s" if t != -1 else "FALLO")
                if t != -1:
                    tiempos_qsimov.append(t)

            tiempo_medio_qsimov = (round(statistics.mean(tiempos_qsimov), 4)
                                   if tiempos_qsimov else -1)
            std_qsimov          = (round(statistics.stdev(tiempos_qsimov), 4)
                                   if len(tiempos_qsimov) >= 2 else -1)

            writer.writerow([N, qubits,
                             tiempo_medio_qiskit, std_qiskit, repQiskit,
                             tiempo_medio_qsimov, std_qsimov, repQsimov])
            f.flush()

        writer.writerow([])
        writer.writerow(["Muestras:", muestras])

    print(f"\nResultados guardados en '{ruta_final}'")


# ═══════════════════════════════════════════════════════════════════════════════
#  ─────────────────────────── Test de Tasa de Éxitos ──────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def _ejecutar_y_medir_tasa_fallos(N, nQ, repeticiones, simulador):
    """
    Ejecuta el algoritmo de Shor una vez y devuelve si se encontró la solución o no.

    Args:
        N (int): Número que debe factorizar el simulador.
        nQ (int): Número de qubits para la entrada de la exponencial modular.
        repeticiones (int): Número de veces que se ejecuta el simulador.
        simulador (list): Simulador que se usa para la factorización.
    """
    try:
        resultado = Shor(N, nQ, 3, repeticiones, simulador).shor()
        return bool(resultado[0])
    except Exception as e:
        print(f"ERROR → {e}")
        return False


def medir_tasa_fallos(repQiskit, repQsimov, muestras=5,
                      valores_N=None,
                      fichero_salida="resultados_tasa_exitos.csv"):
    """
    Funcion que automatiza las pruebas de Tiempo de tasa de fallos.

    Args:
        repQiskit (int): Repeticiones del circuito cuántico para Qiskit.
        repQsimov (int): Repeticiones del circuito cuántico para Qsimov.
        muestras (int): Ejecuciones por N sobre las que se calcula la media.
        valores_N (list): Valores de N a probar. Si None, usa VALORES_N_DEFECTO.
        fichero_salida (str): Nombre base del fichero CSV.
    """
    if repQiskit == repQsimov:
        raise ValueError("repQiskit y repQsimov deben ser distintos entre sí.")

    if valores_N is None:
        valores_N = VALORES_N_DEFECTO

    ruta_final = _generar_ruta_fichero(fichero_salida)
    print(f"Guardando resultados en '{ruta_final}'\n")

    cabecera = ["N", "Qubits",
                "TasaFalloQiskit", "StdQiskit", "RepQiskit",
                "TasaFalloQsimov", "StdQsimov", "RepQsimov"]

    with open(ruta_final, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(cabecera)

        for N in valores_N:
            nQ     = calcular_qubits(N)
            qubits = (3 * nQ) // 2

            print(f"{'='*55}")
            print(f"  N={N}  |  nQ={nQ}  |  Qubits del circuito={qubits}")
            print(f"{'='*55}")

            # ── Qiskit ────────────────────────────────────────────────────
            fallos_qiskit = []
            for i in range(muestras):
                print(f"  [Qiskit] muestra {i+1}/{muestras} ...", end=" ", flush=True)
                exito = _ejecutar_y_medir_tasa_fallos(N, nQ, repQiskit, "qiskit")
                print("ÉXITO ✓" if exito else "FALLO ✗")
                fallos_qiskit.append(0 if exito else 100)

            tasa_qiskit = (round(statistics.mean(fallos_qiskit), 2)
                           if fallos_qiskit else -1)
            std_qiskit  = (round(statistics.stdev(fallos_qiskit), 2)
                           if len(fallos_qiskit) >= 2 else -1)

            # ── Qsimov ────────────────────────────────────────────────────
            fallos_qsimov = []
            for i in range(muestras):
                print(f"  [Qsimov] muestra {i+1}/{muestras} ...", end=" ", flush=True)
                exito = _ejecutar_y_medir_tasa_fallos(N, nQ, repQsimov, "qsimov")
                fallos_qsimov.append(0 if exito else 100)

            tasa_qsimov = (round(statistics.mean(fallos_qsimov), 2)
                           if fallos_qsimov else -1)
            std_qsimov  = (round(statistics.stdev(fallos_qsimov), 2)
                           if len(fallos_qsimov) >= 2 else -1)

            writer.writerow([N, qubits,
                             tasa_qiskit, std_qiskit, repQiskit,
                             tasa_qsimov, std_qsimov, repQsimov])
            f.flush()

        writer.writerow([])
        writer.writerow(["Muestras:", muestras])

    print(f"\nResultados guardados en '{ruta_final}'")

# ═══════════════════════════════════════════════════════════════════════════════
#  ───────────────────────────── Test de Memoria ──────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def _ejecutar_y_medir_memoria(N, nQ, repeticiones, simulador):
    """
    Ejecuta el algoritmo de Shor una vez y devuelve el consumo de memoria RAM en MB.

    Args:
        N (int): Número que debe factorizar el simulador.
        nQ (int): Número de qubits para la entrada de la exponencial modular.
        repeticiones (int): Número de veces que se ejecuta el simulador.
        simulador (str): Simulador que se usa para la factorización ('qiskit' o 'qsimov').
    """
    proceso = psutil.Process(os.getpid())
    memoria_inicial = proceso.memory_info().rss

    try:
        Shor(N, nQ, 3, repeticiones, simulador).shor()
        memoria_final = proceso.memory_info().rss
        
        # Diferencia en Megabytes (MB)
        consumo_ram = (memoria_final - memoria_inicial) / (1024 ** 2)
        return round(max(0.0, consumo_ram), 2)
        
    except Exception as e:
        print(f"ERROR → {e}")
        return -1


def medir_memoria(repQiskit, repQsimov, 
                  valores_N=None,
                  fichero_salida="resultados_memoria.csv"):
    """
    Funcion que automatiza las pruebas de consumo de Memoria (RAM).
    Se realiza una única medición por valor de N dado el determinismo
    del tamaño del vector de estado en simuladores cuánticos.

    Args:
        repQiskit (int): Repeticiones del circuito cuántico para Qiskit.
        repQsimov (int): Repeticiones del circuito cuántico para Qsimov.
        valores_N (list): Valores de N a probar. Si None, usa VALORES_N_DEFECTO.
        fichero_salida (str): Nombre base del fichero CSV.
    """
    if repQiskit == repQsimov:
        raise ValueError("repQiskit y repQsimov deben ser distintos entre sí.")

    if valores_N is None:
        valores_N = VALORES_N_DEFECTO

    ruta_final = _generar_ruta_fichero(fichero_salida)
    print(f"Guardando resultados de memoria en '{ruta_final}'\n")

    cabecera = ["N", "Qubits",
                "MemoriaQiskit_MB", "RepQiskit",
                "MemoriaQsimov_MB", "RepQsimov"]

    with open(ruta_final, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(cabecera)

        for N in valores_N:
            nQ     = calcular_qubits(N)
            qubits = (3 * nQ) // 2

            print(f"{'='*55}")
            print(f"  N={N}  |  nQ={nQ}  |  Qubits del circuito={qubits}")
            print(f"{'='*55}")

            # ── Qiskit ────────────────────────────────────────────────────
            print("  [Qiskit] Midiendo RAM...", end=" ", flush=True)
            memoria_qiskit = _ejecutar_y_medir_memoria(N, nQ, repQiskit, "qiskit")
            print(f"{memoria_qiskit:.2f} MB" if memoria_qiskit != -1 else "FALLO")

            # ── Qsimov ────────────────────────────────────────────────────
            print("  [Qsimov] Midiendo RAM...", end=" ", flush=True)
            memoria_qsimov = _ejecutar_y_medir_memoria(N, nQ, repQsimov, "qsimov")
            print(f"{memoria_qsimov:.2f} MB" if memoria_qsimov != -1 else "FALLO")

            writer.writerow([N, qubits,
                             memoria_qiskit, repQiskit,
                             memoria_qsimov, repQsimov])
            f.flush()

    print(f"\nResultados guardados en '{ruta_final}'")

# ═══════════════════════════════════════════════════════════════════════════════
#  ───────────────────────────── Estimación de recursos─────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def estimar_recursos(valores_N, fichero_salida="estimacion_teorica_shor.csv"):
    """
    Genera un CSV con estimaciones teóricas de profundidad, puertas y qubits 
    para el algoritmo de Shor basado en la arquitectura de Vedral, Barenco, Ekert 
    y Beckman et al. (1996).
    
    Args:
        valores_N (list): Lista de números N a factorizar.
        fichero_salida (str): Nombre base del fichero CSV.
    """
    ruta_final = _generar_ruta_fichero(fichero_salida)
    print(f"Guardando estimaciones teóricas en '{ruta_final}'\n")

    # Cabecera ajustada para la versión estándar
    cabecera = [
        "N", 
        "Bits_n", 
        "Qubits_Estandar", 
        "Puertas_Ideal", 
        "Puertas_Realista", 
        "Profundidad_Ideal", 
        "Profundidad_Realista"
    ]

    with open(ruta_final, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(cabecera)

        for N in valores_N:
            # 1. Calculamos el tamaño en bits de N
            n = math.ceil(math.log2(N))
            
            # 2. Fórmulas de la arquitectura Estándar (Beckman et al., 1996)
            # Requiere 2n (control) + n (target) + n+1 (ancillas matemáticas) + n (ancillas de suma)
            qubits = 5 * n + 1 
            
            # Coste asintótico de puertas para aritmética booleana
            puertas_ideal = 72 * (n ** 3)
            
            # La profundidad sigue ligada al orden de puertas por la secuencialidad
            # del registro de control en multiplicaciones modulares.
            profundidad_ideal = puertas_ideal 
            
            # 3. Factor de corrección para topologías reales (overhead de SWAPs)
            factor_enrutamiento = 2
            puertas_realista = puertas_ideal * factor_enrutamiento
            profundidad_realista = profundidad_ideal * factor_enrutamiento

            # Guardamos la fila
            writer.writerow([
                N, 
                n, 
                qubits, 
                puertas_ideal, 
                puertas_realista, 
                profundidad_ideal, 
                profundidad_realista
            ])
            
            print(f"N={N} (Bits={n}) -> Qubits: {qubits} | Est. Realista: {puertas_realista} puertas")

    print(f"\nEstimaciones teóricas generadas con éxito.")

# ----------------------------------------------------------------
    #   PRUEBAS DE CÓDIGO


# medir_tiempos(
#         repQiskit=256,
#         repQsimov=5,
#         muestras=5,
#         fichero_salida="resultados_tiempo.csv"
#     )
    

# medir_tasa_fallos(
#         repQiskit=256,
#         repQsimov=5,
#         muestras=5,
#         fichero_salida="resultados_tasa_fallos.csv"
#     )

# medir_memoria(
#         repQiskit=256,
#         repQsimov= 5,
#         fichero_salida= "resultados_memoria.csv"
# )

v = [15, 21, 33, 35, 39, 51, 55] 
estimar_recursos(
        valores_N= v,
        fichero_salida= "estimaciones_circuito.csv"
)