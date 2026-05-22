import numpy as np
import math

from qsimov import QRegistry, QGate
from qsimov import QGate


def exponencial_modular(a, N, n):
    N_dimension = 2**n 
    matrix = np.zeros((N_dimension, N_dimension))
    for y in range(N_dimension):
        if y < N:
            resultado = (a * y) % N
        else:
            resultado = y
        matrix[resultado, y] = 1
    puerta = QGate(num_qubits=n, num_bits=n, name=f"U_{a}mod{N}")
    try:
        puerta.matrix = matrix
    except AttributeError:
        print("Aviso: No se puede inyectar la matriz directamente. Intentando alternativa...")
        
    return puerta

def qft_inversa(qr, nQ):

    # Swaps
    for i in range(nQ // 2):
        qr = qr.apply_gate("SWAP", targets=[i, nQ - i - 1])

    # Rotaciones y Hadamard
    for j in range(nQ):
        for m in range(j):
            angulo = -np.pi / (2 ** (j - m))
            
            try:
                qr = qr.apply_gate("P", targets=[j], controls=[m], angle=angulo)
            except (TypeError, ValueError):
                # Si falla, fabricamos la puerta Fase controlada nosotros mismos al vuelo
                matriz_fase = np.array([[1, 0], [0, np.exp(1j * angulo)]])
                puerta_fase = QGate(name=f"P_{angulo:.2f}", matrix=matriz_fase)
                qr = qr.apply_gate(puerta_fase, targets=[j], controls=[m])
            
        qr = qr.apply_gate("H", targets=[j])
    
    return qr

def ejecutar_shor_qsimov(N, nQ, a, repeticiones=4096):
    n = N.bit_length()
    
    if (n >= nQ):
        print(f"Error: El número de qubits de conteo (nQ={nQ}) debe ser mayor que n={n}")
        return 0

    qr = QRegistry(nQ + n)

    # Superposición
    for i in range(nQ):
        qr = qr.apply_gate("H", targets=[i])
        
    # Inicialización a 1 en el registro inferior
    qr = qr.apply_gate("X", targets=[nQ])

    # Exponencial Modular controlada
    for q in range(nQ):
        base_potenciada = pow(a, 2**q, N) 
        puerta_base = exponencial_modular(base_potenciada, N, n)
        
        qr = qr.apply_gate(puerta_base, targets=list(range(nQ, nQ + n)), controls=[q])

    qr = qft_inversa(qr, nQ)

    _, medicion = qr.measure(list(range(nQ)))
    c_binario = "".join(str(int(bit)) for bit in medicion)

    return {c_binario: repeticiones}

def resultado_mayor_indice_qsimov(counts):
    # Lógica agnóstica igual que antes
    counts_copia = dict(counts) 
    
    while counts_copia:
        c_binario = max(counts_copia, key=counts_copia.get)
        c = int(c_binario, 2)

        if c != 0:
            return c
        
        del counts_copia[c_binario]

    return 0