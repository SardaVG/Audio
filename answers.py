"""
Programación basada en agentes - Examen
Nombre: Victor Eduardo Garcia Sardaneta
"""

# 1. Los agentes reactivos pueden razonar sobre su entorno y planificar acciones futuras.
respuesta1 = "Falso"  # Los agentes reactivos responden de manera inmediata sin planificación

# 2. En la arquitectura de un agente BDI, ¿qué representa 'Belief'?
respuesta2 = "Las creencias o conocimientos que el agente tiene sobre el mundo"

# 3. ¿Qué método HTTP se usa para hacer una solicitud a OpenAI API?
respuesta3 = "POST"

# 4. ¿Para qué sirve el parámetro 'temperature' en OpenAI API?
respuesta4 = "Controla la creatividad de las respuestas generadas"

# 5. Los agentes pueden aprender de su experiencia y mejorar su desempeño con el tiempo.
respuesta5 = "Verdadero"

# 6. ¿Qué significa la propiedad de autonomía en un agente inteligente?
respuesta6 = "Que el agente opera sin intervención directa y controla sus acciones"

# 7. ¿Qué rol proporciona instrucciones iniciales al modelo en una solicitud a OpenAI API?
respuesta7 = "system"

# 8. ¿Cómo se maneja la entrada del usuario en Pygame?
respuesta8 = "A través del módulo pygame.event"

# 9. Pygame permite la reproducción de sonidos y música en un juego.
respuesta9 = "Verdadero"

# 10. ¿Cuál de las siguientes características NO es propia de los agentes inteligentes?
respuesta10 = "Memoria ilimitada"

# Crear un diccionario con todas las respuestas
respuestas = {
    "Pregunta 1": respuesta1,
    "Pregunta 2": respuesta2,
    "Pregunta 3": respuesta3,
    "Pregunta 4": respuesta4,
    "Pregunta 5": respuesta5,
    "Pregunta 6": respuesta6,
    "Pregunta 7": respuesta7,
    "Pregunta 8": respuesta8,
    "Pregunta 9": respuesta9,
    "Pregunta 10": respuesta10
}

# Imprimir todas las respuestas
for pregunta, respuesta in respuestas.items():
    print(f"{pregunta}: {respuesta}") 