from flask import Flask, request, jsonify
from flask_cors import CORS
from logic import *
import random
from itertools import permutations, combinations

app = Flask(__name__)
CORS(app)

class JuegoMastermind:
    def __init__(self):
        self.num_elementos = None
        self.colores = []
        self.posiciones = []
        self.symbols = []
        self.conocimiento = And()
        self.universos = []
        self.historial = []
        self.intentos = 0
        self.mostrar_debug = True  # Bandera para controlar la salida de depuración

    def configurar_juego(self, num_elementos):
        self.num_elementos = num_elementos
        self.colores = [f"c{i}" for i in range(num_elementos)]
        self.posiciones = [f"p{i}" for i in range(num_elementos)]
        self.symbols = [Symbol(f"p{i}c{j}") for i in range(num_elementos) for j in range(num_elementos)]
        self._inicializar_conocimiento()
        self._generar_universos()
        self.historial = []
        self.intentos = -1
        
        if self.mostrar_debug:
            print("\n=== CONFIGURACIÓN INICIAL ===")
            print(f"Colores: {self.colores}")
            print(f"Posiciones: {self.posiciones}")
            print(f"Total universos posibles: {len(self.universos)}")
            self._imprimir_universos()
        
        return {"status": "success", "message": f"Juego configurado con {num_elementos} colores"}

    def _imprimir_universos(self):
        """Muestra los universos actuales en la consola"""
        print("\nUniversos posibles:")
        for i, universo in enumerate(self.universos):
            print(f"{i+1}. {universo}")
        print(f"Total: {len(self.universos)} universos")

    def manejar_respuesta(self, propuesta, aciertos):
        if aciertos == self.num_elementos:
            # Asegúrate que esta parte esté EXACTAMENTE así
            return {
                "status": "ganado",  # Debe ser "ganado" exactamente
                "combinacion": propuesta,
                "mensaje": "¡Combinación correcta encontrada!"
            }

    def _inicializar_conocimiento(self):
        self.conocimiento = And()
        
        # Cada color aparece exactamente una vez
        for colo in self.colores:
            self.conocimiento.add(Or(*[Symbol(f"p{i}{colo}") for i in range(self.num_elementos)]))
        
        # Restricciones de unicidad
        for colo in self.colores:
            for i in range(self.num_elementos):
                for j in range(self.num_elementos):
                    if i != j:
                        self.conocimiento.add(
                            Implication(Symbol(f"p{i}{colo}"), Not(Symbol(f"p{j}{colo}"))))

        for i in range(self.num_elementos):
            for colo in self.colores:
                for colo2 in self.colores:
                    if colo != colo2:
                        self.conocimiento.add(
                            Implication(Symbol(f"p{i}{colo}"), Not(Symbol(f"p{i}{colo2}"))))

    def _generar_universos(self):
        self.universos = []
        for perm in permutations(self.colores):
            self.universos.append([f"p{i}{perm[i]}" for i in range(self.num_elementos)])

    def _filtrar_universos(self):
        universos_validos = []
        for universo in self.universos:
            if not model_check(self.conocimiento, Not(And(*[Symbol(v) for v in universo]))):
                universos_validos.append(universo)
        return universos_validos

    def generar_propuesta(self):
        universos_validos = self._filtrar_universos()
        
        if self.mostrar_debug:
            print(f"\n=== INTENTO {self.intentos + 1} ===")
            print(f"Universos válidos: {len(universos_validos)}")
            if len(universos_validos) <= 10:  # Solo mostrar si son pocos
                for i, u in enumerate(universos_validos):
                    print(f"{i+1}. {u}")
        
        if not universos_validos:
            if self.mostrar_debug:
                print("¡No hay más universos válidos!")
            return None
        
        propuesta = random.choice(universos_validos)
        self.intentos += 1
        self.historial.append({
            "intento": self.intentos,
            "propuesta": propuesta.copy(),
            "universos_restantes": len(universos_validos)
        })
        
        if self.mostrar_debug:
            print(f"\nPropuesta generada: {propuesta}")
        
        return propuesta

    def procesar_respuesta(self, propuesta, aciertos):
        if self.mostrar_debug:
            print(f"\nRespuesta recibida: {aciertos} aciertos")
        
        if aciertos == self.num_elementos:
            if self.mostrar_debug:
                print("¡Solución correcta encontrada!")
            return {"status": "ganado", "combinacion": propuesta}
        
        if aciertos == 0:
            if self.mostrar_debug:
                print("Descartando todas las variables de la propuesta")
            for simbolo in propuesta:
                self.conocimiento.add(Not(Symbol(simbolo)))
            return {"status": "continua", "message": f"Descartadas {len(propuesta)} variables"}
        
        # Lógica para aciertos parciales
        if self.mostrar_debug:
            print(f"Procesando {aciertos} aciertos parciales...")
        
        combinaciones_correctas = list(combinations(propuesta, aciertos))
        opciones_disjuntas = []
        
        for combinacion in combinaciones_correctas:
            falsas = [v for v in propuesta if v not in combinacion]
            opciones = [Symbol(v) for v in combinacion] + [Not(Symbol(v)) for v in falsas]
            opciones_disjuntas.append(And(*opciones))
        
        self.conocimiento.add(Or(*opciones_disjuntas))
        
        # Mostrar cómo queda el conocimiento
        if self.mostrar_debug:
            print("\nConocimiento actualizado:")
            universos_validos = self._filtrar_universos()
            print(f"Universos restantes válidos: {len(universos_validos)}")
            if len(universos_validos) <= 10:
                for i, u in enumerate(universos_validos):
                    print(f"{i+1}. {u}")
        
        return {"status": "continua", "message": f"Actualizado con {aciertos} aciertos"}

juego = JuegoMastermind()

# Endpoints (igual que antes)
@app.route('/iniciar', methods=['POST'])
def iniciar_juego():
    data = request.json
    num_elementos = data.get('num_elementos', 4)
    return jsonify(juego.configurar_juego(num_elementos))

@app.route('/propuesta', methods=['GET'])
def obtener_propuesta():
    propuesta = juego.generar_propuesta()
    if not propuesta:
        return jsonify({"error": "No hay más combinaciones posibles"}), 400
    return jsonify({
        "propuesta": propuesta,
        "intento_actual": juego.intentos,
        "universos_restantes": juego.historial[-1]["universos_restantes"] if juego.historial else 0
    })

@app.route('/responder', methods=['POST'])
def responder():
    data = request.json
    resultado = juego.procesar_respuesta(data['propuesta'], data['aciertos'])
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