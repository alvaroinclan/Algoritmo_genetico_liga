

from __future__ import annotations # Para trabajar con anotaciones. Nos permiten añadir información sobre los tipos de datos esperados en 
# variables, parámetros de funciones y valores de retorno. Lo vimos en clase en los ejemplos de algoritmos geneticos.
import streamlit as st # Importamos streamlit 
import matplotlib.pyplot as plt # Para graficas, aunque al final no lo hemos utilizado 

from typing import List, Dict, Tuple # Para trabajar con tuplas(equipos_cat), listas(horarios, poblacion, jornada) y diccionarios(las utilizamos constantemente)
import random # Para hacer todo lo que tenga que ver con números aleatorios. Generar la población inicial, ...

import pandas as pd # para trabajar con tablas


## GENERAR JORNADA AL AZAR

# Funcion para generar la jornada
def emparejar_equipos(equipos):
    # Mezclamos la lista de forma aleatoria
    random.shuffle(equipos)
    
    # Creamos los partidos recorriendo la lista de dos en dos y los mostramos por pantalla  
    st.write("Jornada generada al azar:\n")
    for i in range(0, len(equipos), 2):
        st.write(f"Partido {int(i/2 +1)}: {equipos[i]} vs {equipos[i+1]}")

# Lista de equipos de la liga española de la temporada 25/26 
equipos_liga = [
    "FC Barcelona", "Real Madrid", "Villarreal CF", "Atlético de Madrid",
    "RCD Espanyol", "Real Betis", "RC Celta", "Athletic Club",
    "Elche CF", "Rayo Vallecano", "Real Sociedad", "Getafe CF",
    "Girona FC", "Sevilla FC", "CA Osasuna", "Deportivo Alavés",
    "RCD Mallorca", "Valencia CF", "Levante UD", "Real Oviedo"
]


st.title("Genera jornada al azar")
pulsador = st.button("Generar")

# Si pulsa el boton el usuario se genera la jornada
if pulsador == True:
    
    emparejar_equipos(equipos_liga)

## CREAR JORNADA CUSTOMIZADA

st.title("Genera una jornada customizada")


#Creamos una lista para guardar las selecciones actuales
seleccionados = []

# Generamos las 10 barras de selección con un bucle 
for i in range(1, 11):

    # Mostramos como opcion los equipos que no han sido seleccionados previamente
    opciones = [e for e in equipos_liga if e not in seleccionados]
    # De esta forma los equipos se eliminan para las siguiente iteraciones a media que se seleccionan

    # Mostramos la barra de selección
    partido = st.multiselect(
        f"Elige el partido {i}",
        options=opciones,
        max_selections=2, # Nos permite solo escoger dos equipos
        key=f"partido_{i}" # Esto para que no falle streamlit, tiene que ver con el session_state que vimos en clase. De esta forma estamos guardando 
        # los partidos en la session_state para luego utilizarlos en el algoritmo genetico 
    )
    
    # Añadimos los equipos seleccionados a la lista 
    seleccionados.extend(partido) # Es como append pero los añade elemento a elemento 

# Ahora vamos a utilizar la session_state para utilizar la selección 

# Convertimos la selección de Streamlit a índices para el algoritmo. En la selección los hemos guardado por nombres. 
jornada_seleccionada = []

# Recorremos los partidos de la jornada en st.session_state y guardamos los indices
for i in range(1, 11):
    partido_nombres = st.session_state[f"partido_{i}"]
    if len(partido_nombres) == 2:
        idx_local = equipos_liga.index(partido_nombres[0])
        idx_visitante = equipos_liga.index(partido_nombres[1])
        jornada_seleccionada.append((idx_local, idx_visitante, i))

# Observemos que esta forma de hacerlo nos obliga a seleccionar los partidos en orden. Es decir, emepzar con el 1 hasta llegar al 10.



## CÓDIGO DEL ALGORITMO GENÉTICO 


