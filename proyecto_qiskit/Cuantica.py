import math
import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer.primitives import SamplerV2
from qiskit.circuit.library import UnitaryGate


def exponencial_modular(a, N, n):
    '''
    Crea una puerta unitaria que calcula f(y) = (a * y) mod N.
    Este método usa una matriz de permutación.
    '''
    # Calculo la dimension del espacio de estados
    N_dimension = 2**n 
    # Creo la matriz de ceros
    matrix = np.zeros((N_dimension, N_dimension))

    for y in range(N_dimension):
        if y < N:
            # Multiplicacion modular
            resultado = (a * y) % N
        else:
            # operacion identidad 
            resultado = y
        
        matrix[resultado, y] = 1

    puerta_u = UnitaryGate(matrix, label=f"({a}*y) mod {N}")
    return puerta_u.control()


def circuito_shor(N, nQ, a):
    '''
    Esta funcion crea el circuito que genera las mediciones de la c en el algoritmo de Shor

    Args:
        N (int): Modulo de la exponencial modular
        nQ (int): Numero de qubits de la entrada de la exponencial modular
        a (int): Base de la exponencial modular

    Returns:
        QuantumCircuit: Circuito cuantica que genera las mediciones del algoritmo de shor
    '''
    n = N.bit_length() # Obtengo el numero de qubits necesario para codificar N
    
    if (n >= nQ):
        print(f"Error: El número de qubits de conteo (nQ={nQ}) debe ser mayor que los bits del módulo (n={n}) para garantizar precisión en la QFT")
        return 0

    qc = QuantumCircuit(nQ + n, nQ)

    qc.h(range(nQ))    # Pongo en superposición los qubits de la entrada de la exponencial modular
    qc.x(nQ)           # Pongo el primer qubit a 1, para que la primera multiplicación de la exponencial modular no de 0

    # Aplico la puerta controlada 'nQ' veces
    for q in range(nQ):
        # Calculamos la base para esta iteración: a^(2^q) mod 15
        # Esto es lo que "escala" la exponencial modular correctamente
        base_potenciada = pow(a, 2**q, 15)
        
        # Creamos la compuerta específica para esa potencia
        puerta = exponencial_modular(base_potenciada, N, n)
        
        # La añadimos al circuito
        qc.append(puerta, [q] + list(range(nQ, nQ + n)))
        

    #iqft = QFT(num_qubits=nQ, inverse=True).to_gate()
    iqft = qft_inversa(nQ)
    qc.append(iqft, range(nQ))

    qc.measure(range(nQ), range(nQ)) # Mido el resultado de la ejecucion del circuito cuantico
    
    return qc


def ejecutar_en_simulador(qc, optimizacion=1, repeticiones=4096):
    '''
    Esta función usa un sampler para generar las mediciones de un circuito cuantico

    Args:
        qc (QuantumCircuit): Circuito cuyas mediciones se quieren obtener
        optimizacion (int): Nivel al que se optimizan los circuitos generados para samplear. Puede ser 0,1,2,3, de base es 1
        repeticiones (int): Numero de veces que va a generar una solucion

    Returns:
        dict: diccionario en el que se indica el numero de veces que se ha medido cada combinación de bits
    '''
    backend = AerSimulator()
    pm = generate_preset_pass_manager(optimization_level= optimizacion, backend=backend)
    isa_circuit = pm.run(qc)

    sampler = SamplerV2()
    result = sampler.run([isa_circuit], shots=repeticiones).result()

    counts = result[0].data.c.get_counts() # .c es como llama qiskit al registro de los bits clasicos por defecto, aunque hay que tener cuidado con esto
    return counts

def resultado_mayor_indice(counts):
    '''
    Esta funcion saca de un diccionario (.get_counts() del sampler) el resultado con indice de repetición mayor

    Args:
        counts (dict): Diccionario con los resultados de las mediciones y su indice de repeticion, de la forma: 'medicion': indice (int)

    Returns:
        int: Número decodificado correspondiente al resultado más repetido durante la ejecución del circuito cuantico
    '''

    while counts:

        c_binario = max(counts, key=counts.get)     # Obtengo el resultado con mator indice de repeticion
        c = int(c_binario, 2)       # Lo decodifico

        if (c!=0):
            return c
        
        del counts[c_binario]       # Si es 0, lo elimino y compruebo el siguiente

    return 0    # Si todos los resultados eran 0, lo devuelvo


def qft_inversa(nQ):
    '''
    Esta funcion implementa la puerta QFT Inversa, para usarla dentro del algoritmo principal

    Args:
        nQ (int): Número de qubits con los que debe trabajar la QFT Inversa
    '''

    qc = QuantumCircuit(nQ, name="IQFT")

    # Invierto el orden de los qubits porque qiskit usa little endian
    for i in range (nQ // 2):
        qc.swap(i, nQ -i -1)

    # Aplico las rotaciones y la puerta Hadamard
    for j in range (nQ):
        for m in range(j):
            angulo = -np.pi / (2 ** (j - m))  # 2 ^ (j - m) = 2 ^ ('distancia' entre el qubit que se esta procesando y uno anterior)
            qc.cp(angulo, m, j)
        qc.h(j)

    return qc.to_gate()