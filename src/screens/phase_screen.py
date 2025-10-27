
import pygame
import sys
from typing import Dict, Any, List

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from src.managers.sound_manager import SoundManager

class PhaseScreen:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, sound_manager: SoundManager, stage_info: Dict[str, Any], stage_number: int):
        self.screen = screen
        self.base_font = font # The font passed from GameManager
        self.sound_manager = sound_manager
        self.stage_info = stage_info
        self.stage_number = stage_number
        self.running = True

        # Fonts for different text sizes
        self.title_font = pygame.font.Font(None, 50)
        self.header_font = pygame.font.Font(None, 40)
        self.text_font = pygame.font.Font(None, 28)
        self.small_text_font = pygame.font.Font(None, 22)

        # Mapping from enemy type string to actual image filename
        self.enemy_image_map = {
            "straight": "Enemy.gif",
            "weaving": "Enemy2.gif",
            "diving": "Enemy3.gif",
        }

    def _draw_text(self, text: str, position: tuple, font: pygame.font.Font, color: tuple = WHITE, center: bool = True) -> None:
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=position)
        else:
            text_rect = text_surface.get_rect(topleft=position)
        self.screen.blit(text_surface, text_rect)

    def _draw_enemy_images(self, enemy_types: List[str], y_pos: int) -> None:
        x_start = SCREEN_WIDTH / 2 - (len(enemy_types) - 1) * 75  # Center the images
        for enemy_type in enemy_types:
            image_filename = self.enemy_image_map.get(enemy_type)
            if image_filename:
                try:
                    image = pygame.image.load(f"assets/images/{image_filename}").convert_alpha()
                    image = pygame.transform.scale(image, (80, 80))  # Scale image for better display
                    image_rect = image.get_rect(center=(x_start, y_pos))
                    self.screen.blit(image, image_rect)
                    x_start += 150
                except pygame.error:
                    print(f"Warning: Could not load image for enemy type '{enemy_type}' from file '{image_filename}'")
            else:
                print(f"Warning: No image mapping found for enemy type '{enemy_type}'")

    def show(self) -> None:
        # Scale logo like in GameOverScreen
        logo_image = pygame.image.load("assets/images/Logo.png").convert_alpha()
        logo_width = int(SCREEN_WIDTH * 0.6)
        logo_height = int(logo_image.get_height() * (logo_width / logo_image.get_width()))
        logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4.5))
        
        self.sound_manager.play_sound('newphase')

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.running = False

            self.screen.fill((0, 0, 0))  # Black background
            self.screen.blit(logo_image, logo_rect)

            # --- Layout and Positioning ---
            y_pos = logo_rect.bottom + 20
            self._draw_text(f"Fase {self.stage_number}", (SCREEN_WIDTH / 2, y_pos), self.title_font)
            y_pos += 45

            self._draw_text("Inimigos:", (SCREEN_WIDTH / 2, y_pos), self.header_font)
            y_pos += 65  # Space for images
            self._draw_enemy_images(self.stage_info.get("enemy_types_available", []), y_pos)
            y_pos += 50



            self._draw_text("Pressione ENTER para continuar", (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40), self.text_font)

            pygame.display.flip()