# Hemos hecho una serie de cambios:
# En la funcion random_individual para que haga combinaciones de horarios de la jornada seleccionada. 
# En la funcion init para meter por parametro la jornada seleccionada
# Las categorías de los equipos ya que antes lo hacíamos por índices y ahora lo hacemos diferentes para no depender del orden de seleccion de los equipos en la jornada.
# Ademas ahora utilizamos los equipos de la liga para que la visualizacion quede mejor. 
# También cambia la funcion formatear jornada(pasamos nombre del equipo en lugar de indice como antes) y la funcion mutate que no cambia ahora el orden de los equipos en el partido, es decir, solo cambia el horario. 
# El resto del código es igual 

# Ademas la funcion one pint crossover ya no tiene sentido porque no cambia nada al solo haber un padre, igual que la funcion tournament select, aunque estas dos funciones las he dejado tal como estabann pese a esto.

# 1. DATOS DEL PROBLEMA 


# Lo primero que vamos a hacer es definir todas las constantes y funciones que representan las restricciones y los datos de audiencia del problema.


# Equipos y Categorías 

# Definimos una tupla que define la categoria de cada equipo segun las audiencias
CATEGORIAS_EQUIPOS_MAP = {
    "FC Barcelona": "A", "Real Madrid": "A", "Atlético de Madrid": "A",
    "Villarreal CF": "B", "Real Sociedad": "B", "Athletic Club": "B", 
    "Real Betis": "B", "Girona FC": "B", "Sevilla FC": "B", "Valencia CF": "B",
    "RCD Espanyol": "C", "RC Celta": "C", "Elche CF": "C", "Rayo Vallecano": "C",
    "Getafe CF": "C", "CA Osasuna": "C", "Deportivo Alavés": "C", 
    "RCD Mallorca": "C", "Levante UD": "C", "Real Oviedo": "C"
}

# Generamos EQUIPOS_CAT basándonos en el orden de equipos_liga
EQUIPOS_CAT = [CATEGORIAS_EQUIPOS_MAP[equipo] for equipo in equipos_liga]



# Define un diccionario que almacena la audiencia base para un partido jugado el Sábado a las 22:00 h. Restriccion 2
AUDIENCIA_BASE_SAB_22H: Dict[Tuple[str, str], float] = {
    ('A', 'A'): 5.0, ('A', 'B'): 4.3, ('A', 'C'): 3.5,
    ('B', 'B'): 3.5, ('B', 'A'): 4.0,  ('B','C'): 2.0,
    ('C', 'C'): 1.0, ('C', 'A'): 2.8, ('C', 'B'): 1.7,

}


# Definimos una funcion que dados los indices 
def get_audiencia_base(eq1_idx: int, eq2_idx: int) -> float: # Toma dos enteros(indices de los equipos del partido) y devuelve un decimal(la audiencia)
    # Obtenemos las categorias usando el indice 
    cat1 = EQUIPOS_CAT[eq1_idx]
    cat2 = EQUIPOS_CAT[eq2_idx]
    # Obtenemos la clave del diccionario
    key = tuple((cat1, cat2))
    # Devolvemos la audiencia del partido
    return AUDIENCIA_BASE_SAB_22H.get(key, 0.0)


# Horarios y Coeficientes de penalizacion y solapamiento

# Definimos una lista de los 12 nombres de las franjas horarias disponibles. 
# Utilizaremos los índices numéricos (0 a 11) para representar los horarios en el cromosoma.
HORARIOS = [
    "Vie 20:00", "Lun 20:00",
    "Sab 12:00", "Sab 16:00", "Sab 18:00", "Sab 20:00", "Sab 22:00",
    "Dom 12:00", "Dom 16:00", "Dom 18:00", "Dom 20:00", "Dom 22:00"
]

