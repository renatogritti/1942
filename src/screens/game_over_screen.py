"""
Projeto: Clone 1942
Descrição: Módulo responsável pela tela de Game Over do jogo.
           Exibe a pontuação final, o recorde e opções para o jogador iniciar um novo jogo ou sair.
Autoria: Renato Gritti
"""

import pygame
import sys
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE
from src.managers.sound_manager import SoundManager # Importa SoundManager
from typing import Callable, Tuple

class GameOverScreen:
    """
    Representa a tela de Game Over do jogo.

    Esta tela exibe a pontuação final do jogador, o recorde e oferece opções para
    reiniciar o jogo ou sair.
    """
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, sound_manager: SoundManager, get_score: Callable[[], int], get_highscore: Callable[[], int], reset_game_callback: Callable[[], None]) -> None:
        """
        Inicializa a tela de Game Over.

        Args:
            screen (pygame.Surface): A superfície da tela do Pygame.
            font (pygame.font.Font): A fonte a ser usada para renderizar o texto.
            sound_manager (SoundManager): A instância do SoundManager para gerenciar os sons.
            get_score (Callable[[], int]): Uma função de callback para obter a pontuação atual.
            get_highscore (Callable[[], int]): Uma função de callback para obter o recorde.
            reset_game_callback (Callable[[], None]): Uma função de callback para reiniciar o jogo.
        """
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.get_score = get_score
        self.get_highscore = get_highscore
        self.reset_game_callback = reset_game_callback

        self.logo_image = pygame.image.load("assets/images/Logo.png").convert_alpha()
        logo_width: int = int(SCREEN_WIDTH * 0.6)
        logo_height: int = int(self.logo_image.get_height() * (logo_width / self.logo_image.get_width()))
        self.logo_image = pygame.transform.scale(self.logo_image, (logo_width, logo_height))
        self.logo_rect = self.logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

    def show(self) -> None:
        """
        Exibe a tela de Game Over e aguarda a entrada do usuário.

        Para a música do jogo, toca o som de game over e entra em um loop de eventos
        até que o jogador escolha reiniciar ou sair.
        """
        self.sound_manager.stop_all_sounds() # Para todos os sons antes de tocar o de game over
        self.sound_manager.play_sound('gameover')
        self.screen.fill(BLACK)
        self.screen.blit(self.logo_image, self.logo_rect)

        score_text: pygame.Surface = self.font.render(f"YOUR SCORE: {self.get_score()}", True, WHITE)
        score_rect: pygame.Rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        highscore_text: pygame.Surface = self.font.render(f"HIGH SCORE: {self.get_highscore()}", True, WHITE)
        highscore_rect: pygame.Rect = highscore_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(highscore_text, highscore_rect)

        options_text: pygame.Surface = self.font.render("Press 'N' for New Game or 'Q' to Quit", True, WHITE)
        options_rect: pygame.Rect = options_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        self.screen.blit(options_text, options_rect)

        pygame.display.flip()

        waiting_for_input: bool = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        self.reset_game_callback()
                        waiting_for_input = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
