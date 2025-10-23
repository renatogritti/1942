"""
Projeto: Clone 1942
Descrição: Módulo responsável por definir a classe Coin, que representa uma moeda coletável no jogo.
           As moedas são geradas por inimigos destruídos e fornecem energia ao jogador quando coletadas.
Autoria: Renato Gritti
"""

import pygame
import random
from src.config import *
from PIL import Image, ImageSequence
from typing import List, Tuple


class Coin(pygame.sprite.Sprite):
    """
    Representa uma moeda de energia que cai na tela e pode ser coletada pelo jogador.

    As moedas são sprites animados que, ao serem coletadas, restauram a energia do jogador.
    """
    animation_frames: List[pygame.Surface] = []
    frame_durations: List[int] = []
    _is_loaded: bool = False

    def __init__(self, center_pos: Tuple[int, int]) -> None:
        """
        Inicializa uma nova instância de Coin.

        Carrega os frames da animação do GIF da moeda se ainda não tiverem sido carregados.

        Args:
            center_pos (Tuple[int, int]): A posição central (x, y) onde a moeda será criada.
        """
        super().__init__()

        if not Coin._is_loaded:
            Coin._load_animated_gif()

        self.current_frame: int = random.randint(0, len(Coin.animation_frames) - 1)
        self.image: pygame.Surface = Coin.animation_frames[self.current_frame]
        self.rect: pygame.Rect = self.image.get_rect(center=center_pos)

        self.last_anim_time: int = 0
        self.anim_delay: int = Coin.frame_durations[self.current_frame]
        self.speed_y: int = 3  # Moeda cai lentamente

    @classmethod
    def _load_animated_gif(cls) -> None:
        """
        Carrega os frames de um arquivo GIF animado para uso como animação da moeda.

        Cada frame é convertido para uma superfície Pygame e redimensionado.
        As durações de cada frame também são armazenadas para controlar a animação.
        """
        try:
            pil_image: Image.Image = Image.open("assets/images/Coin.gif")
        except Exception as e:
            print(f"Erro ao carregar a imagem da moeda 'assets/images/Coin.gif': {e}")
            pygame.quit()
            return

        for frame in ImageSequence.Iterator(pil_image):
            duration: int = frame.info.get('duration', 100)
            cls.frame_durations.append(duration)

            frame_image: Image.Image = frame.convert('RGBA')
            pygame_image: pygame.Surface = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()

            # Redimensiona a moeda
            target_width: int = 30
            aspect_ratio: float = pygame_image.get_height() / pygame_image.get_width()
            target_height: int = int(target_width * aspect_ratio)
            scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (target_width, target_height))
            
            cls.animation_frames.append(scaled_image)
        cls._is_loaded = True

    def update(self) -> None:
        """
        Atualiza a animação e a posição da moeda na tela.

        Avança para o próximo frame da animação com base no tempo e move a moeda para baixo.
        A moeda é removida se sair da parte inferior da tela.
        """
        # Animação
        now: int = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.anim_delay = Coin.frame_durations[self.current_frame]
            center: Tuple[int, int] = self.rect.center
            self.image = self.animation_frames[self.current_frame]
            self.rect = self.image.get_rect(center=center)

        # Movimento
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()  # Remove se sair da tela
