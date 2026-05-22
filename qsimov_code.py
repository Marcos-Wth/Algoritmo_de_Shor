import numpy as np

import qsimov
from qsimov import QRegistry
from qsimov import QGate

def _expmod_matrix(a, N, n):
    """Función interna que construye la matriz para SimpleGate."""
    a, N, n = int(a), int(N), int(n)
    N_dimension = 2**n
    matrix = np.zeros((N_dimension, N_dimension))
    for y in range(N_dimension):
        if y < N:
            resultado = (a * y) % N
        else:
            resultado = y
        matrix[resultado, y] = 1
    return matrix

# Se registra una sola vez al importar el módulo
qsimov.add_gate("expmod", _expmod_matrix, 3, 3, overwrite=True)


def exponencial_modular(a, N, n):
    # El string "expmod(2,15,4)" sigue el mismo patrón que "runity(3)"
    # y el parser de qsimov lo acepta sin problema
    return qsimov.SimpleGate(f"expmod({a},{N},{n})")


def qft_inversa(n_qubits: int) -> qsimov.QGate:

    qft = qsimov.QGate(n_qubits, 0, f"QFT{n_qubits}")

    for k in range(n_qubits):
        # 1. Hadamard sobre el qubit actual
        qft.add_operation("H", targets=k)

        # 2. Rotaciones de fase controladas CR(2π/2^(m+1))
        #    control = qubit k+m, target = qubit k
        #    runity(m+1) aplica exactamente R(2π/2^(m+1))
        for m in range(1, n_qubits - k):
            qft.add_operation(
                f"runity({m + 1})",
                targets=k,
                controls={k + m}
            )

    # 3. Intercambio de qubits para corregir el orden de bits
    for i in range(n_qubits // 2):
        qft.add_operation("swap", targets=[i, n_qubits - 1 - i])

    return qft.invert()

def circuito_shor(N, nQ, a):
    n = N.bit_length()

    if n >= nQ:
        print(f"Error: nQ={nQ} debe ser mayor que n={n}")
        return None

    qr = QRegistry(nQ + n)

    # Superposición en el registro de conteo
    for i in range(nQ):
        qr = qr.apply_gate("H", targets=i)

    # BUG 2 corregido: el LSB del registro de trabajo es nQ+n-1 (qubit 0 = MSB global)
    # targets=nQ flipaba el MSB del trabajo → valor entero 2^(n-1) en vez de 1
    qr = qr.apply_gate("X", targets=nQ + n - 1)

    # Exponencial modular controlada
    for q in range(nQ):
        # BUG 1 corregido: qubit q tiene peso 2^(nQ-1-q), así que debe
        # controlar a^(2^(nQ-1-q)) para que el trabajo acumule a^x correctamente
        base_potenciada = pow(a, 2**(nQ - 1 - q), N)
        puerta_base = exponencial_modular(base_potenciada, N, n)
        qr = qr.apply_gate(
            puerta_base,
            targets=list(range(nQ, nQ + n)),
            controls={q}
        )

    # IQFT sobre el registro de conteo
    iqft = qft_inversa(nQ)
    qr = qr.apply_gate(iqft, targets=list(range(nQ)))

    # Medición del registro de conteo
    qr, medicion = qr.measure(set(range(nQ)))

    c_binario = "".join(str(int(medicion[i])) for i in range(nQ))

    return c_binario
