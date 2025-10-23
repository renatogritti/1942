# src/bullet.py
import pygame
from src.config import *

class Bullet(pygame.sprite.Sprite):
    """Representa um projétil disparado pelo jogador."""
    def __init__(self, x, y):
        """Inicializa um projétil do jogador.

        Args:
            x (int): A coordenada X inicial do projétil.
            y (int): A coordenada Y inicial do projétil.
        """
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill((255, 255, 0))  # Yellow
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        """Atualiza a posição do projétil e o remove se sair da tela."""
        self.rect.y -= 10  # Move the bullet up
        if self.rect.bottom < 0:
            self.kill()  # Remove the bullet if it goes off-screen

class EnemyBullet(pygame.sprite.Sprite):
    """Representa um projétil disparado por um inimigo."""
    def __init__(self, x, y, player_pos, bullet_speed):
        """Inicializa um projétil inimigo.

        Args:
            x (int): A coordenada X inicial do projétil.
            y (int): A coordenada Y inicial do projétil.
            player_pos (tuple): A posição (x, y) do jogador (não usado para tiros retos).
            bullet_speed (int): A velocidade do projétil.
        """
        super().__init__()
        self.image = pygame.Surface((4, 15))
        self.image.fill((255, 0, 0))  # Red
        self.rect = self.image.get_rect(center=(x, y))

        # Bullets shoot straight down
        self.speed_x = 0
        self.speed_y = bullet_speed # Always move downwards


    def update(self):
        """Atualiza a posição do projétil inimigo e o remove se sair da tela."""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or \
           self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()  # Remove the bullet if it goes off-screen