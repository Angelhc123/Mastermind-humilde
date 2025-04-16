from logic import *
import random
from itertools import *

# Entrada del usuario para el número de colores y posiciones
num_elementos = int(input("Introduce la cantidad de colores y posiciones: "))

# Generamos las listas de colores y posiciones
colores = [f"c{i}" for i in range(num_elementos)]
posiciones = [f"p{i}" for i in range(num_elementos)]

symbols = []

# Generamos las variables para cada color y posición
for i in range(num_elementos):
    for j in range(num_elementos):
        symbols.append(Symbol(f"p{i}c{j}"))

Conocimiento = And()

# Cada color aparece una vez
for colo in colores:
    lista_de_simbolos = [Symbol(f"p{i}{colo[-1]}") for i in range(num_elementos)]  # Corregido aquí
    Conocimiento.add(Or(*lista_de_simbolos))

# Un color no puede estar en dos posiciones a la vez
for colo in colores:
    for i in range(num_elementos):
        for j in range(num_elementos):
            if i != j:
                Conocimiento.add(
                    Implication(Symbol(f"p{i}{colo[-1]}"), Not(Symbol(f"p{j}{colo[-1]}"))))  # Corregido aquí

# Una posición solo puede tener un color
for i in range(num_elementos):
    for colo in colores:
        for colo2 in colores:
            if colo != colo2:
                Conocimiento.add(
                    Implication(Symbol(f"p{i}{colo[-1]}"), Not(Symbol(f"p{i}{colo2[-1]}"))))  # Corregido aquí

# Lista para almacenar variables negativas
variables_negativas = set()

# Ciclo para adivinar
intentos = 0
while True:
    intentos += 1

    # Generar combinaciones posibles
    universos_posibles = []
    
    for perm in permutations(colores):
        universo_valido = True
        universo = [f"p{i}{perm[i][-1]}" for i in range(num_elementos)]  # Corregido aquí
        
        for var in universo:
            if var in variables_negativas:
                universo_valido = False
                break
        
        if universo_valido:
            universos_posibles.append(universo)

    if not universos_posibles:
        print("No hay más combinaciones posibles. Terminando.")
        break

    propuesta = random.choice(universos_posibles)
    print(f"\nIntento #{intentos}")
    print("Propuesta del sistema:", propuesta)

    aciertos = int(input("¿Cuántas posiciones son correctas? "))

    if aciertos == num_elementos:
        print("✅ ¡El sistema adivinó la combinación correcta!")
        break
    elif aciertos == 0:
        print("❌ Ninguna posición es correcta.")
        for simbolo in propuesta:
            variables_negativas.add(simbolo)
            print(f"Descartada: {simbolo}")
    else:
        print(f"🟡 Hay {aciertos} posiciones correctas, pero no todas.")
        combinaciones_correctas = combinations(propuesta, aciertos)
        opciones = []
        
        todas_variables = set(propuesta)
        variables_posiblemente_correctas = set()
        
        for combinacion in combinaciones_correctas:
            correctas = combinacion
            falsas = [v for v in propuesta if v not in correctas]
            
            variables_posiblemente_correctas.update(correctas)
            
            for v in correctas:
                opciones.append(Symbol(v))
            for v in falsas:
                opciones.append(Not(Symbol(v)))
            
            print("Posible combinación:", " ".join(
                [f"Not({v})" if v in falsas else v for v in propuesta]))
        
        variables_definitivamente_falsas = todas_variables - variables_posiblemente_correctas
        
        for var in variables_definitivamente_falsas:
            variables_negativas.add(var)
            print(f"Descartada definitivamente: {var}")
        
        Conocimiento.add(Or(*opciones))