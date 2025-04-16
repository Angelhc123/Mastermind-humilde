from logic import *  # Importa todas las clases lógicas (Symbol, And, Or, Implication, etc.)
import random  # Para generar elecciones aleatorias
from itertools import permutations, combinations  # Para generar permutaciones y combinaciones

class JuegoAdivinanza:
    def __init__(self):
        """Inicializa todas las variables necesarias para el juego"""
        self.num_elementos = 0  # Número de colores/posiciones
        self.colores = []  # Lista de colores (ej. ['0', '1', '2', '3'])
        self.posiciones = []  # Lista de posiciones (ej. ['p0', 'p1', 'p2', 'p3'])
        self.universos_posibles = []  # Todas las permutaciones posibles iniciales
        self.variables_descartadas = set()  # Variables que sabemos son incorrectas
        self.propuestas_previas = set()  # Propuestas ya mostradas al usuario
        self.intentos = 0  # Contador de intentos

    def configurar_juego(self):
        """Solicita la configuración inicial al usuario y prepara las estructuras de datos"""
        try:
            # Solicita el número de elementos (colores/posiciones)
            self.num_elementos = int(input("Introduce la cantidad de colores y posiciones: "))
            if self.num_elementos <= 0:
                raise ValueError("El número debe ser positivo")
            
            # Genera las listas de colores y posiciones
            self.colores = [str(i) for i in range(self.num_elementos)]
            self.posiciones = [f"p{i}" for i in range(self.num_elementos)]
            
            # Genera todas las permutaciones posibles iniciales
            self.universos_posibles = list(permutations(self.colores))
            
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            return False
        return True

    def permutacion_a_variables(self, perm):
        """Convierte una permutación a lista de variables (ej. ('0','1','2') -> ['p00', 'p11', 'p22'])"""
        return [f"p{i}{perm[i]}" for i in range(self.num_elementos)]

    def generar_propuesta(self):
        """Genera una nueva propuesta válida que cumpla con las restricciones actuales"""
        # Filtra universos que no contengan variables descartadas y no sean propuestas previas
        universos_validos = [
            perm for perm in self.universos_posibles
            if not any(var in self.variables_descartadas 
                     for var in self.permutacion_a_variables(perm))
            and ' '.join(self.permutacion_a_variables(perm)) not in self.propuestas_previas
        ]
        
        # Si no hay universos válidos, muestra mensaje de error
        if not universos_validos:
            print("\n❌ No hay más combinaciones posibles.")
            print("La solución debería ser:", " ".join(f"p{i}{i}" for i in range(self.num_elementos)))
            return None
        
        # Selecciona un universo al azar de los válidos
        universo_actual = random.choice(universos_validos)
        propuesta = self.permutacion_a_variables(universo_actual)
        
        # Registra la propuesta para no repetirla
        self.propuestas_previas.add(' '.join(propuesta))
        return propuesta

    def manejar_respuesta(self, propuesta, aciertos):
        """
        Procesa la respuesta del usuario y actualiza el conocimiento del juego
        Retorna True si se adivinó la solución, False en caso contrario
        """
        # Caso 1: Todas las posiciones son correctas
        if aciertos == self.num_elementos:
            self.validar_solucion_final(propuesta)
            return True
        
        # Caso 2: Ninguna posición es correcta
        elif aciertos == 0:
            self.variables_descartadas.update(propuesta)
            print(f"Descartadas {self.num_elementos} variables incorrectas.")
        
        # Caso 3: Algunas posiciones son correctas (pero no todas)
        else:
            self.manejar_aciertos_parciales(propuesta, aciertos)
        
        return False

    def validar_solucion_final(self, propuesta):
        """Valida la solución final usando model checking"""
        print("\nValidando solución con model checking...")
        
        conocimiento = And()  # Crea una base de conocimiento
        
        # Regla 1: Cada color debe aparecer exactamente una vez
        for c in self.colores:
            conocimiento.add(Or(*[Symbol(f"p{p}{c}") for p in range(self.num_elementos)]))
        
        # Regla 2: Restricciones de exclusividad
        for p in range(self.num_elementos):
            for c in self.colores:
                # Un color no puede estar en dos posiciones diferentes
                for other_p in range(self.num_elementos):
                    if other_p != p:
                        conocimiento.add(Implication(Symbol(f"p{p}{c}"), Not(Symbol(f"p{other_p}{c}"))))
                
                # Una posición no puede tener dos colores diferentes
                for other_c in self.colores:
                    if other_c != c:
                        conocimiento.add(Implication(Symbol(f"p{p}{c}"), Not(Symbol(f"p{p}{other_c}"))))
        
        # Añade todas las variables que sabemos son incorrectas
        for var in self.variables_descartadas:
            conocimiento.add(Not(Symbol(var)))
        
        # Crea la consulta para validar la solución propuesta
        query = And(*[Symbol(var) for var in propuesta])
        
        # Realiza la validación
        if model_check(conocimiento, query):
            print("✅ ¡Solución correcta validada!")
            print("Combinación ganadora:", " ".join(propuesta))
        else:
            print("❌ Validación fallida. Esto no debería ocurrir.")

    def manejar_aciertos_parciales(self, propuesta, aciertos):
        """Maneja el caso cuando algunas posiciones son correctas pero no todas"""
        # Genera todas las combinaciones posibles de aciertos
        todas_combinaciones = list(combinations(propuesta, aciertos))
        variables_incorrectas = set(propuesta)  # Inicialmente asumimos que todas son incorrectas
        
        # Encuentra variables que son incorrectas en TODAS las combinaciones posibles
        for combo in todas_combinaciones:
            variables_incorrectas.intersection_update({v for v in propuesta if v not in combo})
        
        # Actualiza las variables descartadas
        if variables_incorrectas:
            self.variables_descartadas.update(variables_incorrectas)
            print(f"Descartadas {len(variables_incorrectas)} variables incorrectas.")
        
        # Actualiza los universos posibles eliminando aquellos con variables descartadas
        self.universos_posibles[:] = [
            perm for perm in self.universos_posibles
            if not any(f"p{i}{perm[i]}" in self.variables_descartadas 
                     for i in range(self.num_elementos))
        ]

    def jugar(self):
        """Método principal que ejecuta el juego"""
        if not self.configurar_juego():  # Configuración inicial
            return
        
        # Bucle principal del juego
        while True:
            self.intentos += 1
            propuesta = self.generar_propuesta()  # Genera nueva propuesta
            
            if not propuesta:  # Si no hay propuesta válida, termina
                break
            
            # Muestra la propuesta actual
            print(f"\nIntento #{self.intentos}")
            print("Propuesta:", " ".join(propuesta))
            
            # Solicita y valida la respuesta del usuario
            while True:
                try:
                    aciertos = int(input("¿Cuántas son correctas? "))
                    if 0 <= aciertos <= self.num_elementos:
                        break
                    print(f"Ingresa un número entre 0 y {self.num_elementos}")
                except ValueError:
                    print("¡Entrada inválida!")
            
            # Procesa la respuesta y verifica si terminó el juego
            if self.manejar_respuesta(propuesta, aciertos):
                break

if __name__ == "__main__":
    # Punto de entrada del programa
    juego = JuegoAdivinanza()
    juego.jugar()