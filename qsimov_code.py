import numpy as np

import qsimov
from qsimov import QRegistry


def _expmod_matrix(a, N, n):

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

# Añado la puerta a el 'pool' de puertas de qsimov
qsimov.add_gate("expmod", _expmod_matrix, 3, 3, overwrite=True)

# Esto solo es para que luego el codigo final sea lo mas parecido posible al de qiskit
def exponencial_modular(a, N, n):

    return qsimov.SimpleGate(f"expmod({a},{N},{n})")


def qft_inversa(n_qubits: int) -> qsimov.QGate:

    qft = qsimov.QGate(n_qubits, 0, f"QFT{n_qubits}")

    for k in range(n_qubits):

        # Aplico Hadamard al qubit actual (k)
        qft.add_operation("H", targets=k)

        # Aplico las rotaciones de fase del resto de qbits sobre el qubit k
        for m in range(1, n_qubits - k):
            qft.add_operation(
                f"runity({m + 1})",
                targets=k,
                controls={k + m}
            )

    #  Intercambio de qubits para corregir el orden de bits
    for i in range(n_qubits // 2):
        qft.add_operation("swap", targets=[i, n_qubits - 1 - i])

    # La hago iqft
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

    # Inicializo a 1 el ultimo qubit
    qr = qr.apply_gate("X", targets=nQ + n - 1)

    # Aplico la exponencial modular al registro auxiliar
    for q in range(nQ):
        base_potenciada = pow(a, 2**(nQ - 1 - q), N)
        puerta_base = exponencial_modular(base_potenciada, N, n)
        qr = qr.apply_gate(
            puerta_base,
            targets=list(range(nQ, nQ + n)),
            controls={q}
        )

    # aplico la IQFT sobre el registro de conteo
    iqft = qft_inversa(nQ)
    qr = qr.apply_gate(iqft, targets=list(range(nQ)))

    # Medición
    qr, medicion = qr.measure(set(range(nQ)))
    c_binario = "".join(str(int(medicion[i])) for i in range(nQ))

    return c_binario
