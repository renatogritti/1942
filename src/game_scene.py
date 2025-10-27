"""
Projeto: Clone 1942
Descrição: Este projeto é um clone do clássico jogo 1942, desenvolvido em Python utilizando a biblioteca Pygame.
           O jogo simula combates aéreos, com o jogador controlando um avião para abater inimigos, coletar moedas
           e evitar colisões. Inclui sistema de pontuação, recorde, diferentes níveis de dificuldade e efeitos visuais.
Autoria: Renato Gritti
"""

import pygame
import sys
import random
from typing import Dict, Any, Tuple, Callable

from src.config import *
from src.game_objects.player import Player
from src.game_objects.enemy import Enemy
from src.game_objects.effects import BombEffect, Explosion, Cloud, GifExplosion
from src.game_objects.bullet import Bullet, EnemyBullet
from src.game_objects.coin import Coin
from src.game_objects.island import Island
from src.game_objects.powerups import BombPowerUp, AmmoPowerUp # Novo import
from src.screens.game_over_screen import GameOverScreen
from src.screens.phase_screen import PhaseScreen
from src.managers.sound_manager import SoundManager
from src.managers.score_manager import ScoreManager
from src.managers.collision_manager import CollisionManager
from src.managers.render_manager import RenderManager

class GameScene:
    """
    Representa a cena principal do jogo 1942 Clone.

    Gerencia o ciclo de vida do jogo, incluindo inicialização, carregamento de recursos,
    loop principal, processamento de eventos, atualização do estado do jogo e renderização.
    """
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, 
                 sound_manager: SoundManager, score_manager: ScoreManager,
                 change_scene_callback: Callable[[str], None]) -> None:
        """
        Inicializa a cena do jogo, configurando a tela, carregando recursos e preparando o estado inicial.
        """
        self.screen = screen
        self.font = font
        self.sound_manager = sound_manager
        self.score_manager = score_manager
        self.change_scene_callback = change_scene_callback

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True # Esta variável agora controla o loop interno da cena, não o loop principal do jogo
        self.score: int = 0

        self.current_difficulty_index: int = INITIAL_DIFFICULTY_STAGE_INDEX
        self.current_difficulty_settings: Dict[str, Any] = DIFFICULTY_STAGES[self.current_difficulty_index]

        # Grupos de Sprites
        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.clouds: pygame.sprite.Group = pygame.sprite.Group()
        self.islands: pygame.sprite.Group = pygame.sprite.Group()
        self.enemy_bullets: pygame.sprite.Group = pygame.sprite.Group()
        self.coins: pygame.sprite.Group = pygame.sprite.Group()
        self.powerups: pygame.sprite.Group = pygame.sprite.Group() # Novo grupo
        self.player: Player = Player(self.all_sprites)
        self.all_sprites.add(self.player)

        # Inicializa o CollisionManager
        self.collision_manager = CollisionManager(
            all_sprites_group=self.all_sprites,
            player_bullets_group=self.player.bullets,
            enemies_group=self.enemies,
            enemy_bullets_group=self.enemy_bullets,
            coins_group=self.coins,
            powerups_group=self.powerups, # Passa o novo grupo
            sound_manager=self.sound_manager,
            score_callback=self._add_score,
            game_over_callback=self._handle_game_over,
            player_instance=self.player
        )

        self.background: pygame.Surface
        self._setup_background()

        # Inicializa o RenderManager
        self.render_manager = RenderManager(
            screen=self.screen,
            font=self.font,
            all_sprites_group=self.all_sprites,
            islands_group=self.islands,
            enemy_bullets_group=self.enemy_bullets,
            background_surface=self.background,
            get_score=self._get_score,
            get_highscore=self._get_highscore,
            get_player_energy=self._get_player_energy,
            get_player_max_energy=self._get_player_max_energy,
            get_player_bombs=self._get_player_bombs
        )

        self.ADD_ENEMY: int
        self.ADD_CLOUD: int
        self.ADD_ISLAND: int
        self._setup_custom_events()
        # Initial call to show phase screen for the first phase
        self._show_phase_screen(initial_call=True)

    def _show_phase_screen(self, initial_call: bool = False) -> None:
        """
        Exibe a tela de informações da fase.
        """
        if not initial_call:
            self.sound_manager.stop_all_sounds()

        phase_screen = PhaseScreen(
            self.screen,
            self.font,
            self.sound_manager,
            self.current_difficulty_settings,
            self.current_difficulty_index + 1
        )
        phase_screen.show()
        self.start_game_sounds(is_initial_call=initial_call)

    def _setup_background(self) -> None:
        """
        Configura o fundo rolável do jogo.

        Carrega a imagem de fundo e a prepara para criar um efeito de rolagem contínua.
        """
        bg_tile: pygame.Surface = pygame.image.load("assets/images/fundo.png").convert()
        tile_width: int = bg_tile.get_width()
        tile_height: int = bg_tile.get_height()
        self.background = pygame.Surface((SCREEN_WIDTH, tile_height))
        for x in range(0, SCREEN_WIDTH, tile_width):
            self.background.blit(bg_tile, (x, 0))

    def _setup_custom_events(self) -> None:
        """
        Configura os eventos personalizados do jogo, como a adição de inimigos, nuvens e ilhas.

        Define temporizadores para disparar esses eventos em intervalos aleatórios ou fixos.
        """
        self.ADD_ENEMY = pygame.USEREVENT + 1
        min_delay, max_delay = self.current_difficulty_settings["enemy_spawn_delay"]
        pygame.time.set_timer(self.ADD_ENEMY, random.randint(min_delay, max_delay))
        self.ADD_CLOUD = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ADD_CLOUD, 1500)
        self.ADD_ISLAND = pygame.USEREVENT + 3
        pygame.time.set_timer(self.ADD_ISLAND, random.randint(5000, 10000))

    def start_game_sounds(self, is_initial_call: bool = False) -> None:
        """
        Inicia os sons de fundo do jogo, como a música inicial e o som do motor do avião.
        """
        if is_initial_call:
            self.sound_manager.play_background_music("assets/sounds/Music.mid", loops=-1, volume=0.2)
        self.sound_manager.play_sound('initial')
        self.sound_manager.play_sound('motor', loops=-1)

    def handle_events(self) -> None:
        """
        Processa todos os eventos do Pygame, como entrada do usuário e eventos personalizados.

        Responde a eventos de teclado para tiro, uso de bomba e saída do jogo,
        além de eventos para adicionar inimigos, nuvens e ilhas.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False # Sinaliza para o GameManager que esta cena deve terminar
                self.change_scene_callback("quit") # Sinaliza para o GameManager sair
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.player.shoot()
                    self.sound_manager.play_sound('tiro')
                elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    self.use_bomb()
                elif event.key == pygame.K_q:
                    self.running = False # Sinaliza para o GameManager que esta cena deve terminar
                    self.change_scene_callback("quit") # Sinaliza para o GameManager sair
            elif event.type == self.ADD_ENEMY:
                new_enemy = Enemy(self, self.current_difficulty_settings)
                self.enemies.add(new_enemy)
                self.all_sprites.add(new_enemy)
            elif event.type == self.ADD_CLOUD:
                new_cloud = Cloud()
                self.clouds.add(new_cloud)
                self.all_sprites.add(new_cloud)
            elif event.type == self.ADD_ISLAND:
                new_island = Island()
                self.islands.add(new_island)
                self.all_sprites.add(new_island)

    def update(self) -> None:
        """
        Atualiza o estado de todos os elementos do jogo.

        Isso inclui a movimentação de sprites, rolagem do fundo,
        verificação de colisões e ajuste da dificuldade do jogo.
        """
        player_pos: Tuple[int, int] = self.player.rect.center
        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy):
                sprite.update(player_pos)
            else:
                sprite.update()

        self._scroll_background()
        self._check_collisions()
        self._update_difficulty()

    def _scroll_background(self) -> None:
        """
        Move o fundo para criar um efeito de rolagem vertical contínua.

        Ajusta as posições Y das duas cópias do fundo para simular um movimento infinito.
        """
        self.render_manager.scroll_background()

    def _add_score(self, points: int) -> None:
        """
        Adiciona pontos à pontuação atual do jogo.
        """
        self.score += points

    def _handle_game_over(self) -> None:
        """
        Gerencia a lógica de fim de jogo, salvando o recorde e exibindo a tela de Game Over.
        """
        self.sound_manager.stop_all_sounds()
        self.sound_manager.stop_background_music()
        self.score_manager.save_highscore(self.score)
        self.change_scene_callback("game_over") # Sinaliza para o GameManager mudar para a tela de Game Over
        self.running = False # Termina o loop interno desta cena

    def _check_collisions(self) -> None:
        """
        Verifica e processa todas as colisões entre os diferentes elementos do jogo.
        Agora delegada ao CollisionManager.
        """
        self.collision_manager.check_all_collisions()

    def _update_difficulty(self) -> None:
        """
        Atualiza a dificuldade do jogo com base na pontuação atual do jogador.

        Avança para o próximo estágio de dificuldade quando a pontuação atinge um limiar,
        ajustando parâmetros como a frequência de surgimento de inimigos.
        """
        if self.current_difficulty_index + 1 < len(DIFFICULTY_STAGES):
            next_stage_threshold: int = DIFFICULTY_STAGES[self.current_difficulty_index + 1]["score_threshold"]
            if self.score >= next_stage_threshold:
                self.current_difficulty_index += 1
                self.current_difficulty_settings = DIFFICULTY_STAGES[self.current_difficulty_index]
                min_delay, max_delay = self.current_difficulty_settings["enemy_spawn_delay"]
                pygame.time.set_timer(self.ADD_ENEMY, random.randint(min_delay, max_delay))
                self._show_phase_screen()

    # Métodos getters para o RenderManager
    def _get_score(self) -> int:
        return self.score

    def _get_highscore(self) -> int:
        return self.score_manager.get_highscore()

    def _get_player_energy(self) -> int:
        return self.player.energy

    def _get_player_max_energy(self) -> int:
        return self.player.max_energy

    def _get_player_bombs(self) -> int:
        return self.player.bombs

    def draw(self) -> None:
        """
        Desenha todos os elementos do jogo na tela.
        Agora delegada ao RenderManager.
        """
        self.render_manager.draw_all()

    def _reset_game(self) -> None:
        """
        Reinicia o estado do jogo para uma nova partida.

        Limpa todos os grupos de sprites, redefine a pontuação e a energia do jogador,
        e reinicia os sons do jogo.
        """
        self.score = 0
        self.player.reset()
        self.all_sprites.empty()
        self.enemies.empty()
        self.clouds.empty()
        self.islands.empty()
        self.enemy_bullets.empty()
        self.coins.empty()
        self.powerups.empty() # Limpa os powerups
        self.all_sprites.add(self.player)
        self.start_game_sounds()

    def use_bomb(self) -> None:
        """
        Ativa uma bomba, destruindo todos os inimigos visíveis na tela e adicionando pontos ao placar.

        Consome uma bomba do inventário do jogador e aciona um efeito visual de explosão.
        """
        if self.player.bombs > 0:
            self.player.bombs -= 1
            bomb_effect = BombEffect(self.screen.get_rect().center)
            self.all_sprites.add(bomb_effect)
            for enemy in self.enemies:
                enemy.kill()
                self.score += 5
