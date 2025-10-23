"""
Projeto: Clone 1942
Descrição: Módulo responsável pela tela de splash inicial do jogo.
           Exibe o logo e aguarda a interação do usuário para iniciar o jogo.
Autoria: Renato Gritti
"""

import pygame
import sys
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE
from src.managers.sound_manager import SoundManager # Importa SoundManager
from typing import Dict, Any

class SplashScreen:
    """
    Representa a tela de splash inicial do jogo.

    Esta tela exibe o logo do jogo e aguarda uma tecla ser pressionada para continuar.
    """
    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager) -> None:
        """
        Inicializa a tela de splash.

        Args:
            screen (pygame.Surface): A superfície da tela do Pygame onde a splash screen será desenhada.
            sound_manager (SoundManager): A instância do SoundManager para gerenciar os sons.
        """
        self.screen = screen
        self.sound_manager = sound_manager
        self.splash_image = pygame.image.load("assets/images/Splash.jpg").convert()
        self.splash_image = pygame.transform.scale(self.splash_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.logo_image = pygame.image.load("assets/images/Logo.png").convert_alpha()
        
        logo_width = int(SCREEN_WIDTH * 0.5)
        logo_height = int(self.logo_image.get_height() * (logo_width / self.logo_image.get_width()))
        self.logo_image = pygame.transform.scale(self.logo_image, (logo_width, logo_height))
        self.logo_rect = self.logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def show(self) -> None:
        """
        Exibe a tela de splash e aguarda a interação do usuário.

        Toca o som de splash e entra em um loop de eventos até que uma tecla seja pressionada
        ou o jogo seja encerrado.
        """
        self.sound_manager.play_sound('splash')
        self.screen.blit(self.splash_image, (0, 0))
        self.screen.blit(self.logo_image, self.logo_rect)
        pygame.display.flip()
        
        waiting_for_key: bool = True
        while waiting_for_key:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting_for_key = False
        self.sound_manager.stop_sound('splash')
