import sys
import os
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_padre = os.path.abspath(os.path.join(ruta_actual, '..'))
if ruta_padre not in sys.path:
    sys.path.append(ruta_padre)

from modulos.Transformaciones import Transformaciones
from proyecto_qiskit import Cuantica

import math
import random


class Shor:
    '''
    Esta clase contiene la lógica para a partir de 'N' obtener los factores primos de este.
    '''

    def __init__(self, N=15, nQ=10, optimizacion=1, repeticiones=4096):
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

        # 1. Creamos el circuito pasándole los atributos de la clase
        qc = Cuantica.circuito_shor(self.N, self.nQ, self.a)
        
        # Control de error: circuito_shor devuelve 0 si n >= nQ
        if qc == 0:
            return 0

        # 2. Obtenemos las mediciones usando el simulador
        counts = Cuantica.ejecutar_en_simulador(qc, self.optimizacion, self.repeticiones)

        # 3. Filtramos el diccionario para obtener el resultado decodificado más repetido
        c = Cuantica.resultado_mayor_indice(counts)

        return c
   



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
        print('\nIniciando Algoritmo de Shor')
        correcto = False
        bases = 0

        while not correcto:
            self.establecer_base()
            bases = bases +1
            if (bases >= self.N - 2 or self.a == -1):
                print("Se han agotado las bases posibles.")
                break
                
            print(f'Probando base a = {self.a}')

            c = self.obtener_c()
            print(f'Valor c medido en el circuito cuantico: {c}')

            sol = self.calcular_factores(c)
            correcto = sol[0]

        print('PROCESO FINALIZADO.')
        p = sol[1]
        q = sol[2]
        r = sol[4]
        print(sol[3])
        return [p, q, c, r] # Devuelvo los valores para luego cuando haga el programa con interfaz

   
# Pruebas

prueba= Shor(15, 8, 3, 10000)
prueba.shor()