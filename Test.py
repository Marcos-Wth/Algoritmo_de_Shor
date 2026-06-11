import time
import math
import csv
import os
import multiprocessing as mp
import resource
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

def _proceso_medir_memoria(N, nQ, repeticiones, simulador, queue):
    """
    Función ejecutada en un proceso hijo aislado.

    Ejecuta el algoritmo de Shor una vez y devuelve, a través de la queue,
    el PICO de memoria RSS de este proceso (en MB). Al ser un proceso nuevo,
    su memoria parte de cero y no arrastra nada de ejecuciones anteriores.

    Args:
        N (int): Número que debe factorizar el simulador.
        nQ (int): Número de qubits para la entrada de la exponencial modular.
        repeticiones (int): Número de veces que se ejecuta el simulador.
        simulador (str): Simulador que se usa para la factorización ('qiskit' o 'qsimov').
        queue (multiprocessing.Queue): Canal para devolver el resultado al proceso padre.
    """
    try:
        Shor(N, nQ, 3, repeticiones, simulador).shor()

        # ru_maxrss: pico de RSS de ESTE proceso desde que arrancó (KB en Linux)
        pico_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        queue.put(round(pico_kb / 1024, 2))
    except Exception as e:
        queue.put(("ERROR", str(e)))


def _ejecutar_y_medir_memoria(N, nQ, repeticiones, simulador):
    """
    Ejecuta el algoritmo de Shor una vez en un proceso aislado y devuelve
    el pico de memoria RAM (RSS) consumido por dicha ejecución, en MB.

    Se usa un proceso nuevo (multiprocessing) en lugar de medir en el
    proceso actual porque el allocator de memoria no devuelve al SO la
    memoria liberada entre ejecuciones, lo que falsearía las medidas de
    ejecuciones posteriores a la de mayor consumo.

    Args:
        N (int): Número que debe factorizar el simulador.
        nQ (int): Número de qubits para la entrada de la exponencial modular.
        repeticiones (int): Número de veces que se ejecuta el simulador.
        simulador (str): Simulador que se usa para la factorización ('qiskit' o 'qsimov').
    """
    queue = mp.Queue()
    p = mp.Process(
        target=_proceso_medir_memoria,
        args=(N, nQ, repeticiones, simulador, queue)
    )
    p.start()
    resultado = queue.get()
    p.join()

    if isinstance(resultado, tuple) and resultado[0] == "ERROR":
        print(f"ERROR → {resultado[1]}")
        return -1

    return resultado


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
#  ──────────────────────── Estimación de memoria ──────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def _formato_legible(num_bytes):
    """
    Convierte un número de bytes a una cadena legible con la unidad
    más apropiada (B, KB, MB, GB, TB, PB, EB).
    """
    unidades = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    valor = float(num_bytes)
    for unidad in unidades:
        if valor < 1024 or unidad == unidades[-1]:
            return f"{valor:.2f} {unidad}"
        valor /= 1024


