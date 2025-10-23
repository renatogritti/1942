# src/effects.py
import pygame
import random
import math # Import math module
from src.config import *

class BombEffect(pygame.sprite.Sprite):
    """Representa o efeito visual de uma bomba explodindo na tela."""
    def __init__(self, center):
        """Inicializa o efeito da bomba.

        Args:
            center (tuple): A posição central (x, y) onde a bomba explode.
        """
        super().__init__()
        pygame.draw.circle(self.image, (255, 255, 0, 150), (75, 75), 75)
        self.rect = self.image.get_rect(center=center)
        self.duration = 30 # frames

    def update(self):
        """Atualiza a duração do efeito da bomba e o remove quando termina."""
        self.duration -= 1
        if self.duration <= 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """Representa o efeito visual de uma explosão com partículas."""
    def __init__(self, center):
        """Inicializa a explosão com partículas.

        Args:
            center (tuple): A posição central (x, y) da explosão.
        """
        super().__init__()
        self.center = center
        self.frame = 0
        self.max_frames = 30 # Increased duration of the explosion
        self.particles = []
        self.num_particles = 30 # Increased number of particles
        self.colors = [(255, 255, 0), (255, 165, 0), (255, 69, 0), (139, 0, 0)] # Yellow, Orange, OrangeRed, DarkRed

        # Generate initial particles
        for _ in range(self.num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 9) # Increased particle speed
            size = random.randint(4, 8) # Increased particle size
            lifetime = random.randint(10, 25) # Increased particle lifetime
            color = random.choice(self.colors)
            self.particles.append({
                'pos': list(center),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': size,
                'lifetime': lifetime,
                'color': color,
                'alpha': 255
            })

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA) # Dummy surface, will be redrawn each frame
        self.rect = self.image.get_rect(center=center)

    def update(self):
        """Atualiza o estado da explosão, movendo e desvanecendo as partículas."""
        self.frame += 1
        if self.frame > self.max_frames and not self.particles:
            self.kill()
            return

        # Update particles
        for p in self.particles[:]: # Iterate over a copy to allow removal
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['lifetime'] -= 1
            p['alpha'] = max(0, min(255, int(255 * (p['lifetime'] / 15)))) # Clamp alpha between 0 and 255
            if p['lifetime'] <= 0:
                self.particles.remove(p)

        # Resize image surface to encompass all particles for drawing
        if self.particles:
            min_x = min(p['pos'][0] for p in self.particles)
            max_x = max(p['pos'][0] + p['size'] for p in self.particles)
            min_y = min(p['pos'][1] for p in self.particles)
            max_y = max(p['pos'][1] + p['size'] for p in self.particles)

            new_width = max(1, int(max_x - min_x))
            new_height = max(1, int(max_y - min_y))
            self.image = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            self.rect = self.image.get_rect(topleft=(min_x, min_y))

            # Draw particles onto the new surface
            for p in self.particles:
                draw_color = (p['color'][0], p['color'][1], p['color'][2], p['alpha'])
                pygame.draw.circle(self.image, draw_color, (int(p['pos'][0] - min_x), int(p['pos'][1] - min_y)), p['size'] // 2)
        else:
            self.image = pygame.Surface((1, 1), pygame.SRCALPHA) # Empty surface if no particles left



class Cloud(pygame.sprite.Sprite):
    """Representa uma nuvem de fundo que se move pela tela."""
    def __init__(self):
        """Inicializa uma nuvem com tamanho, forma e posição aleatórios."""
        super().__init__()
        # Create a semi-transparent white cloud surface
        cloud_width = random.randint(100, 200)
        cloud_height = random.randint(50, 100)
        self.image = pygame.Surface((cloud_width, cloud_height), pygame.SRCALPHA)
        
        # Draw more varied and organic ellipses
        num_ellipses = random.randint(5, 10)
        for _ in range(num_ellipses):
            ellipse_width = random.randint(cloud_width // 4, cloud_width // 2)
            ellipse_height = random.randint(cloud_height // 4, cloud_height // 2)
            ellipse_x = random.randint(0, cloud_width - ellipse_width)
            ellipse_y = random.randint(0, cloud_height - ellipse_height)
            ellipse_rect = pygame.Rect(ellipse_x, ellipse_y, ellipse_width, ellipse_height)
            pygame.draw.ellipse(self.image, (255, 255, 255, random.randint(80, 150)), ellipse_rect)

        self.rect = self.image.get_rect(
            center=(random.randint(0, SCREEN_WIDTH), random.randint(-100, -50)) # Start off-screen top
        )
        self.speed = random.randint(1, 2)

    def update(self):
        """Atualiza a posição da nuvem e a remove se sair da tela."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()