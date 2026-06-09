import time
import math
import csv
import os
import statistics
from datetime import datetime
from Shor import Shor


# Semiprimos impares (producto de exactamente dos primos distintos) en [15, 55]:
# 15=3×5, 21=3×7, 33=3×11, 35=5×7, 39=3×13, 51=3×17, 55=5×11
# No hay más en ese intervalo. El 77=7×11 y el 91=7×13 se quedan fuera.
VALORES_N_DEFECTO = [15, 21, 33, 35, 39, 51, 55]


def calcular_qubits(N):
    n = math.ceil(math.log2(N))
    nQ = 2 * n
    return nQ


def _generar_ruta_fichero(fichero_salida):
    """
    Resuelve la ruta final del fichero:
      - Lo coloca siempre en la carpeta Resultados (junto al script).
      - Si ya existe un fichero con ese nombre, inserta la fecha antes
        de la extensión en vez de sobreescribirlo.
    """
    carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resultados")
    os.makedirs(carpeta, exist_ok=True)

    nombre = os.path.basename(fichero_salida)

    raiz, extension = os.path.splitext(nombre)
    fecha = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return os.path.join(carpeta, f"{raiz}_{fecha}{extension}")


def _ejecutar_y_medir(N, nQ, repeticiones, simulador):
    """Ejecuta el algoritmo de Shor una vez. Devuelve el tiempo en segundos o -1 si falla."""
    try:
        t0 = time.perf_counter()
        Shor(N, nQ, 3, repeticiones, simulador).shor()
        return round(time.perf_counter() - t0, 4)
    except Exception as e:
        print(f"ERROR → {e}")
        return -1


def medir_tiempos(repQiskit, repQsimov, muestras=5,
                  valores_N=None,
                  fichero_salida="resultados_shor.csv"):
    """
    Mide el tiempo medio de ejecución del algoritmo de Shor para ambos
    simuladores y escribe los resultados en Resultados/<fichero_salida>.

    Args:
        repQiskit  (int)  : Repeticiones del circuito cuántico para Qiskit.
        repQsimov  (int)  : Repeticiones del circuito cuántico para Qsimov.
                            Debe ser distinto de repQiskit.
        muestras   (int)  : Ejecuciones por N sobre las que se calcula la media.
        valores_N  (list) : Valores de N a probar. Si None, usa VALORES_N_DEFECTO.
        fichero_salida (str): Nombre base del fichero CSV.
    """

    if valores_N is None:
        valores_N = VALORES_N_DEFECTO

    ruta_final = _generar_ruta_fichero(fichero_salida)
    print(f"Guardando resultados en '{ruta_final}'\n")

    cabecera = ["N", "Qubits",
                "TiempoMedioQiskit", "RepQiskit",
                "TiempoMedioQsimov", "RepQsimov"]

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
                t = _ejecutar_y_medir(N, nQ, repQiskit, "qiskit")
                print(f"{t:.4f} s" if t != -1 else "FALLO")
                if t != -1:
                    tiempos_qiskit.append(t)

            tiempo_medio_qiskit = (round(statistics.mean(tiempos_qiskit), 4)
                                   if tiempos_qiskit else -1)

            # ── Qsimov ────────────────────────────────────────────────────
            tiempos_qsimov = []
            for i in range(muestras):
                print(f"  [Qsimov] muestra {i+1}/{muestras} ...", end=" ", flush=True)
                t = _ejecutar_y_medir(N, nQ, repQsimov, "qsimov")
                print(f"{t:.4f} s" if t != -1 else "FALLO")
                if t != -1:
                    tiempos_qsimov.append(t)

            tiempo_medio_qsimov = (round(statistics.mean(tiempos_qsimov), 4)
                                   if tiempos_qsimov else -1)

            writer.writerow([N, qubits,
                             tiempo_medio_qiskit, repQiskit,
                             tiempo_medio_qsimov, repQsimov])
            f.flush()

        # Fila final: número de muestras usadas para la media
        writer.writerow([])
        writer.writerow(["Muestras:", muestras])

    print(f"\nResultados guardados en '{ruta_final}'")


if __name__ == "__main__":
    medir_tiempos(
        repQiskit=1,
        repQsimov=1,
        muestras=3,
        fichero_salida="resultados_shor.csv"
    )