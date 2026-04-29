## Optimización de horarios de la Liga mediante algoritmos genéticos
Este proyecto forma parte de un ejercicio práctico para la asignatura de Inteligencia Artificial (Grado en Matemáticas). El objetivo principal es diseñar y ejecutar un sistema capaz de organizar los horarios de una jornada de fútbol profesional para maximizar la audiencia total,
cumpliendo con diversas restricciones logísticas y comerciales.


## Descripción del Problema
Actuando como analistas para La Liga, debemos asignar cada uno de los 10 partidos de una jornada a uno de los 12 slots horarios disponibles (repartidos de viernes a lunes). La audiencia de cada partido depende de:
  Categoría de los equipos: (A, B o C) según su base de seguidores. 
  Slot horario: Coeficientes de ponderación según el día y la hora.  
  Coincidencias: Penalizaciones porcentuales si varios partidos ocurren simultáneamente.


## Restricciones y Parámetros
Slots Fijos: Horarios predefinidos (Viernes, Sábado, Domingo y Lunes).
Mínimo de Actividad: Debe jugarse al menos un partido cada día.
Audiencia Base: Definida por una matriz de enfrentamientos entre categorías.
Reducción por Horario: Ajuste de audiencia según el momento de emisión (ej. Sábado 22:00h es el 100%).
Penalización por Solapamiento: Reducción acumulativa del 25% al 75% dependiendo del número de partidos simultáneos.


## Solución Propuesta
El proyecto se divide en dos fases principales:

  1. Análisis y Algoritmia (Notebook)
    Estudio del espacio de búsqueda y complejidad.
    Implementación de una solución por Fuerza Bruta para comparar rendimiento.
    Diseño de un Algoritmo Genético:
      Estructura de datos: Definición de cromosomas y genes.    
      Función Fitness: Algoritmo de cálculo de audiencia neta ponderada.
      Operadores: Selección, cruce y mutación optimizados para el problema.

  2. Interfaz Visual (Streamlit)
    Despliegue de una aplicación interactiva que permite:
    Generar jornadas aleatorias o manuales (con control de errores).
    Ejecutar el algoritmo genético en tiempo real.
    Visualizar la evolución de la audiencia (fitness) mediante gráficos dinámicos por generación.