# Definimos un diccionario con los coeficientes de audiencia de cada partido(tomamos como referencia Sábado a las 22:00)(Restriccion 3)
COEF_HORARIO = {
    "Vie 20:00": 0.8, "Lun 20:00": 0.7,
    "Sab 12:00": 0.6, "Sab 16:00": 0.7, "Sab 18:00": 0.8, "Sab 20:00": 0.9, "Sab 22:00": 1.0,
    "Dom 12:00": 0.5, "Dom 16:00": 0.6, "Dom 18:00": 0.7, "Dom 20:00": 0.8, "Dom 22:00": 0.9
}
# Definimos el numero de franjas horarias posibles de los partidos
NUM_HORARIOS = len(HORARIOS)



# Definimos un diccionario con los coeficientes de reduccion de las audiencias si se solapan partidos(Restriccion 5)
COEF_CONCURRENCIA: Dict[int, float] = {
    0: 1.0, 1: 0.75, 2: 0.6, 3: 0.5, 
    4: 0.4, 5: 0.35, 6: 0.3, 7: 0.25,
}
# Observemos que hemos hecho una transformacion. Por ejemplo para 2 coincidencias la reduccion es del 40% pero nosotros vamos a trabajar con un coeficiente de 0.6.
# Es simplemente dos formas de trabajar con el mismo concepto aritmeticamente. De esta forma no tenemos que restar luego en los calculos, solo multiplicar por el
# coeficiente. 

# Parámetros del Algoritmo Genetico. Definimos el tamaño de la poblacion, numero de generaciones y la penalizacion
# Utilizamos una penalizacion tan grande que se resta a la audiencia para descartar rapidamente las soluciones que no cumplan alguna restriccion
# Por ejemplo que un equipo juegue dos veces. 
POPULATION_SIZE = 100
NUM_GENERATIONS = 500
PENALTY_VIOLATION = 1_000_000.0 


# 2. FUNCION FITNESS



# Definimos una funcion que nos calcula el numero de coincidencias en cada franja horaria de la jornada. Basicamente cuenta cuantos partidos se juegan al mismo tiempo.
#  Recorre el cromosoma y genera un diccionario donde la clave es el horario y el valor es cuántos partidos hay en ese bloque.
def calcular_concurrencia(cromosoma: List[Tuple[int, int, int]]) -> Dict[int, int]: # Toma un cromosoma (lista de tuplas (local, visitante, horario_idx)) y 
    # devuelve un diccionario con el conteo de partidos por horario.

    concurrencia: Dict[int, int] = {h_idx: 0 for h_idx in range(NUM_HORARIOS)} # Inicializa un diccionario concurrencia donde cada índice de horario posible 
    # (desde 0 hasta NUM_HORARIOS-1) tiene un contador inicializado a cero.
    for _, _, h_idx in cromosoma: # Itera sobre cada tupla en el cromosoma, extrayendo solo el índice del horario (h_idx), ignorando los equipos local y visitante.
        concurrencia[h_idx] += 1 # Incrementamos el contador de concurrencia en funcion del indice
    return concurrencia 



