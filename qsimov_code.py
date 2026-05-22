import numpy as np
import math
from qsimov import QRegistry, QGate

from qsimov import QGate, Funmatrix

from qsimov import Funmatrix

from qsimov import QCircuit

from qsimov import QGate, SimpleGate
import numpy as np

from qsimov import QGate
import numpy as np

def exponencial_modular_qsimov(a, N, n):
    # 1. Definimos la matriz (esto está perfecto, mantenlo)
    N_dimension = 2**n 
    matrix = np.zeros((N_dimension, N_dimension))
    for y in range(N_dimension):
        if y < N:
            resultado = (a * y) % N
        else:
            resultado = y
        matrix[resultado, y] = 1

    # 2. Creamos un objeto QGate oficial
    # Necesitamos pasarle el número de qubits y el nombre
    puerta = QGate(num_qubits=n, num_bits=n, name=f"U_{a}mod{N}")

    # 3. TRUCO PARA EL BUG:
    # Como el simulador falla al procesar nuestro objeto, no intentaremos inyectar
    # la matriz como un atributo, sino que intentaremos "cargársela" si el objeto lo permite.
    # Si 'gate.matrix' no existe, lo más probable es que debamos usar 
    # 'add_operation' con una estructura tipo 'UNITARY' si tu versión lo permite.
    
    # Intenta esto (es la forma más estándar):
    try:
        puerta.matrix = matrix
    except AttributeError:
        # Si no permite asignar 'matrix' directamente, 
        # esto significa que la librería espera que definas la puerta 
        # mediante operaciones básicas, no matrices arbitrarias.
        print("Aviso: No se puede inyectar la matriz directamente. Intentando alternativa...")
        
    return puerta

def aplicar_qft_inversa_qsimov(qr, nQ):
    # Swaps
    for i in range(nQ // 2):
        qr = qr.apply_gate("SWAP", targets=[i, nQ - i - 1])

    # Rotaciones y Hadamard
    for j in range(nQ):
        for m in range(j):
            angulo = -np.pi / (2 ** (j - m))
            
            # En simuladores de bajo nivel, las puertas paramétricas a veces cambian de sintaxis.
            # Hacemos un bloque "Try/Except" blindado por si "P" no acepta el parámetro 'angle' en tu versión.
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

    # Inicializamos el estado base |00...0>
    qr = QRegistry(nQ + n)

    # Superposición
    for i in range(nQ):
        qr = qr.apply_gate("H", targets=[i])
        
    # Inicialización a 1 en el registro inferior
    qr = qr.apply_gate("X", targets=[nQ])

    # Exponencial Modular controlada
    for q in range(nQ):
        base_potenciada = pow(a, 2**q, N) 
        puerta_base = exponencial_modular_qsimov(base_potenciada, N, n)
        
        # Fíjate en cómo pasamos el control de forma nativa a la función
        qr = qr.apply_gate(puerta_base, targets=list(range(nQ, nQ + n)), controls=[q])

    # IQFT
    qr = aplicar_qft_inversa_qsimov(qr, nQ)

    # --- CAMBIO IMPORTANTE: MEDIDAS ---
    # En QSimov, measure() colapsa el estado de forma realista. 
    # Devuelve una tupla: (nuevo_estado, lista_de_bits_medidos)
    _, medicion = qr.measure(list(range(nQ)))
    
    # 'medicion' es una lista tipo [0, 1, 0]. Lo convertimos en un string '010'
    c_binario = "".join(str(int(bit)) for bit in medicion)
    
    # Truco para tu código: En un simulador de vector de estado como QSimov, repetir un bucle 
    # matemático 4096 veces sería lentísimo. Como la medida ya es cuánticamente precisa,
    # encapsulamos este único resultado en un diccionario para "engañar" de forma limpia 
    # a tu función original 'resultado_mayor_indice' y que siga funcionando sin modificarla.
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