"""
Projeto: Clone 1942
Descrição: Módulo que define as classes de Power-ups que podem ser coletados pelo jogador.
Autoria: Renato Gritti
"""

import pygame
import random
from src.config import SCREEN_HEIGHT
from PIL import Image, ImageSequence
from typing import List, Tuple

class BombPowerUp(pygame.sprite.Sprite):
    """
    Representa um power-up de bomba que pode ser coletado pelo jogador.
    """
    animation_frames: List[pygame.Surface] = []
    frame_durations: List[int] = []
    _is_loaded: bool = False

    def __init__(self, center_pos: Tuple[int, int]) -> None:
        """
        Inicializa um novo power-up de bomba.
        """
        super().__init__()

        if not BombPowerUp._is_loaded:
            BombPowerUp._load_animated_gif()

        self.current_frame: int = random.randint(0, len(BombPowerUp.animation_frames) - 1)
        self.image: pygame.Surface = BombPowerUp.animation_frames[self.current_frame]
        self.rect: pygame.Rect = self.image.get_rect(center=center_pos)

        self.last_anim_time: int = 0
        self.anim_delay: int = BombPowerUp.frame_durations[self.current_frame]
        self.speed_y: int = 3

    @classmethod
    def _load_animated_gif(cls) -> None:
        """
        Carrega os frames do GIF animado da bomba.
        """
        try:
            pil_image: Image.Image = Image.open("assets/images/bomb.gif")
        except Exception as e:
            print(f"Erro ao carregar a imagem da bomba 'assets/images/bomb.gif': {e}")
            pygame.quit()
            return

        for frame in ImageSequence.Iterator(pil_image):
            duration: int = frame.info.get('duration', 100)
            cls.frame_durations.append(duration)

            frame_image: Image.Image = frame.convert('RGBA')
            pygame_image: pygame.Surface = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()

            target_width: int = 30
            aspect_ratio: float = pygame_image.get_height() / pygame_image.get_width()
            target_height: int = int(target_width * aspect_ratio)
            scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (target_width, target_height))
            
            cls.animation_frames.append(scaled_image)
        cls._is_loaded = True

    def update(self) -> None:
        """
        Atualiza a animação e a posição do power-up.
        """
        now: int = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.anim_delay = self.frame_durations[self.current_frame]
            center: Tuple[int, int] = self.rect.center
            self.image = self.animation_frames[self.current_frame]
            self.rect = self.image.get_rect(center=center)

        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class AmmoPowerUp(pygame.sprite.Sprite):
    """
    Representa um power-up de munição que pode ser coletado pelo jogador.
    """
    _image: pygame.Surface = None

    def __init__(self, center_pos: Tuple[int, int]) -> None:
        """
        Inicializa um novo power-up de munição.
        """
        super().__init__()

        if AmmoPowerUp._image is None:
            AmmoPowerUp._load_image()

        self.image = AmmoPowerUp._image
        self.rect: pygame.Rect = self.image.get_rect(center=center_pos)
        self.speed_y: int = 3

    @classmethod
    def _load_image(cls) -> None:
        """
        Carrega a imagem do power-up de munição.
        """
        try:
            image = pygame.image.load("assets/images/Ammo.png").convert_alpha()
            target_width: int = 35
            aspect_ratio: float = image.get_height() / image.get_width()
            target_height: int = int(target_width * aspect_ratio)
            cls._image = pygame.transform.scale(image, (target_width, target_height))
        except Exception as e:
            print(f"Erro ao carregar a imagem de munição 'assets/images/Ammo.png': {e}")
            pygame.quit()
            return

    def update(self) -> None:
        """
        Atualiza a posição do power-up.
        """
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
