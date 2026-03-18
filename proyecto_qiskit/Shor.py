from modulos import Transformaciones
import math
import random

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import Sampler 

class Shor:
    '''
    Esta clase contiene la lógica para a partir de 'N' obtener los factores primos de este.
    '''

    def __init__(self, N, nQ):
        '''
        Almacena el número cuyos factores primos se desea obtener, 'N', así como una variable para llevar a cabo el control de las bases.

        Args:
            N (int): Número a factorizar.
            nQ (int): Número de qubits con los que va a trabajar la exponencial modular.
        '''

        self.N=N
        self.nQ=nQ
        self.a=2    # utilizar esta variable, para definir la base, ya sea sumandole 1 cada vez que falle, o algo por el estilo para que no se repitan nunca
        self.simulator = AerSimulator()

    def modificar_base(self):
        '''
        Esta función se encargará de modificar la base (a) de la exponencial modular.

        Args:
            N (int): Número a factorizar.

        Returns:
            a (int): Base a utilizar para la exponencial modular.
        '''
        self.a = self.a+1 # Sumo 1 cada vez que se llama a esta función, así me aseguro que no se repiten nunca

        # Compruebo que el mcd de la base y el modulo es 1
        while (math.gcd(self.a,self.N) != 1):
            self.a = self.a+1

    def obtener_c(self):
        '''
        Usa Qiskit para crear un circuito, medir y obtener el valor 'c'.

        Returns:
            c (double): Valor de salida de la QFT.
        '''
        bitsEntrada = self.N.bit_length() # Obtengo el numero de qubits necesarios para la exponencial modular
        circuito = QuantumCircuit(self.nQ + bitsEntrada, self.nQ)

        circuito.h(range(self.nQ)) # Aplico Hadamard al registro de la entrada

        circuito.x(self.nQ)

        qft = QFT(num_qubits=self.nQ, inverse=True).to_gate()
        circuito.append(qft, range(self.nQ))

        circuito.measure(range(self.nQ), range(self.nQ))

        sampler = Sampler() 
        job = sampler.run(circuito, shots=1)
        result = job.result()

        counts = result.quasi_dists[0]

        c = max(counts, key=counts.get)

        return c



    def calcular_factores(self, c):
        '''
        Esta función obtiene los factores primos de 'N' llamando a la función 'obtener_primos' de la clase 'Transformaciones'.
        
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

        while not correcto:
            self.modificar_base()
            if self.a >= self.N:
                print("Se han agotado las bases posibles.")
                break
                
            print(f'Probando base a = {self.a}')

            c = self.obtener_c()
            print(f'Valor c medido en el circuito: {c}')

            sol = self.calcular_factores(c)
            print(sol[3])
            correcto = sol[0]

        print('Proceso finalizado.')

   
# Pruebas

prueba= Shor(55, 10)
prueba.shor()