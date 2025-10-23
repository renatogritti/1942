# src/enemy.py
import pygame
import random
from src.config import *
from PIL import Image, ImageSequence
from src.bullet import EnemyBullet # Import EnemyBullet

class Enemy(pygame.sprite.Sprite):
    """Representa um avião inimigo no jogo."""
    # Class variables to store frames, loaded only once to save memory/cpu
    animation_frames = []
    frame_durations = []
    _is_loaded = False

    def __init__(self, game_instance, difficulty_settings):
        """Inicializa um inimigo com base nas configurações de dificuldade.

        Args:
            game_instance (Game): A instância do jogo principal.
            difficulty_settings (dict): Dicionário com as configurações de dificuldade para este inimigo.
        """
        super().__init__()
        self.game_instance = game_instance # Store game instance
        self.difficulty_settings = difficulty_settings # Store difficulty settings
        # Ensure frames are loaded only once for the entire class
        if not Enemy._is_loaded:
            Enemy._load_animated_gif()

        self.current_frame = random.randint(0, len(Enemy.animation_frames) - 1)
        self.image = Enemy.animation_frames[self.current_frame]
        self.rect = self.image.get_rect(
            center=(random.randint(40, SCREEN_WIDTH - 40), random.randint(-100, -40))
        )
        
        self.last_anim_time = 0
        self.anim_delay = Enemy.frame_durations[self.current_frame]

        # Enemy specific attributes based on difficulty settings
        self.type = random.choice(self.difficulty_settings["enemy_types_available"])
        self.speed_y = random.randint(self.difficulty_settings["enemy_speed_y"][0], self.difficulty_settings["enemy_speed_y"][1])
        self.speed_x = random.randint(self.difficulty_settings["enemy_speed_x"][0], self.difficulty_settings["enemy_speed_x"][1]) if self.type in ['weaving', 'diving'] else 0
        self.direction_x = random.choice([-1, 1]) # For weaving movement

        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_delay = random.randint(self.difficulty_settings["enemy_shoot_delay"][0], self.difficulty_settings["enemy_shoot_delay"][1])

    @classmethod
    def _load_animated_gif(cls):
        """Método de classe para carregar os frames do GIF do inimigo em variáveis de classe."""
        try:
            pil_image = Image.open("assets/images/enemy.gif")
        except Exception as e:
            print(f"Error loading enemy image 'assets/images/enemy.gif': {e}")
            pygame.quit()
            sys.exit()
        for frame in ImageSequence.Iterator(pil_image):
            duration = frame.info.get('duration', 50)
            cls.frame_durations.append(duration)

            frame_image = frame.convert('RGBA')
            pygame_image = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()

            # Scale the image (e.g., to a width of 50px)
            original_width = pygame_image.get_width()
            original_height = pygame_image.get_height()
            target_width = 50
            aspect_ratio = original_height / original_width if original_width > 0 else 1
            target_height = int(target_width * aspect_ratio)
            scaled_image = pygame.transform.scale(pygame_image, (target_width, target_height))
            
            # Flip the image vertically so it points downwards
            flipped_image = pygame.transform.flip(scaled_image, False, True)
            
            cls.animation_frames.append(flipped_image)
        cls._is_loaded = True

    def _move(self, player_pos):
        """Gerencia o movimento do inimigo com base no seu tipo.

        Args:
            player_pos (tuple): A posição (x, y) atual do jogador.
        """
        if self.type == 'straight':
            self.rect.y += self.speed_y
        elif self.type == 'weaving':
            self.rect.y += self.speed_y
            self.rect.x += self.speed_x * self.direction_x
            # Reverse direction if hitting screen edges
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.direction_x *= -1
        elif self.type == 'diving':
            # Move towards player's x, while still moving down
            if self.rect.centerx < player_pos[0]:
                self.rect.x += min(self.speed_x, player_pos[0] - self.rect.centerx)
            elif self.rect.centerx > player_pos[0]:
                self.rect.x -= min(self.speed_x, self.rect.centerx - player_pos[0])
            self.rect.y += self.speed_y

    def _shoot(self, player_pos):
        """Gerencia o disparo de projéteis pelo inimigo.

        Args:
            player_pos (tuple): A posição (x, y) atual do jogador.
        """
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            # Create a bullet at the enemy's current position, aimed at player_pos
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, player_pos, self.difficulty_settings["enemy_bullet_speed"])
            self.game_instance.all_sprites.add(bullet)
            self.game_instance.enemy_bullets.add(bullet)

    def update(self, player_pos): # Accept player_pos
        """Atualiza o estado do inimigo, incluindo animação, movimento e disparo.

        Args:
            player_pos (tuple): A posição (x, y) atual do jogador.
        """
        # --- Animation ---
        now = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.anim_delay = self.frame_durations[self.current_frame]
            
            center = self.rect.center
            self.image = self.animation_frames[self.current_frame]
            self.rect = self.image.get_rect(center=center)

        # --- Movement ---
        self._move(player_pos) # Pass player_pos to move method
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove if it goes off-screen

        # --- Shooting ---
        self._shoot(player_pos) # Pass player_pos to shoot method