# Ahora definimos la funcion fitness que es la encargada de determinar que tan buena es una solucion(individuo) para resolver el problema. 
# En este caso para ver como de buena es una solucion tenemos que calcular su audiencia ya que es lo que queremos maximizar.
def fitness(cromosoma: List[Tuple[int, int, int]]) -> float: # Toma un cromosoma y devuelve un valor de aptitud (float).

    # Verificar que todos los dias se juega y que un equipo solo juega una vez

    equipos_jugando = set() # Definimos un conjunto vacio para los equipos 
    dias_con_partido = set() # Lo mismo para los dias 
    invalido = False # Para validar la jornada. Tienen que cumplir las restricciones. Si no lo penalizamos.  


    for local, visitante, horario_idx in cromosoma:
        if local in equipos_jugando or visitante in equipos_jugando or local == visitante: # Comprobamos que si el equipo esta jugando en otro partido o si juega contra si mismo.
            invalido = True # Si se cumple alguna condicion invalidamos la jornada
            break
        # Vamos añadiendo los equipos al conjunto de los que estan jugando segun recorremos el cromosoma para no repetir equipo
        equipos_jugando.add(local) 
        equipos_jugando.add(visitante)

        # Identificamos los dias con los indices para luego hacer la comprobacion de que jueguen todos los dias 
        if horario_idx in (0, 1): dias_con_partido.add("VL") # Asocia los índices de horario 0 y 1 con el bloque de día "VL" (Viernes/Lunes).
        elif horario_idx >= 2 and horario_idx <= 6: dias_con_partido.add("Sab") # Asocia los índices 2 al 6 con el día "Sab" (Sábado).
        elif horario_idx >= 7: dias_con_partido.add("Dom") # Asocia los índices 7 en adelante con el día "Dom" (Domingo).
    
    if len(equipos_jugando) != 20 or invalido:
        return -PENALTY_VIOLATION # Si no estan jugando todos o si alguno juega demás o contra si mismo aplicamos una penalizacion muy grande

    # Ahora comprobamos los dias de juego
    if len(dias_con_partido) < 3: # si no se juegan todos los dias aplicamos tambien penalizacion miy grande
         return -PENALTY_VIOLATION 

    # Una vez comprobadas las restricciones calculamos la audiencia total

    # Primero vemos si hay solapamiento con la funcion que definimos antes 
    concurrencia_horarios = calcular_concurrencia(cromosoma)
    puntuacion_audiencia = 0.0 # Inicializamos la audiencia en 0


    for local, visitante, horario_idx in cromosoma:  # Recorremos el cromosoma para calcular la audiencia
        base = get_audiencia_base(local, visitante) # Obtenemos la audiencia base como si el partido se jugara el sabado a las 22:00
        horario_str = HORARIOS[horario_idx] # Obtenemos la franja horaria del partido como string a partir de su indice
        coef_h = COEF_HORARIO[horario_str] # Obtenemos el coeficiente de audiencia segun la franja horaria que tengamos
        num_coincidentes = concurrencia_horarios[horario_idx] # Vemos si hay coincidencias en esa franja horaria 
        coef_c = COEF_CONCURRENCIA.get(num_coincidentes, COEF_CONCURRENCIA[7]) # Aplicamos el coeficiente de solapamiento. 
        # Usamos el máximo de reducción si hay mas de 7 coincidencias

        # Hacemos el calculo de la audiencia del partido
        audiencia_partido = base * coef_h * coef_c
        # Calculamos la audiencia de la jornada 
        puntuacion_audiencia += audiencia_partido
    
    # Devolvemos audiencia segun solapamientos y horarios. 
    return puntuacion_audiencia

# Observemos que como tenemos varios return la funcion ejecutara el primero que se encuentre. Es decir si no se cumple las restricciones se devolvera la penalizacion.



# Definimos una funcion para expresar el cromosoma del individuo(jornada) que es una lista de numeros y tuplas de una forma mas legible. 
# Usaremos la funcion para devolver la mejor solucion encontrada una vez aplicado el algoritmo genetico.
def formatear_jornada(cromosoma: List[Tuple[int, int, int]]) -> str: # Toma el cromosoma(lista de tuplas) y devuelve un string
    lineas = ["Solución de Jornada Óptima:"]
    for local, visitante, horario_idx in cromosoma: # Recorremos cada partido del cromosoma
        nombre_local = equipos_liga[local]
        nombre_visitante = equipos_liga[visitante]
        cat_local = CATEGORIAS_EQUIPOS_MAP[nombre_local] # Categoría fija
        cat_visitante = CATEGORIAS_EQUIPOS_MAP[nombre_visitante]
        
        lineas.append(f"  {HORARIOS[horario_idx]}: {nombre_local} ({cat_local}) vs {nombre_visitante} ({cat_visitante})")
    return "\n".join(lineas) # Une todas las líneas de la lista en una sola cadena de texto, separadas por saltos de línea. Esta función no la conocía la encontré en un vídeo y la utilicé.




# 3. ALGORITMO GENETICO


