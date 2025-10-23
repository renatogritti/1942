# src/coin.py
import pygame
import random
from src.config import *
from PIL import Image, ImageSequence

class Coin(pygame.sprite.Sprite):
    """Representa uma moeda de energia que cai na tela."""
    animation_frames = []
    frame_durations = []
    _is_loaded = False

    def __init__(self, center_pos):
        """Inicializa a moeda em uma posição específica."""
        super().__init__()

        if not Coin._is_loaded:
            Coin._load_animated_gif()

        self.current_frame = random.randint(0, len(Coin.animation_frames) - 1)
        self.image = Coin.animation_frames[self.current_frame]
        self.rect = self.image.get_rect(center=center_pos)

        self.last_anim_time = 0
        self.anim_delay = Coin.frame_durations[self.current_frame]
        self.speed_y = 3 # Moeda cai lentamente

    @classmethod
    def _load_animated_gif(cls):
        """Carrega os frames do GIF da moeda."""
        try:
            pil_image = Image.open("assets/images/Coin.gif")
        except Exception as e:
            print(f"Error loading coin image 'assets/images/Coin.gif': {e}")
            pygame.quit()
            return

        for frame in ImageSequence.Iterator(pil_image):
            duration = frame.info.get('duration', 100)
            cls.frame_durations.append(duration)

            frame_image = frame.convert('RGBA')
            pygame_image = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()

            # Redimensiona a moeda
            target_width = 30
            aspect_ratio = pygame_image.get_height() / pygame_image.get_width()
            target_height = int(target_width * aspect_ratio)
            scaled_image = pygame.transform.scale(pygame_image, (target_width, target_height))
            
            cls.animation_frames.append(scaled_image)
        cls._is_loaded = True

    def update(self):
        """Atualiza a animação e a posição da moeda."""
        # Animação
        now = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.anim_delay = self.frame_durations[self.current_frame]
            center = self.rect.center
            self.image = self.animation_frames[self.current_frame]
            self.rect = self.image.get_rect(center=center)

        # Movimento
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove se sair da tela
