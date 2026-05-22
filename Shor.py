import sys
import os
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_padre = os.path.abspath(os.path.join(ruta_actual, '..'))
if ruta_padre not in sys.path:
    sys.path.append(ruta_padre)

from modulos.Transformaciones import Transformaciones
import qiskit_code
import qsimov_code
from collections import Counter
import math
import random


class Shor:
    '''
    Esta clase contiene la lógica para a partir de 'N' obtener los factores primos de este.
    '''

    def __init__(self, N=15, nQ=10, optimizacion=1, repeticiones=4096, backend="qiskit"):
        '''
        Almacena el número cuyos factores primos se desea obtener, 'N', así como una variable para llevar a cabo el control de las bases.

        Args:
            N (int): Número a factorizar. De base es 15
            nQ (int): Número de qubits que se dedican a la entrada de la exponencial modular. De base es 10
            optimizacion (int): Nivel de optimizacion que se aplicara al circuito cuantico
            repeticiones (int): Numero de veces que se ejecutara el circuito cuantico con cada base
        '''
        self.N=N
        self.nQ=nQ
        self.a = 0
        self.optimizacion = optimizacion
        self.repeticiones = repeticiones
        self.backend = backend.lower()

        self.basesUsadas = set()
        self.establecer_base()


    def establecer_base(self):
        '''
        Esta función establece la base 'a' de la exponencial modular y la almacena en el atributo de clase
        '''
        i=0
        base = random.randint(2,self.N-1)

        while ((math.gcd(base, self.N) != 1) or base in self.basesUsadas):
            self.basesUsadas.add(base)
            base = random.randint(2,self.N-1)
            i=i+1
            if (i>self.N):
                self.a = -1
                return
        
        self.a = base
        self.basesUsadas.add(base)
        return

    def obtener_c(self):
        '''
        Usa Qiskit para crear un circuito, medir y obtener el valor 'c'.

        Returns:
            c (double): Valor de salida de la QFT decodificado.
        '''

        if self.backend == "qiskit":
            # Tu lógica actual de Qiskit
            qc_qiskit = qiskit_code.circuito_shor(self.N, self.nQ, self.a)
            if qc_qiskit == 0: return 0
            counts = qiskit_code.ejecutar_en_simulador(qc_qiskit, self.optimizacion, self.repeticiones)
            return qiskit_code.resultado_mayor_indice(counts)
            
        elif self.backend == "qsimov":
            

            resultados = []
            for _ in range(self.repeticiones):
                c = qsimov_code.circuito_shor(self.N, self.nQ, self.a)  
                if c is None:                                             
                    return 0
                resultados.append(c)
            
            c_mas_frecuente = Counter(resultados).most_common(1)[0][0]
            return int(c_mas_frecuente, 2)
    



    def calcular_factores(self, c):
        '''
        Esta función obtiene los factores primos de 'N' llamando a la función 'obtener_primos' de la clase 'Transformaciones'.

        Returns:
        Devuelve una tupla de 4 elementos: 1º boolean, 2º int (p), 3º int (q), 4º string (codigo)
        
        '''
        t = Transformaciones(self.N, self.nQ, self.a, c)
        return t.obtener_primos()

    def shor(self):
        '''
        Esta función llama al resto, y se encarga de que el proceso se repita hasta que los primos son correctos, primero haciendo que se repita la obtención de 'c',
        y si eso no funciona en un par de ocasiones, hará que se repita la elección de la base directamente.
        '''
        print(f'\nIniciando Algoritmo de Shor para N = {self.N} con {self.nQ} qubits')
        correcto = False
        bases = 0

        while not correcto:
            self.establecer_base()
            bases = bases +1
            if (bases >= self.N - 2 or self.a == -1):
                print("Se han agotado las bases posibles.")
                break
                
            print(f'Probando base a = {self.a}')

            try:
                c = self.obtener_c()
                print(f'Valor c medido en el circuito cuantico: {c}')
                sol = self.calcular_factores(c)
                correcto = sol[0]
            except Exception as e: 
                # Hacemos el control de errores un poco más genérico para que soporte ambos
                error_str = str(e).lower()
                if "not unitary" in error_str or "unitar" in error_str:
                    print(f"  Aviso: La base {self.a} dio un error de unitariedad. Saltando...")
                    continue
                else:
                    raise e 

        print('PROCESO FINALIZADO.')
        p = sol[1]
        q = sol[2]
        r = sol[4]
        if (sol[0]):
            print(sol[3])
        return [p, q, c, r]
