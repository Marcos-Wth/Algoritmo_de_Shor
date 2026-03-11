from Transformaciones import Transformaciones

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
        self.a=1    # utilizar esta variable, para definir la base, ya sea sumandole 1 cada vez que falle, o algo por el estilo para que no se repitan nunca

    def modificar_base(self):
        '''
        Esta función se encargará de modificar la base (a) de la exponencial modular.

        Args:
            N (int): Número a factorizar.

        Returns:
            a (int): Base a utilizar para la exponencial modular.
        '''
        self.a = self.a+1 # Sumo 1 cada vez que se llama a esta función, así me aseguro que no se repiten nunca

    def obtener_c(self):
        '''
        Esta función me devuelve la aproximación 'c' al múltiplo del periodo, proveniente de la QFT (Simulando el proceso en este caso).

        Args:
            N (int): Número a factorizar.
            a (int): Base de la exponencial modular.

        Returns:
            c (double): Valor de salida de la QFT.
        '''
        return 64 # Valor puesto a mano para simular la intervención de una librería

    def calcular_factores(self, c):
        '''
        Esta función obtiene los factores primos de 'N' llamando a la función 'obtener_primos' de la clase 'Transformaciones'.
        
        
        '''
        return Transformaciones.obtener_primos(self.N, self.nQ, self.a, c)

    def shor(self):
        '''
        Esta función llama al resto, y se encarga de que el proceso se repita hasta que los primos son correctos, primero haciendo que se repita la obtención de 'c',
        y si eso no funciona en un par de ocasiones, hará que se repita la elección de la base directamente.
        '''
        print('\n')
        correcto=False

        while(not correcto):
            # Modifico la base para la nueva iteración.
            self.modificar_base()
            print('Ejecutando el algoritmo con base = ',self.a)

            # Al modificar la base, también debo de obtener otra 'c'.
            c= self.obtener_c()
            print('La c obtenida es = ', c)

            # Trato de calcular los primos.
            sol= self.calcular_factores(c)
            print(sol[3])
            correcto=sol[0]
            print('\n')

        print('Fin del algoritmo')

   
# Pruebas

prueba= Shor(15,8,7)
prueba.shor()