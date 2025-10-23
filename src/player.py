"""
Projeto: Clone 1942
Descrição: Módulo responsável por definir a classe Player, que representa o avião controlável pelo jogador.
           Gerencia a movimentação do jogador, disparo de projéteis, coleta de itens (moedas),
           e sua interação com o ambiente e inimigos.
Autoria: Renato Gritti
"""

import pygame
import sys
from src.config import *
from src.bullet import Bullet
from PIL import Image, ImageSequence
from typing import List, Tuple, Any


class Player(pygame.sprite.Sprite):
    """
    Representa o avião do jogador no jogo.

    Gerencia a posição, energia, bombas, animação e ações do jogador, como mover e atirar.
    """
    def __init__(self, all_sprites: pygame.sprite.Group) -> None:
        """
        Inicializa o jogador com suas propriedades, como posição, energia e bombas.

        Args:
            all_sprites (pygame.sprite.Group): O grupo de todos os sprites do jogo,
                                               usado para adicionar projéteis do jogador.
        """
        super().__init__()
        self.all_sprites: pygame.sprite.Group = all_sprites
        self.bullets: pygame.sprite.Group = pygame.sprite.Group()
        
        self.animation_frames: List[pygame.Surface] = []
        self.frame_durations: List[int] = []
        self.load_animated_gif()

        self.current_frame: int = 0
        self.image: pygame.Surface = self.animation_frames[self.current_frame]
        self.rect: pygame.Rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
        
        self.max_energy: int = 100
        self.energy: int = self.max_energy
        self.bombs: int = 1
        self.last_anim_time: int = 0
        # Usa a duração própria do GIF para o atraso, ou um padrão
        self.anim_delay: int = self.frame_durations[0] if self.frame_durations else 50

    def load_animated_gif(self) -> None:
        """
        Carrega todos os frames de um GIF animado do avião do jogador e os converte para superfícies Pygame.

        Cada frame é redimensionado e suas durações são armazenadas para controlar a animação.
        """
        self.animation_frames = []
        self.frame_durations = []
        
        try:
            pil_image: Image.Image = Image.open("assets/images/plane.gif")
        except Exception as e:
            print(f"Erro ao carregar a imagem do avião do jogador 'assets/images/plane.gif': {e}")
            pygame.quit()
            sys.exit()
        for frame in ImageSequence.Iterator(pil_image):
            # Obtém a duração do frame
            duration: int = frame.info.get('duration', 50)
            self.frame_durations.append(duration)

            # Converte o frame PIL para superfície Pygame
            frame_image: Image.Image = frame.convert('RGBA')
            pygame_image: pygame.Surface = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()

            # Escala a imagem
            original_width: int = pygame_image.get_width()
            original_height: int = pygame_image.get_height()
            target_width: int = 64
            aspect_ratio: float = original_height / original_width if original_width > 0 else 1.0
            target_height: int = int(target_width * aspect_ratio)
            scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (target_width, target_height))
            
            self.animation_frames.append(scaled_image)

    def update(self) -> None:
        """
        Atualiza o estado do jogador, incluindo animação, movimento e restrição de tela.

        Processa a entrada do teclado para mover o jogador e garante que ele permaneça dentro dos limites da tela.
        """
        # --- Loop de Animação ---
        now: int = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.anim_delay = self.frame_durations[self.current_frame]
            
            # Atualiza a imagem e preserva o centro
            center: Tuple[int, int] = self.rect.center
            self.image = self.animation_frames[self.current_frame]
            self.rect = self.image.get_rect(center=center)

        # --- Manuseio de Movimento ---
        keys: Any = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

        # Mantém o jogador na tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def reset(self) -> None:
        """
        Reinicia a posição do jogador para o local inicial.

        Útil para iniciar um novo jogo ou após a morte do jogador.
        """
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60)

    def shoot(self) -> None:
        """
        Cria e dispara um projétil do jogador.

        O projétil é adicionado aos grupos de sprites do jogo para ser atualizado e desenhado.
        """
        bullet: Bullet = Bullet(self.rect.centerx, self.rect.top)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)
