import sys
import math
from Shor import Shor


def calcular_qubits(N):
    n = math.ceil(math.log2(N))
    nQ = 2 * n 
    return nQ

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Error. Uso: python main.py <N>")
        sys.exit(1)

    try:
        N = int(sys.argv[1])
        if N < 3: raise ValueError
    except ValueError:
        print("N debe ser un número entero mayor que 2.")
        sys.exit(1)

    try:
        sim = str(sys.argv[2])
    except ValueError:
        print("El valor introducido no corresponde a ningun simulador")
    nQ = calcular_qubits(N)

    try:
        rep = int(sys.argv[3])
        if (rep < 1 or rep > 4096): raise ValueError
    except ValueError:
        print("En número de repeticiones debe ser mayor a o y menor que 4096")

    
    instancia_shor = Shor(N, nQ, 3, rep, sim)
    instancia_shor.shor()
