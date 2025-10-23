"""
Projeto: Clone 1942
Descrição: Módulo responsável por definir as classes de projéteis (Bullet e EnemyBullet) no jogo.
           Contém a lógica para a criação, movimentação e remoção de tiros do jogador e dos inimigos.
Autoria: Renato Gritti
"""

import pygame
from src.config import *
from typing import Tuple


class Bullet(pygame.sprite.Sprite):
    """
    Representa um projétil disparado pelo jogador.

    Este sprite se move para cima na tela e é removido quando sai dos limites visíveis.
    """
    def __init__(self, x: int, y: int) -> None:
        """
        Inicializa um novo projétil do jogador.

        Args:
            x (int): A coordenada X central inicial do projétil.
            y (int): A coordenada Y central inicial do projétil.
        """
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((4, 15))
        self.image.fill((255, 255, 0))  # Amarelo
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        """
        Atualiza a posição do projétil.

        Move o projétil para cima e o remove do grupo de sprites se ele sair da tela.
        """
        self.rect.y -= 10  # Move o projétil para cima
        if self.rect.bottom < 0:
            self.kill()  # Remove o projétil se ele sair da tela


class EnemyBullet(pygame.sprite.Sprite):
    """
    Representa um projétil disparado por um inimigo.

    Este sprite se move para baixo na tela e é removido quando sai dos limites visíveis.
    """
    def __init__(self, x: int, y: int, player_pos: Tuple[int, int], bullet_speed: int) -> None:
        """
        Inicializa um novo projétil inimigo.

        Args:
            x (int): A coordenada X central inicial do projétil.
            y (int): A coordenada Y central inicial do projétil.
            player_pos (Tuple[int, int]): A posição (x, y) do jogador. (Não usado para tiros retos neste momento).
            bullet_speed (int): A velocidade vertical do projétil inimigo.
        """
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((4, 15))
        self.image.fill((255, 0, 0))  # Vermelho
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))

        # Projéteis inimigos atiram reto para baixo
        self.speed_x: int = 0
        self.speed_y: int = bullet_speed  # Sempre se move para baixo

    def update(self) -> None:
        """
        Atualiza a posição do projétil inimigo.

        Move o projétil e o remove do grupo de sprites se ele sair da tela.
        """
        if (self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or
                self.rect.left > SCREEN_WIDTH or self.rect.right < 0):
            self.kill()  # Remove o projétil se ele sair da tela
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
