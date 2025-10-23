import pygame
import sys
import random
from src.config import *
from src.player import Player
from src.enemy import Enemy
from src.effects import BombEffect, Explosion, Cloud
from src.bullet import EnemyBullet # Import EnemyBullet

def bullet_hit_enemy_bullet(player_bullet, enemy_bullet):
    """Callback de colisão para pygame.sprite.groupcollide que infla o rect do tiro inimigo."""
    # Aumenta a área de colisão do tiro inimigo em 10 pixels em cada direção
    inflated_rect = enemy_bullet.rect.inflate(20, 20)
    return inflated_rect.colliderect(player_bullet.rect)

class Game:
    """Representa a classe principal do jogo 1942 Clone. Gerencia o ciclo de vida do jogo, estados, sprites e interações."""
    def __init__(self):
        """Inicializa o jogo, configurando a tela, carregando recursos e preparando o estado inicial."""
        pygame.init()
        pygame.mixer.init() # Initialize the mixer
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("1942 Clone")

        self._load_sounds()
        self._show_splash_screen()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.score = 0
        self.load_highscore()

        # Difficulty Management
        self.current_difficulty_index = INITIAL_DIFFICULTY_STAGE_INDEX
        self.current_difficulty_settings = DIFFICULTY_STAGES[self.current_difficulty_index]

        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group() # Initialize enemy_bullets group
        self.player = Player(self.all_sprites)
        self.all_sprites.add(self.player)

        # --- Background Creation ---
        # Load the background image, which is a tileable vertical strip
        bg_tile = pygame.image.load("assets/images/fundo.png").convert()
        tile_width = bg_tile.get_width()
        tile_height = bg_tile.get_height()

        # Create a new background surface with the full screen width
        self.background = pygame.Surface((SCREEN_WIDTH, tile_height))

        # Tile the image across the entire new background
        for x in range(0, SCREEN_WIDTH, tile_width):
            self.background.blit(bg_tile, (x, 0))

        self.bg_y1 = 0
        self.bg_y2 = -self.background.get_height()

        # Custom Events
        self.ADD_ENEMY = pygame.USEREVENT + 1
        # Use current difficulty settings for initial enemy spawn timer
        min_delay, max_delay = self.current_difficulty_settings["enemy_spawn_delay"]
        pygame.time.set_timer(self.ADD_ENEMY, random.randint(min_delay, max_delay))

        self.ADD_CLOUD = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ADD_CLOUD, 1500)
        
        self.start_game_sounds()

    def _load_sounds(self):
        """Carrega todos os sons do jogo."""
        self.sounds = {
            'splash': pygame.mixer.Sound("assets/sounds/Splash.wav"),
            'initial': pygame.mixer.Sound("assets/sounds/Inicial.wav"),
            'motor': pygame.mixer.Sound("assets/sounds/Motor.wav"),
            'explosion': pygame.mixer.Sound("assets/sounds/Explosao.wav"),
            'gameover': pygame.mixer.Sound("assets/sounds/Gameover.wav")
        }

    def start_game_sounds(self):
        """Inicia os sons do jogo."""
        self.sounds['initial'].play()
        self.sounds['motor'].play(loops=-1)

    def load_highscore(self):
        """Carrega o recorde de pontuação do arquivo 'highscore.txt'. Se o arquivo não existir ou estiver vazio, o recorde é 0."""
        try:
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read())
        except (FileNotFoundError, ValueError):
            self.highscore = 0

    def save_highscore(self):
        """Salva a pontuação atual como novo recorde se for maior que o recorde anterior."""
        if self.score > self.highscore:
            with open("highscore.txt", "w") as f:
                f.write(str(self.score))

    def run(self):
        """Inicia o loop principal do jogo, processando eventos, atualizando o estado e desenhando na tela."""
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        self.save_highscore()
        pygame.quit()
        sys.exit()

    def use_bomb(self):
        """Ativa uma bomba, destruindo todos os inimigos na tela e adicionando pontos ao placar."""
        if self.player.bombs > 0:
            self.player.bombs -= 1
            # Create the visual effect
            bomb_effect = BombEffect(self.screen.get_rect().center)
            self.all_sprites.add(bomb_effect)
            # Destroy all enemies and add to score
            for enemy in self.enemies:
                enemy.kill()
                self.score += 5 # Give some points for bomb kills

    def events(self):
        """Processa todos os eventos do Pygame, como entrada do usuário e eventos personalizados."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.player.shoot()
                elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    self.use_bomb()
                elif event.key == pygame.K_q:
                    self.running = False
            elif event.type == self.ADD_ENEMY:
                new_enemy = Enemy(self, self.current_difficulty_settings) # Pass game instance and difficulty settings to Enemy
                self.enemies.add(new_enemy)
                self.all_sprites.add(new_enemy)
            elif event.type == self.ADD_CLOUD:
                new_cloud = Cloud()
                self.clouds.add(new_cloud)
                self.all_sprites.add(new_cloud)

    def update(self):
        """Atualiza o estado de todos os elementos do jogo, incluindo movimento, colisões e dificuldade."""
        # Check and update difficulty stage
        if self.current_difficulty_index + 1 < len(DIFFICULTY_STAGES):
            next_stage_threshold = DIFFICULTY_STAGES[self.current_difficulty_index + 1]["score_threshold"]
            if self.score >= next_stage_threshold:
                self.current_difficulty_index += 1
                self.current_difficulty_settings = DIFFICULTY_STAGES[self.current_difficulty_index]
                # Reset enemy spawn timer with new difficulty settings
                min_delay, max_delay = self.current_difficulty_settings["enemy_spawn_delay"]
                pygame.time.set_timer(self.ADD_ENEMY, random.randint(min_delay, max_delay))

        player_pos = self.player.rect.center # Get player's current position

        # Update all sprites, passing player_pos only to Enemy instances
        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy):
                sprite.update(player_pos)
            else:
                sprite.update()

        self.enemy_bullets.update() # Update enemy bullets

        # Scroll background
        self.bg_y1 += 1
        self.bg_y2 += 1
        if self.bg_y1 >= self.background.get_height():
            self.bg_y1 = -self.background.get_height()
        if self.bg_y2 >= self.background.get_height():
            self.bg_y2 = -self.background.get_height()

        # Check for collisions: bullets hitting enemies
        hits = pygame.sprite.groupcollide(self.player.bullets, self.enemies, True, True)
        for enemies_hit in hits.values():
            for enemy in enemies_hit:
                self.score += 10 # Increase score for each hit
                explosion = Explosion(enemy.rect.center)
                self.all_sprites.add(explosion)
                self.sounds['explosion'].play()

        # Check for collisions: player bullets hitting enemy bullets
        pygame.sprite.groupcollide(self.player.bullets, self.enemy_bullets, True, True, bullet_hit_enemy_bullet)

        # Check for collisions: enemies hitting player
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        if hits:
            self.player.lives -= 1
            explosion = Explosion(self.player.rect.center)
            self.all_sprites.add(explosion)
            self.player.reset()
            if self.player.lives <= 0:
                self.save_highscore()
                self._show_game_over_screen()

        # Check for collisions: enemy bullets hitting player
        enemy_bullet_hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if enemy_bullet_hits:
            self.player.lives -= 1
            explosion = Explosion(self.player.rect.center)
            self.all_sprites.add(explosion)
            self.player.reset()
            if self.player.lives <= 0:
                self.save_highscore()
                self._show_game_over_screen()

    def draw_text(self, text, x, y):
        """Desenha texto na tela.

        Args:
            text (str): O texto a ser desenhado.
            x (int): A coordenada X da posição superior esquerda do texto.
            y (int): A coordenada Y da posição superior esquerda do texto.
        """
        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(topleft=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_hud(self):
        """Desenha a interface de usuário (HUD) na tela, incluindo pontuação, recorde, vidas e bombas."""
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"High Score: {self.highscore}", 10, 50)
        self.draw_text(f"Lives: {self.player.lives}", SCREEN_WIDTH - 120, 10)
        self.draw_text(f"Bombs: {self.player.bombs}", SCREEN_WIDTH - 120, 50)

    def draw_shadow(self, surface, rect):
        """Desenha uma sombra para um sprite.

        Args:
            surface (pygame.Surface): A superfície do sprite.
            rect (pygame.Rect): O retângulo do sprite.
        """
        shadow_offset = (15, 25) # How far the shadow is from the plane
        shadow_pos = (rect.x + shadow_offset[0], rect.y + shadow_offset[1])
        
        # Create a black, semi-transparent version of the sprite
        shadow_image = surface.copy()
        shadow_image.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.screen.blit(shadow_image, shadow_pos)

    def _show_splash_screen(self):
        """Exibe a tela de splash inicial com o logo do jogo e aguarda uma tecla ser pressionada."""
        self.sounds['splash'].play()
        splash_image = pygame.image.load("assets/images/Splash.jpg").convert()
        splash_image = pygame.transform.scale(splash_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        logo_image = pygame.image.load("assets/images/Logo.png").convert_alpha()

        # Scale logo to fit, e.g., 50% of screen width, maintaining aspect ratio
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

        # Load and display Logo.png
        logo_image = pygame.image.load("assets/images/Logo.png").convert_alpha()
        logo_width = int(SCREEN_WIDTH * 0.6) # Slightly larger than splash screen
        logo_height = int(logo_image.get_height() * (logo_width / logo_image.get_width()))
        logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(logo_image, logo_rect)

        # Display Score and High Score
        score_text = self.font.render(f"YOUR SCORE: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        highscore_text = self.font.render(f"HIGH SCORE: {self.highscore}", True, WHITE)
        highscore_rect = highscore_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(highscore_text, highscore_rect)

        # Display options
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
        """Reinicia o estado do jogo para iniciar uma nova partida."""
        self.score = 0
        self.load_highscore()
        self.current_difficulty_index = INITIAL_DIFFICULTY_STAGE_INDEX
        self.current_difficulty_settings = DIFFICULTY_STAGES[self.current_difficulty_index]

        # Clear all sprite groups and re-initialize
        self.all_sprites.empty()
        self.enemies.empty()
        self.clouds.empty()
        self.enemy_bullets.empty()

        self.player = Player(self.all_sprites)
        self.all_sprites.add(self.player)

        # Reset timers
        min_delay, max_delay = self.current_difficulty_settings["enemy_spawn_delay"]
        pygame.time.set_timer(self.ADD_ENEMY, random.randint(min_delay, max_delay))
        pygame.time.set_timer(self.ADD_CLOUD, 1500)

        self.running = True # Set running to True to restart the main game loop
        self.start_game_sounds()

    def draw(self):
        """Desenha todos os elementos do jogo na tela, incluindo fundo, sprites e HUD."""
        # 1. Draw scrolling background
        self.screen.blit(self.background, (0, self.bg_y1))
        self.screen.blit(self.background, (0, self.bg_y2))
        
        # 2. Draw shadows
        self.draw_shadow(self.player.image, self.player.rect)
        for enemy in self.enemies:
            self.draw_shadow(enemy.image, enemy.rect)

        # 3. Draw clouds
        self.clouds.draw(self.screen)
        
        # 4. Draw actual sprites (planes, bullets, effects)
        non_cloud_sprites = pygame.sprite.Group([s for s in self.all_sprites if not isinstance(s, Cloud)])
        non_cloud_sprites.draw(self.screen)
        self.enemy_bullets.draw(self.screen) # Draw enemy bullets

        # 5. Draw HUD
        self.draw_hud()
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()