def estimar_memoria(valores_N, fichero_salida="estimacion_memoria_shor.csv"):
    """
    Genera un CSV con la estimación de memoria RAM necesaria para
    simular el algoritmo de Shor.

    Args:
        valores_N (list): Lista de números N a factorizar.
        fichero_salida (str): Nombre base del fichero CSV.
    """
    ruta_final = _generar_ruta_fichero(fichero_salida)
    print(f"Guardando estimaciones de memoria en '{ruta_final}'\n")

    BYTES_POR_AMPLITUD = 16  # complex128: 8 (real) + 8 (imaginaria)

    cabecera = [
        "N",
        "Bits_n",
        "Qubits_Simulado",
        "Memoria_Simulado_MB",
        "Memoria_Simulado_Legible",
        "Qubits_Estandar",
        "Memoria_Estandar_MB",
        "Memoria_Estandar_Legible",
    ]

    with open(ruta_final, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(cabecera)

        for N in valores_N:
            n = math.ceil(math.log2(N))

            # ── Circuito simplificado (el realmente simulado en este TFG) ──
            qubits_simulado = 3 * n
            bytes_simulado  = (2 ** qubits_simulado) * BYTES_POR_AMPLITUD
            mb_simulado     = round(bytes_simulado / (1024 ** 2), 4)

            # ── Circuito estándar / real (Beckman et al., 1996) ────────────
            qubits_estandar = 5 * n + 1
            bytes_estandar  = (2 ** qubits_estandar) * BYTES_POR_AMPLITUD
            mb_estandar     = round(bytes_estandar / (1024 ** 2), 4)

            writer.writerow([
                N,
                n,
                qubits_simulado,
                mb_simulado,
                _formato_legible(bytes_simulado),
                qubits_estandar,
                mb_estandar,
                _formato_legible(bytes_estandar),
            ])

            print(f"N={N} (n={n}) -> "
                  f"Simulado: {qubits_simulado} qubits ({_formato_legible(bytes_simulado)}) | "
                  f"Estándar: {qubits_estandar} qubits ({_formato_legible(bytes_estandar)})")

    print(f"\nEstimaciones de memoria generadas con éxito.")


# ═══════════════════════════════════════════════════════════════════════════════
#  ──────────────────────── Estimación de recursos cuánticos ───────────────────
# ═══════════════════════════════════════════════════════════════════════════════
def generar_bits_rsa(bits_list):
    """
    Genera valores N "placeholder" cuyo único propósito es tener
    exactamente el bit-length indicado, para usarlos en
    estimar_recursos / estimar_memoria (que solo usan
    n = ceil(log2(N))).

    NO son semiprimos reales y NO deben pasarse a los simuladores.
    """
    return [2 ** (n - 1) + 1 for n in bits_list]

def estimar_recursos(valores_N, fichero_salida="estimacion_teorica_shor.csv"):
    """
    Genera un CSV con estimaciones teóricas de profundidad, puertas y qubits 
    para el algoritmo de Shor.
    
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

# ═══════════════════════════════════════════════════════════════════════════════
#  ──────────────────────── Automatización de Ejecuciones ──────────────────────
# ═══════════════════════════════════════════════════════════════════════════════


def ejecutar_pruebas(muestras):
    
    print("INICIANDO PRUEBAS")
    tiempo_inicio = time.perf_counter()

    # Pruebas de TIEMPO DE EJECUCIÓN

    print("Ejecutando Prueba 1/6")
    medir_tiempos(
        repQiskit=128,
        repQsimov=1,
        muestras=muestras,
        fichero_salida="resultados_tiempo_1.csv"
    )

    print("Ejecutando Prueba 2/6")
    medir_tiempos(
        repQiskit=1024,
        repQsimov=5,
        muestras=muestras,
        fichero_salida="resultados_tiempo_2.csv"
    )

    # Pruebas de TASA DE FALLOS

    print("Ejecutando Prueba 3/6")
    medir_tasa_fallos(
        repQiskit=128,
        repQsimov=1,
        muestras=muestras,
        fichero_salida="resultados_tasa_fallos_1.csv"
    )

    print("Ejecutando Prueba 4/6")
    medir_tasa_fallos(
        repQiskit=1024,
        repQsimov=5,
        muestras=muestras,
        fichero_salida="resultados_tasa_fallos_2.csv"
    )

    # Estimación de MEMORIA

    v = [
        # n=4-6 bits (ya probados antes)
        15, 21, 35, 39, 51, 55,
        # n=7 bits
        65, 69, 77, 85, 87, 91,
        # n=8 bits
        111, 115, 119, 123, 129,
        # n=9 bits
        155, 159, 161, 177, 183,
        # n=10 bits
        213, 215, 217, 219, 221,
        # n=11 bits (≈128 GB teóricos para el simulador)
        377, 391, 437, 481, 493,
        # n=12 bits (≈1 TB teóricos para el simulador — punto claramente inviable)
        2279, 2491, 2501, 2537, 2623 ]
    
    print("Ejecutando Prueba 5/6")
    estimar_memoria(
        valores_N= v,
        fichero_salida= "estimaciones_memoria.csv"
    )

    # Estimación de CIRCUITO CUÁNTICO

    BITS_RSA = [512, 768, 1024, 1536, 2048, 3072, 4096]
    v = generar_bits_rsa(BITS_RSA)

    print("Ejecutando Prueba 6/6")
    estimar_recursos(
            valores_N= v,
            fichero_salida= "estimaciones_circuito.csv"
    )

    print("PRUEBAS FINALIZADAS")
    tiempo_fin = time.perf_counter()
    tiempo_total_minutos = (tiempo_fin - tiempo_inicio) / 60
    print(f"\nTiempo total de ejecución: {tiempo_total_minutos:.2f} minutos.")

# medir_memoria(
#         repQiskit=20,
#         repQsimov= 1,
#         fichero_salida= "resultados_memoria.csv"
# )



ejecutar_pruebas(15) # Cambiar el numero introdicido puede aumentar mucho el tiempo de ejecución