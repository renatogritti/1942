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
from typing import Dict, Any, Tuple

from src.config import *
from src.player import Player
from src.enemy import Enemy
from src.effects import BombEffect, Explosion, Cloud, GifExplosion
from src.bullet import Bullet, EnemyBullet
from src.coin import Coin
from src.island import Island


def bullet_hit_enemy_bullet(player_bullet: Bullet, enemy_bullet: EnemyBullet) -> bool:
    """
    Callback de colisão para pygame.sprite.groupcollide.

    Esta função é usada para determinar a colisão entre um tiro do jogador e um tiro inimigo.
    Ela infla o retângulo (rect) do tiro inimigo para uma área de colisão maior,
    simulando uma área de impacto mais generosa para o tiro inimigo.

    Args:
        player_bullet (Bullet): O sprite do tiro disparado pelo jogador.
        enemy_bullet (EnemyBullet): O sprite do tiro disparado por um inimigo.

    Returns:
        bool: True se houver colisão entre os retângulos inflados, False caso contrário.
    """
    inflated_rect = enemy_bullet.rect.inflate(20, 20)
    return inflated_rect.colliderect(player_bullet.rect)


class Game:
    """
    Representa a classe principal do jogo 1942 Clone.

    Gerencia o ciclo de vida do jogo, incluindo inicialização, carregamento de recursos,
    loop principal, processamento de eventos, atualização do estado do jogo e renderização.
    """
    def __init__(self) -> None:
        """
        Inicializa o jogo, configurando a tela, carregando recursos e preparando o estado inicial.
        """
        pygame.init()
        pygame.mixer.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1942 Clone")

        self._load_sounds()
        self._show_splash_screen()

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.Font(None, 36)
        self.running: bool = True
        self.score: int = 0
        self.highscore: int = 0
        self.load_highscore()

        self.current_difficulty_index: int = INITIAL_DIFFICULTY_STAGE_INDEX
        self.current_difficulty_settings: Dict[str, Any] = DIFFICULTY_STAGES[self.current_difficulty_index]

        # Grupos de Sprites
        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.clouds: pygame.sprite.Group = pygame.sprite.Group()
        self.islands: pygame.sprite.Group = pygame.sprite.Group()
        self.enemy_bullets: pygame.sprite.Group = pygame.sprite.Group()
        self.coins: pygame.sprite.Group = pygame.sprite.Group()
        self.player: Player = Player(self.all_sprites)
        self.all_sprites.add(self.player)

        self.background: pygame.Surface
        self.bg_y1: int
        self.bg_y2: int
        self._setup_background()

        self.ADD_ENEMY: int
        self.ADD_CLOUD: int
        self.ADD_ISLAND: int
        self._setup_custom_events()
        self.start_game_sounds()

    def _load_sounds(self) -> None:
        """
        Carrega todos os arquivos de som necessários para o jogo.

        Os sons são armazenados em um dicionário para fácil acesso.
        Define o volume para alguns sons.
        """
        self.sounds: Dict[str, pygame.mixer.Sound] = {
            'splash': pygame.mixer.Sound("assets/sounds/Splash.wav"),
            'initial': pygame.mixer.Sound("assets/sounds/Inicial.wav"),
            'motor': pygame.mixer.Sound("assets/sounds/Motor.wav"),
            'explosion': pygame.mixer.Sound("assets/sounds/Explosao.wav"),
            'gameover': pygame.mixer.Sound("assets/sounds/Gameover.wav"),
            'tiro': pygame.mixer.Sound("assets/sounds/Tiro.wav"),
            'coin': pygame.mixer.Sound("assets/sounds/Coin.wav")
        }
        self.sounds['motor'].set_volume(0.3)

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
        self.bg_y1 = 0
        self.bg_y2 = -self.background.get_height()

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

    def start_game_sounds(self) -> None:
        """
        Inicia os sons de fundo do jogo, como a música inicial e o som do motor do avião.
        """
        self.sounds['initial'].play()
        self.sounds['motor'].play(loops=-1)

    def run(self) -> None:
        """
        Inicia o loop principal do jogo.

        Este loop gerencia a execução do jogo, incluindo a taxa de quadros,
        processamento de eventos, atualização do estado e renderização.
        O jogo continua rodando até que `self.running` seja False.
        """
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        self.save_highscore()
        pygame.quit()
        sys.exit()

    def events(self) -> None:
        """
        Processa todos os eventos do Pygame, como entrada do usuário e eventos personalizados.

        Responde a eventos de teclado para tiro, uso de bomba e saída do jogo,
        além de eventos para adicionar inimigos, nuvens e ilhas.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.player.shoot()
                    self.sounds['tiro'].play()
                elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    self.use_bomb()
                elif event.key == pygame.K_q:
                    self.running = False
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
        self.bg_y1 += 1
        self.bg_y2 += 1
        if self.bg_y1 >= self.background.get_height():
            self.bg_y1 = -self.background.get_height()
        if self.bg_y2 >= self.background.get_height():
            self.bg_y2 = -self.background.get_height()

    def _check_collisions(self) -> None:
        """
        Verifica e processa todas as colisões entre os diferentes elementos do jogo.

        Inclui colisões entre tiros do jogador e inimigos, tiros do jogador e tiros inimigos,
        jogador e inimigos, jogador e tiros inimigos, e jogador e moedas.
        """
        # Tiros do jogador com inimigos
        hits: Dict[pygame.sprite.Sprite, Any] = pygame.sprite.groupcollide(self.player.bullets, self.enemies, True, True)
        for enemies_hit in hits.values():
            for enemy in enemies_hit:
                self.score += 10
                self.sounds['explosion'].play()
                # Adiciona ambos os efeitos de explosão
                particle_explosion = Explosion(enemy.rect.center)
                gif_explosion = GifExplosion(enemy.rect.center, size=64)
                self.all_sprites.add(particle_explosion)
                self.all_sprites.add(gif_explosion)
                if random.random() > 0.7:  # 30% de chance de dropar moeda
                    coin = Coin(enemy.rect.center)
                    self.all_sprites.add(coin)
                    self.coins.add(coin)

        # Tiros do jogador com tiros inimigos
        pygame.sprite.groupcollide(self.player.bullets, self.enemy_bullets, True, True, bullet_hit_enemy_bullet)

        # Colisão do jogador com inimigos
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            self.player.energy -= 30
            # Adiciona ambos os efeitos de explosão
            particle_explosion = Explosion(hit.rect.center)
            gif_explosion = GifExplosion(hit.rect.center, size=64)
            self.all_sprites.add(particle_explosion)
            self.all_sprites.add(gif_explosion)
            if self.player.energy <= 0:
                self.save_highscore()
                self._show_game_over_screen()

        # Colisão do jogador com tiros inimigos
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for hit in hits:
            self.player.energy -= 10
            if self.player.energy <= 0:
                self.save_highscore()
                self._show_game_over_screen()

        # Colisão do jogador com moedas
        hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for hit in hits:
            self.sounds['coin'].play()
            self.player.energy = min(self.player.max_energy, self.player.energy + 20)

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

    def draw(self) -> None:
        """
        Desenha todos os elementos do jogo na tela.

        Inclui o fundo, sombras dos sprites, sprites principais, tiros inimigos e a HUD.
        """
        self.screen.blit(self.background, (0, self.bg_y1))
        self.screen.blit(self.background, (0, self.bg_y2))

        # Desenha os elementos de fundo (ilhas)
        self.islands.draw(self.screen)

        # Desenha as sombras dos elementos principais
        for sprite in self.all_sprites:
            if isinstance(sprite, (Player, Enemy, Cloud)):
                self.draw_shadow(sprite.image, sprite.rect)

        # Desenha os sprites principais (exceto ilhas, que já foram desenhadas)
        for sprite in self.all_sprites:
            if not isinstance(sprite, Island):
                self.screen.blit(sprite.image, sprite.rect)

        self.enemy_bullets.draw(self.screen)

        self.draw_hud()
        pygame.display.flip()

    def draw_text(self, text: str, x: int, y: int) -> None:
        """
        Desenha texto na tela em uma posição especificada.

        Args:
            text (str): O texto a ser exibido.
            x (int): A coordenada X superior esquerda para o texto.
            y (int): A coordenada Y superior esquerda para o texto.
        """
        text_surface: pygame.Surface = self.font.render(text, True, WHITE)
        text_rect: pygame.Rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_hud(self) -> None:
        """
        Desenha a interface de usuário (HUD) na tela.

        Exibe informações como pontuação, recorde, barra de energia do jogador e quantidade de bombas.
        """
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"High Score: {self.highscore}", 10, 50)
        self.draw_energy_bar(self.player.energy, self.player.max_energy)
        self.draw_text(f"Bombs: {self.player.bombs}", SCREEN_WIDTH - 120, 50)

    def draw_energy_bar(self, current_energy: int, max_energy: int) -> None:
        """
        Desenha a barra de energia do jogador na tela.

        A cor da barra muda de acordo com o nível de energia.

        Args:
            current_energy (int): A energia atual do jogador.
            max_energy (int): A energia máxima do jogador.
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

    def draw_shadow(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """
        Desenha uma sombra para um sprite, criando um efeito de profundidade.

        Args:
            surface (pygame.Surface): A superfície do sprite a ser sombreada.
            rect (pygame.Rect): O retângulo (posição e tamanho) do sprite.
        """
        shadow_offset: Tuple[int, int] = (15, 25)
        shadow_pos: Tuple[int, int] = (rect.x + shadow_offset[0], rect.y + shadow_offset[1])
        shadow_image: pygame.Surface = surface.copy()
        shadow_image.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(shadow_image, shadow_pos)

    def _show_splash_screen(self) -> None:
        """
        Exibe a tela de splash inicial com o logo do jogo e aguarda uma tecla ser pressionada.

        Toca o som de splash e redimensiona as imagens para se ajustarem à tela.
        """
        self.sounds['splash'].play()
        splash_image: pygame.Surface = pygame.image.load("assets/images/Splash.jpg").convert()
        splash_image = pygame.transform.scale(splash_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        logo_image: pygame.Surface = pygame.image.load("assets/images/Logo.png").convert_alpha()
        logo_width: int = int(SCREEN_WIDTH * 0.5)
        logo_height: int = int(logo_image.get_height() * (logo_width / logo_image.get_width()))
        logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_rect: pygame.Rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(splash_image, (0, 0))
        self.screen.blit(logo_image, logo_rect)
        pygame.display.flip()
        waiting_for_key: bool = True
        while waiting_for_key:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting_for_key = False
        self.sounds['splash'].stop()

    def _show_game_over_screen(self) -> None:
        """
        Exibe a tela de Game Over, mostrando a pontuação final, o recorde e opções para um novo jogo ou sair.

        Para a música do jogo, toca o som de game over e aguarda a entrada do usuário.
        """
        pygame.mixer.stop()
        self.sounds['gameover'].play()
        self.screen.fill(BLACK)
        logo_image: pygame.Surface = pygame.image.load("assets/images/Logo.png").convert_alpha()
        logo_width: int = int(SCREEN_WIDTH * 0.6)
        logo_height: int = int(logo_image.get_height() * (logo_width / logo_image.get_width()))
        logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_rect: pygame.Rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(logo_image, logo_rect)
        score_text: pygame.Surface = self.font.render(f"YOUR SCORE: {self.score}", True, WHITE)
        score_rect: pygame.Rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        highscore_text: pygame.Surface = self.font.render(f"HIGH SCORE: {self.highscore}", True, WHITE)
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
                        self._reset_game()
                        waiting_for_input = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def _reset_game(self) -> None:
        """
        Reinicia o estado do jogo para uma nova partida.

        Limpa todos os grupos de sprites, redefine a pontuação e a energia do jogador,
        e reinicia os sons do jogo.
        """
        self.score = 0
        self.player.energy = self.player.max_energy
        self.all_sprites.empty()
        self.enemies.empty()
        self.clouds.empty()
        self.islands.empty()
        self.enemy_bullets.empty()
        self.coins.empty()
        self.all_sprites.add(self.player)
        self.start_game_sounds()

    def load_highscore(self) -> None:
        """
        Carrega o recorde de pontuação de um arquivo.

        Se o arquivo não existir ou o conteúdo for inválido, o recorde é definido como 0.
        """
        try:
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read())
        except (FileNotFoundError, ValueError):
            self.highscore = 0

    def save_highscore(self) -> None:
        """
        Salva a pontuação atual como novo recorde se for maior que o recorde existente.

        O recorde é salvo em um arquivo de texto.
        """
        if self.score > self.highscore:
            with open("highscore.txt", "w") as f:
                f.write(str(self.score))

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


if __name__ == "__main__":
    game = Game()
    game.run()
