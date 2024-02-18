import pygame
import random
import numpy as np
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.99):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.q_table = np.zeros((state_size, action_size))

    def choose_action(self, state):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.randint(0, self.action_size - 1)
        else:
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.discount_factor * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.learning_rate * td_error

        self.exploration_rate *= self.exploration_decay

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((75, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.alive_time = 0

    def update(self):
        self.alive_time += 1

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 20)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

player = Player()
enemies = pygame.sprite.Group()  # Create enemy group

all_sprites = pygame.sprite.Group()
all_sprites.add(player)

reward = 0

running = True
clock = pygame.time.Clock()

# Initialize Q-learning agent
state_size = (SCREEN_WIDTH + 1) * (SCREEN_HEIGHT + 1) * (SCREEN_WIDTH + 1) * (SCREEN_HEIGHT + 1)
action_size = 4  # Up, Down, Left, Right
agent = QLearningAgent(state_size, action_size)

while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
        elif event.type == ADDENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)

    pressed_keys = pygame.key.get_pressed()

    # Get current state
    state = (
        player.rect.left * (SCREEN_HEIGHT + 1) * (SCREEN_WIDTH + 1) * (SCREEN_HEIGHT + 1) +
        player.rect.top * (SCREEN_WIDTH + 1) * (SCREEN_HEIGHT + 1) +
        player.rect.right * (SCREEN_HEIGHT + 1) +
        player.rect.bottom
    )

    # Choose action based on Q-learning
    action = agent.choose_action(state)

    # Update player position based on action
    if action == 0:
        player.rect.move_ip(0, -10)  # Move up
    elif action == 1:
        player.rect.move_ip(0, 10)  # Move down
    elif action == 2:
        player.rect.move_ip(-10, 0)  # Move left
    elif action == 3:
        player.rect.move_ip(10, 0)  # Move right

    
    # Update reward
    collide = False
    if pygame.sprite.spritecollideany(player, enemies):

        collide = True
        # Decrement reward if player collides with enemy
       

    # Update Q-table based on the new state
    next_state = (
        player.rect.left * (SCREEN_HEIGHT + 1) * (SCREEN_WIDTH + 1) * (SCREEN_HEIGHT + 1) +
        player.rect.top * (SCREEN_WIDTH + 1) * (SCREEN_HEIGHT + 1) +
        player.rect.right * (SCREEN_HEIGHT + 1) +
        player.rect.bottom
    )

    if player.alive_time % 30 == 0: 
        if collide == True:
            reward -=10
            print("Collision")

        else:
            reward += 5

        print("Reward:", reward)
    
    agent.update_q_table(state, action, reward, next_state)

    # Update enemies
    enemies.update()
    # Update player
    player.update()

    all_sprites.update()

    # Draw everything
    screen.fill((0, 0, 0))
    
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)
    for entity in enemies:
        screen.blit(entity.surf, entity.rect)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
