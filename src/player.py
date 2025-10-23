# src/player.py
import pygame
from src.config import *
from src.bullet import Bullet
from PIL import Image, ImageSequence

class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites):
        super().__init__()
        self.all_sprites = all_sprites
        self.bullets = pygame.sprite.Group()
        self.load_animated_gif()

        self.current_frame = 0
        self.image = self.animation_frames[self.current_frame]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
        
        self.lives = 3
        self.bombs = 1
        self.last_anim_time = 0
        # Use the GIF's own duration for the delay, or a default
        self.anim_delay = self.frame_durations[0] if self.frame_durations else 50

    def load_animated_gif(self):
        """ Loads all frames from a GIF and converts them to Pygame surfaces. """
        self.animation_frames = []
        self.frame_durations = []
        
        try:
            pil_image = Image.open("assets/images/plane.gif")
        except Exception as e:
            print(f"Error loading player plane image 'assets/images/plane.gif': {e}")
            pygame.quit()
            sys.exit()
        for frame in ImageSequence.Iterator(pil_image):
            # Get frame duration
            duration = frame.info.get('duration', 50)
            self.frame_durations.append(duration)

            # Convert PIL frame to Pygame surface
            frame_image = frame.convert('RGBA')
            pygame_image = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()

            # Scale the image
            original_width = pygame_image.get_width()
            original_height = pygame_image.get_height()
            target_width = 64
            aspect_ratio = original_height / original_width if original_width > 0 else 1
            target_height = int(target_width * aspect_ratio)
            scaled_image = pygame.transform.scale(pygame_image, (target_width, target_height))
            
            self.animation_frames.append(scaled_image)

    def update(self):
        # --- Animation Loop ---
        now = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.anim_delay = self.frame_durations[self.current_frame]
            
            # Update image and preserve center
            center = self.rect.center
            self.image = self.animation_frames[self.current_frame]
            self.rect = self.image.get_rect(center=center)

        # --- Movement Handling ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def reset(self):
        """ Resets the player's position to the initial spot. """
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60)

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        self.all_sprites.add(bullet)
        self.bullets.add(bullet)
