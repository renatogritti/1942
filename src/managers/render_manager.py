import pygame
from typing import Any, Tuple, Callable
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from src.game_objects.player import Player
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
        self.font = font
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

    def _draw_text(self, text: str, x: int, y: int) -> None:
        """
        Desenha texto na tela em uma posição especificada.
        """
        text_surface: pygame.Surface = self.font.render(text, True, WHITE)
        text_rect: pygame.Rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)

    def _draw_energy_bar(self, current_energy: int, max_energy: int) -> None:
        """
        Desenha a barra de energia do jogador na tela.
        A cor da barra muda de acordo com o nível de energia.
        """
        x: int = SCREEN_WIDTH // 2 - 100
        y: int = 10
        width: int = 200
        height: int = 20
        fill: float = (current_energy / max_energy) * width
        outline_rect: pygame.Rect = pygame.Rect(x, y, width, height)
        fill_rect: pygame.Rect = pygame.Rect(x, y, fill, height)
        color: Tuple[int, int, int] = (0, 255, 0)  # Verde
        if current_energy / max_energy < 0.3:
            color = (255, 0, 0)  # Vermelho
        elif current_energy / max_energy < 0.6:
            color = (255, 255, 0)  # Amarelo
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, WHITE, outline_rect, 2)

    def _draw_shadow(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """
        Desenha uma sombra para um sprite, criando um efeito de profundidade.
        """
        shadow_offset: Tuple[int, int] = (15, 25)
        shadow_pos: Tuple[int, int] = (rect.x + shadow_offset[0], rect.y + shadow_offset[1])
        shadow_image: pygame.Surface = surface.copy()
        shadow_image.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(shadow_image, shadow_pos)

    def _draw_hud(self) -> None:
        """
        Desenha a interface de usuário (HUD) na tela.
        Exibe informações como pontuação, recorde, barra de energia do jogador e quantidade de bombas.
        """
        self._draw_text(f"Score: {self.get_score()}", 10, 10)
        self._draw_text(f"High Score: {self.get_highscore()}", 10, 50)
        self._draw_energy_bar(self.get_player_energy(), self.get_player_max_energy())
        self._draw_text(f"Bombs: {self.get_player_bombs()}", SCREEN_WIDTH - 120, 50)

    def scroll_background(self) -> None:
        """
        Move o fundo para criar um efeito de rolagem vertical contínua.
        Ajusta as posições Y das duas cópias do fundo para simular um movimento infinito.
        """
        self.bg_y1 += 1
        self.bg_y2 += 1
        if self.bg_y1 >= self.background.get_height():
            self.bg_y1 = -self.background.get_height()
        if self.bg_y2 >= self.background.get_height():
            self.bg_y2 = -self.background.get_height()

    def draw_all(self) -> None:
        """
        Desenha todos os elementos do jogo na tela.
        """
        self.screen.blit(self.background, (0, self.bg_y1))
        self.screen.blit(self.background, (0, self.bg_y2))

        # Desenha os elementos de fundo (ilhas)
        self.islands.draw(self.screen)

        # Desenha as sombras dos elementos principais
        for sprite in self.all_sprites:
            if isinstance(sprite, (Player, Enemy, Cloud)):
                self._draw_shadow(sprite.image, sprite.rect)

        # Desenha os sprites principais (exceto ilhas, que já foram desenhadas)
        for sprite in self.all_sprites:
            if not isinstance(sprite, Island):
                self.screen.blit(sprite.image, sprite.rect)

        self.enemy_bullets.draw(self.screen)

        self._draw_hud()
        pygame.display.flip()
