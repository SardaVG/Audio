import pygame
import random
import math
import json
import openai

# Configuración de OpenAI
openai.api_key = ''

pygame.init()


screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Agente que evita obstáculos")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


agent_radius = 10
SAFE_DISTANCE = 1  

# Función para obtener decisión de la IA para esquivar obstáculos
def get_ai_avoidance_decision(agent_pos, obstacles, goal_pos):
    # Preparar el contexto para la IA
    obstacle_data = []
    for obs in obstacles:
        obstacle_data.append({
            "x": obs.x,
            "y": obs.y,
            "width": obs.width,
            "height": obs.height
        })
    
    prompt = {
        "agent_position": {"x": agent_pos.x, "y": agent_pos.y},
        "goal_position": {"x": goal_pos.x, "y": goal_pos.y},
        "obstacles": obstacle_data
    }
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that helps control an agent avoiding obstacles. The agent must maintain a safe distance from obstacles. Return only a JSON with 'direction_x' and 'direction_y' values between -2 and 2 for more aggressive avoidance when needed."},
                {"role": "user", "content": f"Given the current state: {json.dumps(prompt)}, provide movement direction to avoid obstacles and reach the goal. Keep at least {SAFE_DISTANCE} pixels away from obstacles. Use larger values (-2 to 2) when needed to avoid obstacles."}
            ]
        )
        
        direction_data = json.loads(response.choices[0].message.content)
        print(f"\nAI Movement Decision:")
        print(f"Direction X: {direction_data['direction_x']:.2f}")
        print(f"Direction Y: {direction_data['direction_y']:.2f}")
        return pygame.Vector2(direction_data["direction_x"], direction_data["direction_y"])
    except Exception as e:
        print(f"Error getting AI decision: {e}")
        return pygame.Vector2(0, 0)

# Función para generar obstáculos usando IA
def generate_ai_obstacles():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that generates obstacle positions. Return only a JSON array with 5 obstacles, each containing 'x', 'y', 'width', and 'height'."},
                {"role": "user", "content": f"Generate 5 obstacles for a {screen_width}x{screen_height} screen."}
            ]
        )
        
        obstacles_data = json.loads(response.choices[0].message.content)
        print("\nAI Generated Obstacles:")
        for i, obs in enumerate(obstacles_data, 1):
            print(f"Obstacle {i}: Position({obs['x']}, {obs['y']}), Size({obs['width']}x{obs['height']})")
        
        new_obstacles = []
        for obs in obstacles_data:
            new_obstacles.append(pygame.Rect(
                obs["x"], 
                obs["y"], 
                obs["width"], 
                obs["height"]
            ))
        
        return new_obstacles
    except Exception as e:
        print(f"Error generating obstacles: {e}")
        return []

# Reemplazar la generación aleatoria de obstáculos con la versión IA
obstacles = generate_ai_obstacles()
if not obstacles:  
    obstacles = []
    for _ in range(5):
        obs_width = random.randint(50, 100)
        obs_height = random.randint(50, 100)
        obs_x = random.randint(0, screen_width - obs_width)
        obs_y = random.randint(0, screen_height - obs_height)
        obstacles.append(pygame.Rect(obs_x, obs_y, obs_width, obs_height))


agent_pos = pygame.Vector2(50, 50)
goal_pos = pygame.Vector2(screen_width - 50, screen_height - 50)


def calculate_distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

# Función para evitar obstáculos
def avoid_obstacles(agent_pos, direction):
    ai_direction = get_ai_avoidance_decision(agent_pos, obstacles, goal_pos)
    return ai_direction

def check_collision(position, obstacles, include_safe_distance=True):
    # Crear un rectángulo para el agente con un margen de seguridad
    safety_margin = SAFE_DISTANCE if include_safe_distance else 0
    agent_rect = pygame.Rect(
        position.x - (agent_radius + safety_margin), 
        position.y - (agent_radius + safety_margin),
        (agent_radius + safety_margin) * 2, 
        (agent_radius + safety_margin) * 2
    )
    
    for obstacle in obstacles:
        if agent_rect.colliderect(obstacle):
            return True
    return False

def find_safe_position(current_pos, direction, movement_speed, obstacles):
    # Intentar diferentes multiplicadores de velocidad para encontrar una posición segura
    for speed_multiplier in [1.0, 1.5, 2.0]:
        next_pos = current_pos + direction * movement_speed * speed_multiplier
        if not check_collision(next_pos, obstacles):
            return next_pos, speed_multiplier
    return None, None

clock = pygame.time.Clock()
running = True

# Aumentar la velocidad de movimiento
movement_speed = 10

# Ajustar la distancia de detección de la meta
GOAL_DETECTION_RADIUS = 20  

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Calcular distancia a la meta antes de mover
    distance_to_goal = calculate_distance(agent_pos, goal_pos)
    
    if distance_to_goal < GOAL_DETECTION_RADIUS:
        print("¡Meta alcanzada!")
        running = False
    else:
        direction = goal_pos - agent_pos
        if direction.length() != 0:
            direction.normalize_ip()

        direction = avoid_obstacles(agent_pos, direction)
        
        # Si estamos cerca de la meta, reducir la velocidad
        if distance_to_goal < GOAL_DETECTION_RADIUS * 2:
            movement_speed = 5  # Velocidad reducida cerca de la meta
        
        # Intentar encontrar una posición segura
        safe_pos, speed_mult = find_safe_position(agent_pos, direction, movement_speed, obstacles)
        
        if safe_pos is not None:
            agent_pos = safe_pos
            if speed_mult > 1.0:
                print(f"¡Movimiento evasivo! Velocidad multiplicada por {speed_mult:.1f}")
        else:
            print("¡Buscando ruta alternativa!")
            # Intentar encontrar una dirección alternativa
            for angle in [45, -45, 90, -90]:
                rotated_direction = pygame.Vector2()
                rotated_direction.x = direction.x * math.cos(math.radians(angle)) - direction.y * math.sin(math.radians(angle))
                rotated_direction.y = direction.x * math.sin(math.radians(angle)) + direction.y * math.cos(math.radians(angle))
                
                safe_pos, speed_mult = find_safe_position(agent_pos, rotated_direction, movement_speed, obstacles)
                if safe_pos is not None:
                    agent_pos = safe_pos
                    print(f"¡Nueva dirección encontrada! Ángulo: {angle}°")
                    break

    for obs in obstacles:
        pygame.draw.rect(screen, BLACK, obs)
    
    pygame.draw.circle(screen, GREEN, goal_pos, 10)
    
    pygame.draw.circle(screen, BLUE, (int(agent_pos.x), int(agent_pos.y)), agent_radius)
    
    pygame.display.flip()
    
    clock.tick(60)


pygame.quit()


#1.-Agrégale la toma de deciones por IA
#2.- La decisión de esquivar los bloques la debe tomar la IA
#3.- La decisión de donde poner los nuevos obstáculos debe ser por ia

#solo debe resolver el punto 2 o el 3

#adjunta tu codigo con el nombre meta.py