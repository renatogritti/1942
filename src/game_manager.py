import pygame
import sys
from typing import Any

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from src.screens.splash_screen import SplashScreen
from src.screens.game_over_screen import GameOverScreen
from src.managers.sound_manager import SoundManager
from src.managers.score_manager import ScoreManager
from src.game_scene import GameScene # Importar a GameScene

class GameManager:
    """
    Gerencia o ciclo de vida geral do jogo, incluindo inicialização, loop principal
    e transições entre diferentes cenas (splash, jogo, game over).
    """
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1942 Clone")

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.Font(None, 36)
        self.running: bool = True

        self.sound_manager: SoundManager = SoundManager()
        self.score_manager: ScoreManager = ScoreManager()

        self.current_scene: Any = None # Será a cena ativa (SplashScreen, GameScene, GameOverScreen)
        self.game_scene_instance: GameScene = None # Para manter a instância da GameScene

        self._setup_initial_scene()

    def _setup_initial_scene(self) -> None:
        """
        Configura a cena inicial do jogo (Splash Screen).
        """
        splash_screen = SplashScreen(self.screen, self.sound_manager)
        splash_screen.show() # A SplashScreen tem seu próprio loop, então ela bloqueia até terminar
        self.change_scene("game") # Após a splash, vai para a cena do jogo

    def change_scene(self, scene_name: str) -> None:
        """
        Muda a cena atual do jogo.

        Args:
            scene_name (str): O nome da cena para a qual mudar ("game", "game_over", "quit").
        """
        if scene_name == "game":
            # Cria uma nova instância de GameScene
            self.game_scene_instance = GameScene(self.screen, self.font, self.sound_manager, self.score_manager, self.change_scene)
            self.current_scene = self.game_scene_instance
        elif scene_name == "game_over":
            # A GameOverScreen precisa de callbacks para pontuação e reset do jogo
            game_over_screen = GameOverScreen(self.screen, self.font, self.sound_manager, 
                                                self.game_scene_instance._get_score, self.score_manager.get_highscore, 
                                                self._reset_game_and_switch_to_game_scene)
            game_over_screen.show() # GameOverScreen também tem seu próprio loop
            self.running = False # Se o jogo acabou e o usuário não reiniciou, sair
        elif scene_name == "quit":
            self.running = False
        else:
            print(f"Cena desconhecida: {scene_name}")
            self.running = False

    def _reset_game_and_switch_to_game_scene(self) -> None:
        """
        Callback para reiniciar o jogo a partir da tela de Game Over.
        """
        if self.game_scene_instance:
            self.game_scene_instance._reset_game()
        self.change_scene("game")

    def run(self) -> None:
        """
        Inicia o loop principal do GameManager.
        """
        while self.running:
            self.clock.tick(FPS)
            
            if self.current_scene:
                # As cenas agora têm seus próprios métodos handle_events, update e draw
                self.current_scene.handle_events()
                self.current_scene.update()
                self.current_scene.draw()
            
            # pygame.display.flip() # Já é chamado dentro do draw da cena

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
