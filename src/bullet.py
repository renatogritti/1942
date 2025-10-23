# src/bullet.py
import pygame
from src.config import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill((255, 255, 0))  # Yellow
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 10  # Move the bullet up
        if self.rect.bottom < 0:
            self.kill()  # Remove the bullet if it goes off-screen

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, player_pos, bullet_speed):
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill((255, 0, 0))  # Red
        self.rect = self.image.get_rect(center=(x, y))

        # Bullets shoot straight down
        self.speed_x = 0
        self.speed_y = bullet_speed # Always move downwards


    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or \
           self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()  # Remove the bullet if it goes off-screen