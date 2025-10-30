import pygame
from typing import Any, Tuple, Callable
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from src.game_objects.player import Player, MiniPlane # Importar MiniPlane
from src.game_objects.enemy import Enemy
from src.game_objects.effects import Cloud
from src.game_objects.island import Island

class RenderManager:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font,
                 all_sprites_group: pygame.sprite.Group,
                 islands_group: pygame.sprite.Group,
                 enemy_bullets_group: pygame.sprite.Group,
                 background_surface: pygame.Surface,
                 get_score: Callable[[], int],
                 get_highscore: Callable[[], int],
                 get_player_energy: Callable[[], int],
                 get_player_max_energy: Callable[[], int],
                 get_player_bombs: Callable[[], int]) -> None:
        self.screen = screen
        self.font = font # Keep original font for other potential uses
        self.all_sprites = all_sprites_group
        self.islands = islands_group
        self.enemy_bullets = enemy_bullets_group
        self.background = background_surface
        self.get_score = get_score
        self.get_highscore = get_highscore
        self.get_player_energy = get_player_energy
        self.get_player_max_energy = get_player_max_energy
        self.get_player_bombs = get_player_bombs

        self.bg_y1: int = 0
        self.bg_y2: int = -self.background.get_height()

        # Novas fontes para a HUD
        self.font_label = pygame.font.Font(None, 24)
        self.font_value = pygame.font.Font(None, 38)

        # Carregar ícone da bomba
        try:
            self.bomb_icon = pygame.image.load("assets/images/bomb.gif").convert_alpha()
            self.bomb_icon = pygame.transform.scale(self.bomb_icon, (30, 30))
        except pygame.error:
            print("Warning: 'assets/images/bomb.png' not found. Using a placeholder.")
            self.bomb_icon = pygame.Surface((30, 30), pygame.SRCALPHA)
            self.bomb_icon.fill((255, 100, 0)) # Placeholder color

    def _draw_text(self, text: str, x: int, y: int, font: pygame.font.Font, color: Tuple[int, int, int] = WHITE, align: str = "left") -> None:
        """
        Desenha texto na tela, com alinhamento opcional.
        """
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "left":
            text_rect.topleft = (x, y)
        elif align == "right":
            text_rect.topright = (x, y)
        elif align == "center":
            text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def _draw_energy_bar(self, current_energy: int, max_energy: int) -> None:
        """
        Desenha a barra de energia do jogador na parte inferior da tela.
        """
        width, height = 200, 15
        x = (SCREEN_WIDTH - width) // 2
        y = SCREEN_HEIGHT - height - 25 # Positioned in the middle of the HUD area
        
        fill = (current_energy / max_energy) * width
        outline_rect = pygame.Rect(x, y, width, height)
        fill_rect = pygame.Rect(x, y, fill, height)
        
        color = (0, 255, 0) # Green
        if current_energy / max_energy < 0.3:
            color = (255, 0, 0) # Red
        elif current_energy / max_energy < 0.6:
            color = (255, 255, 0) # Yellow
            
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, WHITE, outline_rect, 2)

    def _draw_shadow(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        shadow_offset = (15, 25)
        shadow_pos = (rect.x + shadow_offset[0], rect.y + shadow_offset[1])
        shadow_image = surface.copy()
        shadow_image.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(shadow_image, shadow_pos)

    def _draw_hud(self) -> None:
        """
        Desenha a HUD na parte inferior da tela com um layout atraente.
        """
        label_y = SCREEN_HEIGHT - 60
        value_y = SCREEN_HEIGHT - 42

        # --- Lado Esquerdo: Score e Bombas ---
        energy_bar_x_start = (SCREEN_WIDTH - 200) // 2

        # Score
        self._draw_text("Score", 10, label_y, self.font_label)
        self._draw_text(f"{self.get_score():07d}", 10, value_y, self.font_value)

        # Bombas
        bombs_x = energy_bar_x_start - 100
        self._draw_text("Bombs", bombs_x, label_y, self.font_label, align="center")
        
        bomb_icon_y = value_y + (self.font_value.get_height() - self.bomb_icon.get_height()) // 2
        bomb_text = f"{self.get_player_bombs()}"
        bomb_text_width = self.font_value.size(bomb_text)[0]
        total_width = self.bomb_icon.get_width() + bomb_text_width + 5
        
        start_x = bombs_x - total_width // 2
        self.screen.blit(self.bomb_icon, (start_x, bomb_icon_y))
        self._draw_text(bomb_text, start_x + self.bomb_icon.get_width() + 5, value_y, self.font_value)

        # --- Lado Direito: Record ---
        energy_bar_x_end = energy_bar_x_start + 200
        record_x = energy_bar_x_end + ((SCREEN_WIDTH - energy_bar_x_end) / 2)
        
        self._draw_text("Record", record_x, label_y, self.font_label, align="center")
        self._draw_text(f"{self.get_highscore():07d}", record_x, value_y, self.font_value, align="center")

        # --- Centro: Barra de Energia ---
        self._draw_energy_bar(self.get_player_energy(), self.get_player_max_energy())

    def scroll_background(self) -> None:
        self.bg_y1 += 1
        self.bg_y2 += 1
        if self.bg_y1 >= self.background.get_height():
            self.bg_y1 = -self.background.get_height()
        if self.bg_y2 >= self.background.get_height():
            self.bg_y2 = -self.background.get_height()

    def draw_all(self) -> None:
        self.screen.blit(self.background, (0, self.bg_y1))
        self.screen.blit(self.background, (0, self.bg_y2))
        self.islands.draw(self.screen)
        for sprite in self.all_sprites:
            if isinstance(sprite, (Player, Enemy, Cloud, MiniPlane)):
                self._draw_shadow(sprite.image, sprite.rect)
        for sprite in self.all_sprites:
            if not isinstance(sprite, Island):
                self.screen.blit(sprite.image, sprite.rect)
        self.enemy_bullets.draw(self.screen)
        self._draw_hud()
        pygame.display.flip()
