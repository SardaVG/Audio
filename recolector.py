import pygame
import random
import openai
import threading
import time


pygame.init()

screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Agente Recolector de Objetos")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


agent_size = 20
object_size = 10
enemy_size = 20


agent_rect = pygame.Rect(random.randint(0, screen_width - agent_size), random.randint(0, screen_height - agent_size), agent_size, agent_size)
agent_speed = 3


num_objects = 5
num_enemies = 3

objects = []
for _ in range(num_objects):
    objects.append(pygame.Rect(random.randint(0, screen_width - object_size), random.randint(0, screen_height - object_size), object_size, object_size))

enemies = []
for _ in range(num_enemies):
    enemies.append(pygame.Rect(random.randint(0, screen_width - enemy_size), random.randint(0, screen_height - enemy_size), enemy_size, enemy_size))


def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# Función para mover al agente
def move_agent(keys, agent_rect):
    if keys[pygame.K_LEFT] and agent_rect.left > 0:
        agent_rect.x -= agent_speed
    if keys[pygame.K_RIGHT] and agent_rect.right < screen_width:
        agent_rect.x += agent_speed
    if keys[pygame.K_UP] and agent_rect.top > 0:
        agent_rect.y -= agent_speed
    if keys[pygame.K_DOWN] and agent_rect.bottom < screen_height:
        agent_rect.y += agent_speed

def move_enemy(enemy, agent_rect):
    # Calculate direction to move enemy towards agent
    dx = agent_rect.x - enemy.x
    dy = agent_rect.y - enemy.y
    
    # Normalize movement speed
    speed = 2
    if dx != 0 or dy != 0:
        # Calculate distance
        distance = (dx ** 2 + dy ** 2) ** 0.5
        # Normalize direction
        dx = (dx / distance) * speed if distance > 0 else 0
        dy = (dy / distance) * speed if distance > 0 else 0
    
    # Update enemy position
    enemy.x += dx
    enemy.y += dy
    
    # Keep enemy within screen bounds
    enemy.x = max(0, min(enemy.x, screen_width - enemy_size))
    enemy.y = max(0, min(enemy.y, screen_height - enemy_size))

# Fix indentation for these global variables
clock = pygame.time.Clock()
running = True
score = 0
enemy_responses = {i: None for i in range(num_enemies)}

while running:
    screen.fill(WHITE)
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    keys = pygame.key.get_pressed()
    move_agent(keys, agent_rect)

    
    # Replace OpenAI logic with direct enemy movement
    for enemy in enemies:
        move_enemy(enemy, agent_rect)

    
    objects_to_remove = []
    for obj in objects:
        if check_collision(agent_rect, obj):
            objects_to_remove.append(obj)
            score += 1

   
    for obj in objects_to_remove:
        objects.remove(obj)

    
    for enemy in enemies:
        if check_collision(agent_rect, enemy):
            print("¡Has sido alcanzado por un enemigo! Game Over.")
            running = False
    
   
    for obj in objects:
        pygame.draw.circle(screen, YELLOW, obj.center, object_size // 2)

   
    pygame.draw.rect(screen, BLUE, agent_rect)

    
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

   
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Objetos recolectados: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    
    pygame.display.flip()

    
    clock.tick(30)


pygame.quit()


#debe remover el código de openAI y hace que los enemigos se muevan por logica de programacion
#1.- sube tu codigo con el nombre recolector.py
#2.- Solo debes cambiar el metodo que llama a la ia, debes entender como funciona para sustituirlo 
#3.- Puedes revisar todos los ejemplos que desees pero no usar IA