import math
import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer.primitives import SamplerV2
from qiskit.circuit.library import UnitaryGate


def exponencial_modular_15(a, n):
    '''
    Crea una puerta unitaria que calcula f(y) = (a * y) mod 15.
    Este método usa una matriz de permutación.
    '''

    N_dimension = 2**n 
    matrix = np.zeros((N_dimension, N_dimension))

    for y in range(N_dimension):
        if y < 15:
            resultado = (a * y) % 15
        else:
            resultado = y
        
        matrix[resultado, y] = 1

    puerta_u = UnitaryGate(matrix, label=f"({a}*y) mod 15")
    return puerta_u.control()

'''
def exponencial_modular_15(a, n):
    qc = QuantumCircuit(n)

    if a in [2, 13]:

        qc.swap(0, 1)

        qc.swap(1, 2)

        qc.swap(2, 3)

        if a == 13: 
            qc.x([0, 1, 2, 3])

    elif a in [7, 8]:

        qc.swap(2, 3)

        qc.swap(1, 2)

        qc.swap(0, 1)

        if a == 7: 
            qc.x([0, 1, 2, 3])

    elif a in [4, 11]:

        qc.swap(1, 3)

        qc.swap(0, 2)

        if a == 11: 
            qc.x([0, 1, 2, 3])

    elif a == 14:

        qc.x([0, 1, 2, 3])

    else:
        raise ValueError(f"Base {a} no válida")

    return qc.to_gate().control()
    '''

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
    exponencial_modular = exponencial_modular_15(a, n)
    for q in range(nQ):
        # Calculamos la base para esta iteración: a^(2^q) mod 15
        # Esto es lo que "escala" la exponencial modular correctamente
        base_potenciada = pow(a, 2**q, 15)
        
        # Creamos la compuerta específica para esa potencia
        puerta = exponencial_modular_15(base_potenciada, n)
        
        # La añadimos al circuito
        qc.append(puerta, [q] + list(range(nQ, nQ + n)))
        

    # QFT Inversa
    iqft = QFT(num_qubits=nQ, inverse=True).to_gate()
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

    # DEBUG
    counts_ordenado = dict(sorted(counts.items(), key=lambda item: item[1]))
    print(counts_ordenado)
    #DEBUG

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
        print("El resultado más repetido es :",c_binario) # DEBUG
        c = int(c_binario, 2)       # Lo decodifico

        if (c!=0):
            return c
        
        del counts[c_binario]       # Si es 0, lo elimino y compruebo el siguiente

    return 0    # Si todos los resultados eran 0, lo devuelvo