# Ahora vamos a definir el algoritmo genetico como tal. Utiliza la funcion fitness que hemos definido para ir evolucionando la poblacion para encontrar la solucion.

# Como vimos en los ejemplos de clase utilizamos programacion orientada objetos. Definimos una clase para aplicar el algoritmo.

class GeneticAlgorithm:

    # Definimos la funcion constructor para inicializar los atributos del algoritmo y del problema
    def __init__(self, 
        jornada_fija,
        population_size: int = 100, 
        elitism_rate: float = 0.3, 
        crossover_rate: float = 0.8, 
        mutation_rate: float = 0.7, 
        num_generations: int = 5000, 
        seed: int = None):
        # Definimos el tamaño de poblacion, tasa de elitismo, tasa de mutacion, numero de generacion.
        self.jornada_fija = jornada_fija
        self.population_size = population_size
        self.elitism_rate = elitism_rate
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_generations = num_generations
        if seed is not None:
            random.seed(seed)
        
        # Definimos el numero de equipos y de partidos y los indices de los horarios  
        self.num_teams = 20
        self.num_matches = 10
        self.allowed_horarios = list(range(len(HORARIOS)))


    # Definimos una funcion para generar individuos(jornadas) aleatorias.
    def random_individual(self) -> List[Tuple[int, int, int]]: # Nos devuelve una lista de tuplas de 3 enteros, equipo local, equipo visitante y horario
        # Partimos de la jornada fija seleccionada en Streamlit
        # jornada_fija es una lista de tuplas (local, visitante)
        jornada = []
        for local, visitante, _  in self.jornada_fija:
            horario = random.choice(self.allowed_horarios)
            jornada.append((local, visitante, horario))
        return jornada

    # Funcion para generar la poblacion a partir de la funcion que genera individuos.
    def init_population(self) -> List[List[Tuple[int, int, int]]]:
        return [self.random_individual() for _ in range(self.population_size)] # Generamos tantos individuos como indique population_size. 
        #Es un bucle for pero escrito en una linea. Lo vimos en clase. 

    # Funcion para evaluar la poblacion
    def evaluate(self, population: List[List[Tuple[int, int, int]]]) -> List[Tuple[float, List[Tuple[int, int, int]]]]:
        puntuados = [(fitness(ind), ind) for ind in population] # Crea parejas (puntuación, jornada) usando la función fitness que vimos antes.
        puntuados.sort(key=lambda x: x[0], reverse=True) # Ordena la población de mayor a menor audiencia.
        return puntuados

    # Funcion para elegir el padre
    def tournament_select(self, scored_pop: List[Tuple[float, List[Tuple[int, int, int]]]], k: int = 3) -> List[Tuple[int, int, int]]:
        contenders = random.sample(scored_pop, k) # Elige k (3) individuos al azar de la población.
        winner = max(contenders, key=lambda x: x[0])[1] # El que tiene el fitness más alto entre los 3 gana el derecho a reproducirse.
        return winner[:] 

    # Funcion para el cruce genetico, cambia dos jornadas para generar hijos 
    def one_point_crossover_jornada(self, a: List[Tuple[int, int, int]], b: List[Tuple[int, int, int]]) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
        if len(a) != len(b):
            return a[:], b[:] 
        point = random.randint(1, len(a) - 1) #  Elige un partido al azar entre los 10 partidos.
        hijo1 = a[:point] + b[point:] # El hijo1 hereda los primeros partidos del padre a y los restantes del padre b, y viceversa para el hijo2
        hijo2 = b[:point] + a[point:]
        return hijo1, hijo2

    # Funcion para la mutacion de padres a hijos
    def mutate(self, ind: List[Tuple[int, int, int]]) -> None: 
        if random.random() < self.mutation_rate:  # Con un 70% de probabilidad, elige un partido y le cambia el horario por uno distinto.
            match_idx = random.randrange(len(ind))
            local, visitante, current_h = ind[match_idx]
            new_h = random.choice([h for h in self.allowed_horarios if h != current_h])
            ind[match_idx] = (local, visitante, new_h)
        
        

    # Funcion para la evolucion de la poblacion 
    def evolve(self):
        # Creamos la población inicial y la evalúamos por primera vez
        population = self.init_population()
        scored = self.evaluate(population)
        # Registramos cuál es la mejor jornada encontrada al inicio.
        best_score, best_ind = scored[0]
        # Calculamos cuántos individuos de la poblacion se salvarán. 
        elite_count = max(1, int(self.elitism_rate * self.population_size))
        


        for gen in range(self.num_generations):
            new_population: List[List[Tuple[int, int, int]]] = [ind[:] for _, ind in scored[:elite_count]] # Copiamos los mejores individuos directamente 
            #a la siguiente generación. Elitismo. 

            # Rellenamos el resto de la población mediante reproducción. Utilizamos las funciones anteriores.
            while len(new_population) < self.population_size:
                # Seleccionamos dos padres
                p1 = self.tournament_select(scored, k=3) 
                p2 = self.tournament_select(scored, k=3)
                # Cruzamos a los padres para crear hijos, o simplemente los clonamos si no hay cruce.
                if random.random() < self.crossover_rate:
                    c1, c2 = self.one_point_crossover_jornada(p1, p2)
                else:
                    c1, c2 = p1[:], p2[:]
                
                # Mutamos a los hijos y los añadimos a la nueva generación.
                self.mutate(c1)
                new_population.append(c1)
                if len(new_population) < self.population_size:
                    self.mutate(c2)
                    new_population.append(c2)
            
            # La poblacion pasa a ser la "nueva generacion"
            population = new_population
            # Volvemos a puntuar las jornadas 
            scored = self.evaluate(population)
            
            # Si el mejor de esta generación es mejor que el récord histórico actualizamos el récord.
            if scored[0][0] > best_score:
                best_score, best_ind = scored[0]

            # Devolvemos la mejor solucion encontrada despues de todas las generaciones. Devolvemos la jornada y su audiencia.
            yield best_score, best_ind # Cambiamos el return para hacer la grafica





