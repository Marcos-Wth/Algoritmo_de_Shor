import math
from fractions import Fraction

class Transformaciones():
    '''
    Esta clase contiene la lógica para a partir de los valores del problema y la 'c' devuelta por la QFT; tratar de calcular los dos factores primos de 'N'.
    '''
    def __init__(self, N, nQ, a, c):
        '''
        Almacena los valores necesarios para obtener los factores primos del módulo.

        Args:
            N (int): Módulo, cuyos factores primos se desea obtener
            nQ (int): Número de qubits que se dedican a la entrada de la exponencial modular
            a (int): Base escogida de la exponencial modular
            c (int): Valor devuelto por la puerta QFT
        '''
    
        self.a=a
        self.N=N
        self.nQ=nQ
        self.c=c
        self.H=2 ** nQ


    def fracciones_continuas(self):
        '''
        Función que genera aproximaciones a la fracción c/H, y con la forma P/Q; después comprueba si Q cumple las condiciones para ser el periodo.

        Returns:
            Q: Entero que es potencialmente el periodo de la exponencial modular.
        '''

        fraccion=Fraction(self.c, self.H)  # Utilizo los números reales en forma de fracción, que es más conveniente
        resto=fraccion
        coeficientes = []
        p = [0, 1]
        q = [1, 0]

        while (True):
            try:
                a=resto.numerator //resto.denominator
            except ZeroDivisionError:
                print('División por 0 en la fracción')
                break

            coeficientes.append(a)
            n = len(coeficientes) - 1
            
            p_n = a * p[n + 1] + p[n]
            q_n = a * q[n + 1] + q[n]
            
            p.append(p_n)
            q.append(q_n)
            
            aproximacion = Fraction(p_n, q_n)
            
            Q = q_n 

            if (pow(self.a,Q,self.N)==1):
                return Q
            
            if aproximacion == fraccion:
                return -1

            parte_fraccionaria = resto - a
            
            if parte_fraccionaria.numerator == 0:
                break
                
            resto = 1 / parte_fraccionaria


    def condiciones_periodo(self, r):
        '''
        Función que comprueba si el periodo cumple con los criterios que debe de cumplir.

        Args:
            r (int): Posible periodo que ha de ponerse a prueba.

        Returns:
            boolean: 'True' si las cumple o 'False' si no lo hace.
        '''

        # Primera condición, 'r' debe de ser par
        if (r%2!=0):
            return False
        
        # Segunda condición, 'r' no puede ser trivial
        if ((r==0) or (r==1) or (r==self.N)):
            return False
        
        # Tercera condición : a^(r/2) != -1 (Mod N)
        if ((pow(self.a,(r//2),(self.N)))== self.N-1):
            return False

        return True
    

    def calcular_primos(self,r):
        '''
        Función que calcula los dos factores primos de N.

        Args:
            r (int): Periodo.

        Returns:
            p q (int): Los dos primos
        '''

        num=self.a**(r//2)

        # primer primo
        p = math.gcd(num-1, self.N)

        # segundo primo
        q = math.gcd(num+1, self.N)

        return p,q
    

    def verificar_primos(self,p,q):
        '''
        Función que comprueba si los primos obtenidos son correctos.

        Args:
            p (int): 1º primo.
            q (int): 2º primo.

        Returns:
            boolean: 'True' si son correctos, 'False' si no.
        '''

        trivial=False
        if (p==1) or (p==self.N):
            trivial=True


        if (q==1) or (q==self.N):
            trivial=True

        if trivial:
            return False
        
        num=p*q
        if num==self.N:
            return True
        else:
            return False


    def obtener_primos(self):
        """
        Calcula los factores primos de N usando el periodo extraído de la QFT.
        """
        # 1. Intentar extraer el periodo r
        r = self.fracciones_continuas()
        
        if r == -1:
            codigo= f"No se ha encontrado ninguna aproximación válida para r"
            return [False, -1, -1, codigo, r]

        # 2. Verificar si r es útil para la factorización
        if not self.condiciones_periodo(r):
            codigo= f"ERROR: El periodo r = {r} no es apto para factorizar N"
            return [False, -1, -1, codigo, r]
    
        # 3. Calcular candidatos a primos
        p, q = self.calcular_primos(r)

        # 4. Verificación final
        if self.verificar_primos(p, q):
            codigo = f"PRIMOS ENCONTRADOS: N={self.N} -> p={p}, q={q} (periodo={r})"
            return [True, p, q, codigo, r]
        else:
            codigo = f"ERROR: Factores p={p}, q={q} no son válidos para N={self.N}"
            return [False, p, q, codigo, r]