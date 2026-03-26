from modulos import Transformaciones
import math
import random

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer.primitives import SamplerV2


def exponencial_modular_15(a):
    '''
    Esta funcion crea una puerta para calcular la exponencial modular para N = 15

    Args:
        a (int): Base de la exponencial modular

    Returns:
        Gate(): Puerta cuantica que calcula la exponencial modular
    '''
    qc = QuantumCircuit(4)
    
    if a in [2, 13]:
        qc.swap(0, 1)
        qc.swap(1, 2)
        qc.swap(2, 3)
        if a == 13: qc.x([0, 1, 2, 3])
        
    elif a in [7, 8]:
        qc.swap(2, 3)
        qc.swap(1, 2)
        qc.swap(0, 1)
        if a == 7: qc.x([0, 1, 2, 3])
        
    elif a in [4, 11]:
        qc.swap(1, 3)
        qc.swap(0, 2)
        if a == 11: qc.x([0, 1, 2, 3])
        
    elif a == 14:
        qc.x([0, 1, 2, 3])
        
    else:
        raise ValueError(f"Base {a} no válida")

    return qc.to_gate().control()

def circuito_shor(N, a):
    '''
    Esta funcion crea el circuito que genera las mediciones de la c en el algoritmo de Shor

    Args:
        N (int): Modulo de la exponencial modular
        a (int): Base de la exponencial modular

    Returns:
        QuantumCircuit: Circuito cuantica que calcula que genera las mediciones del algoritmo de shor
    '''
    # Para N=15 usamos 8 qubits de conteo (precisión) y 4 auxiliares
    n_count = 8 
    n_aux = 4
    qc = QuantumCircuit(n_count + n_aux, n_count)

    # 1. Inicialización
    qc.h(range(n_count))    # Registro de arriba en superposición
    qc.x(n_count)           # El registro de abajo empieza en |1>

    # 2. Exponencial Modular
    # Aplicamos la puerta controlada 'n_count' veces
    puerta_U = exponencial_modular_15(a)
    for q in range(n_count):
        # Aplicamos la puerta U^(2^q)
        # (En este ejemplo simplificado aplicamos la misma, pero se escala)
        qc.append(puerta_U, [q] + list(range(n_count, n_count + n_aux)))

    # 3. QFT Inversa
    iqft = QFT(num_qubits=n_count, inverse=True).to_gate()
    qc.append(iqft, range(n_count))

    # 4. Medida
    qc.measure(range(n_count), range(n_count))
    
    return qc

def ejecutar_en_simulador(qc, optimizacion=1):
    '''
    Esta función usa un sampler para generar las mediciones de un circuito cuantico

    Args:
        qc (QuantumCircuit): Circuito cuyas mediciones se quieren obtener
        optimizacion (int): Nivel al que se optimizan los circuitos generados para samplear. Puede ser 0,1,2,3, de base es 1

    Returns:
        dict: diccionario en el que se indica el numero de veces que se ha medido cada combinación de bits
    '''
    backend = AerSimulator()
    pm = generate_preset_pass_manager(optimization_level= optimizacion, backend=backend)
    isa_circuit = pm.run(qc)

    sampler = SamplerV2()
    result = sampler.run([isa_circuit]).result()

    counts = result[0].data.c.get_counts() # .c es como llama qiskit al registro de los bits clasicos por defecto, aunque hay que tener cuidado con esto
    return counts