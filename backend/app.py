from flask import Flask, request, jsonify
from flask_cors import CORS
from logic import *
import random
from itertools import permutations, combinations

app = Flask(__name__)
CORS(app)

class JuegoAdivinanza:
    def __init__(self):
        self.num_elementos = 0
        self.colores = []
        self.posiciones = []
        self.universos_posibles = []
        self.variables_descartadas = set()
        self.propuestas_previas = set()
        self.intentos = 0
        self.historial = []

    def configurar_juego(self, num_elementos):
        self.num_elementos = num_elementos
        self.colores = [str(i) for i in range(num_elementos)]
        self.posiciones = [f"p{i}" for i in range(num_elementos)]
        self.universos_posibles = list(permutations(self.colores))
        self.variables_descartadas = set()
        self.propuestas_previas = set()
        self.intentos = 0
        self.historial = []
        return True

    def permutacion_a_variables(self, perm):
        """Formato p0c0 para compatibilidad con el frontend"""
        return [f"p{i}c{perm[i]}" for i in range(self.num_elementos)]

    def generar_propuesta(self):
        universos_validos = [
            perm for perm in self.universos_posibles
            if not any(var in self.variables_descartadas 
                     for var in self.permutacion_a_variables(perm))
            and ' '.join(self.permutacion_a_variables(perm)) not in self.propuestas_previas
        ]
        
        if not universos_validos:
            return None
        
        universo_actual = random.choice(universos_validos)
        propuesta = self.permutacion_a_variables(universo_actual)
        self.propuestas_previas.add(' '.join(propuesta))
        return propuesta

    def manejar_respuesta(self, propuesta, aciertos):
        if aciertos == self.num_elementos:
            return {"status": "Ganado", "combinacion": propuesta}
        
        elif aciertos == 0:
            self.variables_descartadas.update(propuesta)
            return {"status": "Continua", "mensaje": f"Descartadas {self.num_elementos} variables"}
        
        else:
            self.manejar_aciertos_parciales(propuesta, aciertos)
            return {"status": "Continua", "mensaje": f"Actualizado con {aciertos} aciertos"}

    def manejar_aciertos_parciales(self, propuesta, aciertos):
        todas_combinaciones = list(combinations(propuesta, aciertos))
        variables_incorrectas = set(propuesta)
        
        for combo in todas_combinaciones:
            variables_incorrectas.intersection_update({v for v in propuesta if v not in combo})
        
        if variables_incorrectas:
            self.variables_descartadas.update(variables_incorrectas)
        
        self.universos_posibles[:] = [
            perm for perm in self.universos_posibles
            if not any(f"p{i}c{perm[i]}" in self.variables_descartadas
                     for i in range(self.num_elementos))
        ]

juego = JuegoAdivinanza()

@app.route('/iniciar', methods=['POST'])
def iniciar_juego():
    data = request.json
    num_elementos = data.get('num_elementos', 4)
    juego.configurar_juego(num_elementos)
    return jsonify({
        "status": "Juego iniciado",
        "num_elementos": num_elementos,
        "message": f"Juego configurado con {num_elementos} colores"
    })

@app.route('/propuesta', methods=['GET'])
def obtener_propuesta():
    propuesta = juego.generar_propuesta()
    if not propuesta:
        return jsonify({"error": "No hay más combinaciones"}), 400
    
    juego.intentos += 1
    juego.historial.append({
        "intento": juego.intentos,
        "propuesta": propuesta
    })
    
    return jsonify({
        "propuesta": propuesta,
        "intento_actual": juego.intentos
    })

@app.route('/responder', methods=['POST'])
def responder():
    data = request.json
    resultado = juego.manejar_respuesta(data['propuesta'], data['aciertos'])
    resultado["historial"] = juego.historial
    return jsonify(resultado)

@app.route('/historial', methods=['GET'])
def obtener_historial():
    return jsonify({
        "historial": juego.historial,
        "total_intentos": juego.intentos
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)