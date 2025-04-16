# Importación de librerías necesarias
from flask import Flask, request, jsonify  # Para crear la API REST
from flask_cors import CORS  # Para manejar CORS (comunicación entre frontend y backend)
from logic import *  # Importa la lógica del juego (Symbol, And, Or, etc.)
import random  # Para generar propuestas aleatorias
from itertools import permutations, combinations  # Para manejar combinaciones de colores

# Configuración inicial de Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

class JuegoAdivinanza:
    def __init__(self):
        """Inicializa todas las variables del juego"""
        self.num_elementos = 0  # Número de colores/posiciones
        self.colores = []  # Lista de colores disponibles (ej. ['0', '1', '2'])
        self.posiciones = []  # Lista de posiciones (ej. ['p0', 'p1', 'p2'])
        self.universos_posibles = []  # Todas las permutaciones posibles de colores
        self.variables_descartadas = set()  # Variables que sabemos son incorrectas
        self.propuestas_previas = set()  # Propuestas que ya hemos hecho
        self.intentos = 0  # Contador de intentos
        self.historial = []  # Registro de todos los intentos

    def configurar_juego(self, num_elementos):
        """Prepara el juego con un número específico de colores/posiciones"""
        self.num_elementos = num_elementos
        self.colores = [str(i) for i in range(num_elementos)]  # Crea colores como strings
        self.posiciones = [f"p{i}" for i in range(num_elementos)]  # Crea posiciones p0, p1, etc.
        # Genera todas las permutaciones posibles de colores
        self.universos_posibles = list(permutations(self.colores))
        # Reinicia el estado del juego
        self.variables_descartadas = set()
        self.propuestas_previas = set()
        self.intentos = 0
        self.historial = []
        return True

    def permutacion_a_variables(self, perm):
        """Convierte una permutación de colores al formato pXcY para el frontend
        Ejemplo: [1, 0, 2] -> ['p0c1', 'p1c0', 'p2c2']"""
        return [f"p{i}c{perm[i]}" for i in range(self.num_elementos)]

    def generar_propuesta(self):
        """Genera una nueva propuesta válida basada en el conocimiento actual"""
        # Filtra permutaciones que no contengan variables descartadas
        universos_validos = [
            perm for perm in self.universos_posibles
            if not any(var in self.variables_descartadas 
                     for var in self.permutacion_a_variables(perm))
            and ' '.join(self.permutacion_a_variables(perm)) not in self.propuestas_previas
        ]
        
        if not universos_validos:
            return None  # No hay más combinaciones posibles
        
        # Elige una permutación aleatoria de las válidas
        universo_actual = random.choice(universos_validos)
        propuesta = self.permutacion_a_variables(universo_actual)
        # Registra esta propuesta para no repetirla
        self.propuestas_previas.add(' '.join(propuesta))
        return propuesta

    def manejar_respuesta(self, propuesta, aciertos):
        """Procesa la respuesta del usuario a una propuesta"""
        if aciertos == self.num_elementos:
            # ¡Solución correcta!
            return {"status": "Ganado", "combinacion": propuesta}
        
        elif aciertos == 0:
            # Todas las variables en la propuesta son incorrectas
            self.variables_descartadas.update(propuesta)
            return {"status": "Continua", "mensaje": f"Descartadas {self.num_elementos} variables"}
        
        else:
            # Algunas correctas, otras no - lógica más compleja
            self.manejar_aciertos_parciales(propuesta, aciertos)
            return {"status": "Continua", "mensaje": f"Actualizado con {aciertos} aciertos"}

    def manejar_aciertos_parciales(self, propuesta, aciertos):
        """Lógica para cuando algunos elementos son correctos pero otros no"""
        # Genera todas las combinaciones posibles de aciertos
        todas_combinaciones = list(combinations(propuesta, aciertos))
        variables_incorrectas = set(propuesta)
        
        # Encuentra variables que deben ser incorrectas
        for combo in todas_combinaciones:
            variables_incorrectas.intersection_update({v for v in propuesta if v not in combo})
        
        # Actualiza las variables descartadas
        if variables_incorrectas:
            self.variables_descartadas.update(variables_incorrectas)
        
        # Filtra los universos posibles eliminando los que contengan variables descartadas
        self.universos_posibles[:] = [
            perm for perm in self.universos_posibles
            if not any(f"p{i}c{perm[i]}" in self.variables_descartadas
                     for i in range(self.num_elementos))
        ]

# Instancia global del juego
juego = JuegoAdivinanza()

# Endpoint para iniciar un nuevo juego
@app.route('/iniciar', methods=['POST'])
def iniciar_juego():
    data = request.json  # Obtiene datos del frontend
    num_elementos = data.get('num_elementos', 4)  # Valor por defecto: 4
    juego.configurar_juego(num_elementos)
    return jsonify({
        "status": "Juego iniciado",
        "num_elementos": num_elementos,
        "message": f"Juego configurado con {num_elementos} colores"
    })

# Endpoint para obtener una nueva propuesta
@app.route('/propuesta', methods=['GET'])
def obtener_propuesta():
    propuesta = juego.generar_propuesta()
    if not propuesta:
        return jsonify({"error": "No hay más combinaciones"}), 400  # Error HTTP 400
    
    juego.intentos += 1
    # Registra el intento en el historial
    juego.historial.append({
        "intento": juego.intentos,
        "propuesta": propuesta
    })
    
    return jsonify({
        "propuesta": propuesta,  # Lista de variables pXcY
        "intento_actual": juego.intentos
    })

# Endpoint para enviar la respuesta del usuario
@app.route('/responder', methods=['POST'])
def responder():
    data = request.json
    # Procesa la respuesta y obtiene el resultado
    resultado = juego.manejar_respuesta(data['propuesta'], data['aciertos'])
    resultado["historial"] = juego.historial  # Incluye el historial completo
    return jsonify(resultado)

# Endpoint para consultar el historial
@app.route('/historial', methods=['GET'])
def obtener_historial():
    return jsonify({
        "historial": juego.historial,  # Todos los intentos
        "total_intentos": juego.intentos  # Número total de intentos
    })

# Punto de entrada para ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Ejecuta en modo debug en puerto 5000