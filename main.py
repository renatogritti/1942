import pygame
import sys
import random
from src.config import *
from src.player import Player
from src.enemy import Enemy
from src.effects import BombEffect, Explosion, Cloud
from src.bullet import EnemyBullet
from src.coin import Coin
from src.island import Island

def bullet_hit_enemy_bullet(player_bullet, enemy_bullet):
    """Callback de colisão para pygame.sprite.groupcollide que infla o rect do tiro inimigo."""
    inflated_rect = enemy_bullet.rect.inflate(20, 20)
    return inflated_rect.colliderect(player_bullet.rect)

class Game:
    """Representa a classe principal do jogo 1942 Clone."""
    def __init__(self):
        """Inicializa o jogo, configurando a tela, carregando recursos e preparando o estado inicial."""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1942 Clone")

        self._load_sounds()
        self._show_splash_screen()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.score = 0
        self.load_highscore()

        self.current_difficulty_index = INITIAL_DIFFICULTY_STAGE_INDEX
        self.current_difficulty_settings = DIFFICULTY_STAGES[self.current_difficulty_index]

        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.islands = pygame.sprite.Group()  # Grupo para ilhas
        self.enemy_bullets = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.player = Player(self.all_sprites)
        self.all_sprites.add(self.player)

        self._setup_background()
        self._setup_custom_events()
        self.start_game_sounds()

    def _load_sounds(self):
        """Carrega todos os sons do jogo."""
        self.sounds = {
            'splash': pygame.mixer.Sound("assets/sounds/Splash.wav"),
            'initial': pygame.mixer.Sound("assets/sounds/Inicial.wav"),
            'motor': pygame.mixer.Sound("assets/sounds/Motor.wav"),
            'explosion': pygame.mixer.Sound("assets/sounds/Explosao.wav"),
            'gameover': pygame.mixer.Sound("assets/sounds/Gameover.wav"),
            'tiro': pygame.mixer.Sound("assets/sounds/Tiro.wav"),
            'coin': pygame.mixer.Sound("assets/sounds/Coin.wav")
        }
        self.sounds['motor'].set_volume(0.3)

    def _setup_background(self):
        """Configura o fundo rolável."""
        bg_tile = pygame.image.load("assets/images/fundo.png").convert()
        tile_width = bg_tile.get_width()
        tile_height = bg_tile.get_height()
        self.background = pygame.Surface((SCREEN_WIDTH, tile_height))
        for x in range(0, SCREEN_WIDTH, tile_width):
            self.background.blit(bg_tile, (x, 0))
        self.bg_y1 = 0
        self.bg_y2 = -self.background.get_height()

    def _setup_custom_events(self):
        """Configura os eventos personalizados do jogo."""
        self.ADD_ENEMY = pygame.USEREVENT + 1
        min_delay, max_delay = self.current_difficulty_settings["enemy_spawn_delay"]
        pygame.time.set_timer(self.ADD_ENEMY, random.randint(min_delay, max_delay))
        self.ADD_CLOUD = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ADD_CLOUD, 1500)
        self.ADD_ISLAND = pygame.USEREVENT + 3
        pygame.time.set_timer(self.ADD_ISLAND, random.randint(5000, 10000))

    def start_game_sounds(self):
        """Inicia os sons do jogo."""
        self.sounds['initial'].play()
        self.sounds['motor'].play(loops=-1)

    def run(self):
        """Inicia o loop principal do jogo."""
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        self.save_highscore()
        pygame.quit()
        sys.exit()

    def events(self):
        """Processa todos os eventos do Pygame."""
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

    def update(self):
        """Atualiza o estado de todos os elementos do jogo."""
        player_pos = self.player.rect.center
        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy):
                sprite.update(player_pos)
            else:
                sprite.update()

        self._scroll_background()
        self._check_collisions()
        self._update_difficulty()

    def _scroll_background(self):
        """Move o fundo para criar um efeito de rolagem."""
        self.bg_y1 += 1
        self.bg_y2 += 1
        if self.bg_y1 >= self.background.get_height():
            self.bg_y1 = -self.background.get_height()
        if self.bg_y2 >= self.background.get_height():
            self.bg_y2 = -self.background.get_height()

    def _check_collisions(self):
        """Verifica todas as colisões do jogo."""
        # Tiros do jogador com inimigos
        hits = pygame.sprite.groupcollide(self.player.bullets, self.enemies, True, True)
        for enemies_hit in hits.values():
            for enemy in enemies_hit:
                self.score += 10
                self.sounds['explosion'].play()
                explosion = Explosion(enemy.rect.center)
                self.all_sprites.add(explosion)
                if random.random() > 0.7: # 30% de chance
                    coin = Coin(enemy.rect.center)
                    self.all_sprites.add(coin)
                    self.coins.add(coin)

        # Tiros do jogador com tiros inimigos
        pygame.sprite.groupcollide(self.player.bullets, self.enemy_bullets, True, True, bullet_hit_enemy_bullet)

        # Colisão do jogador com inimigos
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            self.player.energy -= 30
            explosion = Explosion(hit.rect.center)
            self.all_sprites.add(explosion)
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

    def _update_difficulty(self):
        """Atualiza a dificuldade do jogo com base na pontuação."""
        if self.current_difficulty_index + 1 < len(DIFFICULTY_STAGES):
            next_stage_threshold = DIFFICULTY_STAGES[self.current_difficulty_index + 1]["score_threshold"]
            if self.score >= next_stage_threshold:
                self.current_difficulty_index += 1
                self.current_difficulty_settings = DIFFICULTY_STAGES[self.current_difficulty_index]
                min_delay, max_delay = self.current_difficulty_settings["enemy_spawn_delay"]
                pygame.time.set_timer(self.ADD_ENEMY, random.randint(min_delay, max_delay))

    def draw(self):
        """Desenha todos os elementos do jogo na tela."""
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

    def draw_text(self, text, x, y):
        """Desenha texto na tela."""
        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_hud(self):
        """Desenha a interface de usuário (HUD) na tela."""
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"High Score: {self.highscore}", 10, 50)
        self.draw_energy_bar(self.player.energy, self.player.max_energy)
        self.draw_text(f"Bombs: {self.player.bombs}", SCREEN_WIDTH - 120, 50)

    def draw_energy_bar(self, current_energy, max_energy):
        """Desenha a barra de energia do jogador."""
        x = SCREEN_WIDTH // 2 - 100
        y = 10
        width = 200
        height = 20
        fill = (current_energy / max_energy) * width
        outline_rect = pygame.Rect(x, y, width, height)
        fill_rect = pygame.Rect(x, y, fill, height)
        color = (0, 255, 0) # Verde
        if current_energy / max_energy < 0.3:
            color = (255, 0, 0) # Vermelho
        elif current_energy / max_energy < 0.6:
            color = (255, 255, 0) # Amarelo
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, WHITE, outline_rect, 2)

    def draw_shadow(self, surface, rect):
        """Desenha uma sombra para um sprite."""
        shadow_offset = (15, 25)
        shadow_pos = (rect.x + shadow_offset[0], rect.y + shadow_offset[1])
        shadow_image = surface.copy()
        shadow_image.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(shadow_image, shadow_pos)

    def _show_splash_screen(self):
        """Exibe a tela de splash inicial com o logo do jogo e aguarda uma tecla ser pressionada."""
        self.sounds['splash'].play()
        splash_image = pygame.image.load("assets/images/Splash.jpg").convert()
        splash_image = pygame.transform.scale(splash_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        logo_image = pygame.image.load("assets/images/Logo.png").convert_alpha()
        logo_width = int(SCREEN_WIDTH * 0.5)
        logo_height = int(logo_image.get_height() * (logo_width / logo_image.get_width()))
        logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(splash_image, (0, 0))
        self.screen.blit(logo_image, logo_rect)
        pygame.display.flip()
        waiting_for_key = True
        while waiting_for_key:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting_for_key = False
        self.sounds['splash'].stop()

    def _show_game_over_screen(self):
        """Exibe a tela de Game Over, mostrando a pontuação final, o recorde e opções para um novo jogo ou sair."""
        pygame.mixer.stop()
        self.sounds['gameover'].play()
        self.screen.fill(BLACK)
        logo_image = pygame.image.load("assets/images/Logo.png").convert_alpha()
        logo_width = int(SCREEN_WIDTH * 0.6)
        logo_height = int(logo_image.get_height() * (logo_width / logo_image.get_width()))
        logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(logo_image, logo_rect)
        score_text = self.font.render(f"YOUR SCORE: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        highscore_text = self.font.render(f"HIGH SCORE: {self.highscore}", True, WHITE)
        highscore_rect = highscore_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(highscore_text, highscore_rect)
        options_text = self.font.render("Press 'N' for New Game or 'Q' to Quit", True, WHITE)
        options_rect = options_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        self.screen.blit(options_text, options_rect)
        pygame.display.flip()
        waiting_for_input = True
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

    def _reset_game(self):
        """Reinicia o estado do jogo para uma nova partida."""
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

    def load_highscore(self):
        """Carrega o recorde de pontuação."""
        try:
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read())
        except (FileNotFoundError, ValueError):
            self.highscore = 0

    def save_highscore(self):
        """Salva a pontuação atual como novo recorde."""
        if self.score > self.highscore:
            with open("highscore.txt", "w") as f:
                f.write(str(self.score))

    def use_bomb(self):
        """Ativa uma bomba, destruindo todos os inimigos na tela e adicionando pontos ao placar."""
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