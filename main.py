import sys
import math
from qiskit_code.Shor import Shor 


def calcular_qubits(N):
    n = math.ceil(math.log2(N))
    nQ = 2 * n 
    return nQ

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error. Uso: python main.py <N>")
        sys.exit(1)

    try:
        N = int(sys.argv[1])
        if N < 3: raise ValueError
    except ValueError:
        print("Por favor, introduce un número entero mayor que 2.")
        sys.exit(1)

    nQ = calcular_qubits(N)
    
    print("HOLA QUE TAL ME HE INICIADO Y ESO") # DEBUG
    instancia_shor = Shor(N, nQ, 3, 1024)
    instancia_shor.shor()