## APLICACIÓN DEL ALGORITMO A LA JORNADA CREADA 
## PLOTEAMOS A SU VEZ LAS AUDIENCIAS DE CADA GENERACIÓN 

if st.button("Mostrar la gráfica y el resultado del algoritmo genético para la jornada seleccionada"):

    # Creamos la variable para el gráfico vacío
    grafico_dinamico = st.empty()
    
    # Lista para acumular los datos de todas las generaciones
    historial_audiencia = []

    
    # Definimos un objeto de la clase con los parametros que definimos al principio del todo.
    ga = GeneticAlgorithm(
        jornada_fija = jornada_seleccionada,
        population_size=POPULATION_SIZE, # Tamaño de la poblacion 
        num_generations=NUM_GENERATIONS, # Numero generaciones del algoritmo
        seed=42, # Establecemos semilla
    )

    for gen, (score, ind) in enumerate(ga.evolve()):
        #  Guardamos el nuevo score
        historial_audiencia.append(score)

        # Añadimos el nuevo punto al gráfico
        # El eje X se gestiona automáticamente por el índice del DataFrame
        nuevo_punto = pd.DataFrame(historial_audiencia, columns=['Audiencia'])
        grafico_dinamico.line_chart(nuevo_punto)
        
        # Guardamos la mejor jornada encontrada
        mejor_audiencia = score
        mejor_config_horarios = ind
    
    # Mostramos mejor jornada encontrada
    st.write(f"Audiencia máxima posible para tus partidos: {mejor_audiencia:.2f}")
    st.text(formatear_jornada(mejor_config_horarios))




## Comentario final: como estamos trabajando con la session_state para generar la jornada customizada streamlit no nos permite generar la jornada aleatoria
## y seleccionar la jornada customizada en la misma sesión. Por ello, se vuelve a resetear para hacer una de las dos si ya hemos hecho la otra. 

