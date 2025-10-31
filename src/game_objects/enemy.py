"""
Projeto: Clone 1942
Descrição: Módulo responsável por definir a classe Enemy, que gerencia os diferentes tipos de inimigos no jogo.
           Inclui lógica para carregamento de assets, movimentação variada (reta, zigue-zague, mergulho)
           e disparo de projéteis inimigos, adaptando-se aos estágios de dificuldade.
Autoria: Renato Gritti
"""

import pygame
import random
import sys
import math
from src.config import *
from PIL import Image, ImageSequence
from src.game_objects.bullet import EnemyBullet # Import EnemyBullet
from typing import Dict, Any, List, Tuple


class Enemy(pygame.sprite.Sprite):
    """
    Representa um avião inimigo no jogo, com diferentes padrões de movimento e disparo.

    Os inimigos são animados e suas características (velocidade, frequência de tiro) são
    determinadas pelas configurações de dificuldade do jogo.
    """
    # Variáveis de classe para armazenar frames de animação para diferentes tipos de inimigos
    animation_frames: Dict[str, List[pygame.Surface]] = {}
    frame_durations: Dict[str, List[int]] = {}
    _is_loaded: bool = False

    def __init__(self, game_instance: Any, difficulty_settings: Dict[str, Any]) -> None:
        """
        Inicializa um novo inimigo com base nas configurações de dificuldade atuais do jogo.

        Args:
            game_instance (Any): A instância principal do jogo, usada para acessar grupos de sprites e outros recursos.
            difficulty_settings (Dict[str, Any]): Um dicionário contendo as configurações de dificuldade para este inimigo.
        """
        super().__init__()
        self.game_instance = game_instance
        self.difficulty_settings = difficulty_settings

        if not Enemy._is_loaded:
            Enemy._load_enemy_assets()

        self.type: str = random.choice(self.difficulty_settings["enemy_types_available"])
        self.frames: List[pygame.Surface] = Enemy.animation_frames[self.type]
        self.durations: List[int] = Enemy.frame_durations[self.type]

        self.current_frame: int = random.randint(0, len(self.frames) - 1)
        self.base_image: pygame.Surface = self.frames[self.current_frame]
        self.image: pygame.Surface = self.base_image
        
        self.speed_y: int = random.randint(self.difficulty_settings["enemy_speed_y"][0], self.difficulty_settings["enemy_speed_y"][1])
        
        # Configuração inicial de posição e movimento
        if self.type == 'diving':
            self.movement_state = 'entering'
            self.entry_side = random.choice(['left', 'right'])
            entry_y = random.randint(150, SCREEN_HEIGHT // 2)
            entry_x = -50 if self.entry_side == 'left' else SCREEN_WIDTH + 50
            
            self.circle_center_x = random.randint(200, SCREEN_WIDTH - 200)
            self.circle_center_y = entry_y + 150
            self.circle_radius = random.randint(80, 120)
            # Direção: horária se vem da esquerda, anti-horária se vem da direita
            self.circle_direction = -1 if self.entry_side == 'left' else 1
            self.circle_speed = random.uniform(0.02, 0.04) * self.circle_direction

            # Define o ângulo inicial para o círculo (pi para esquerda, 0 para direita)
            self.circle_angle = math.pi if self.entry_side == 'left' else 0

            # Configuração da curva de Bézier para a entrada
            self.entry_t = 0.0
            self.entry_speed = 0.015
            self.entry_start_pos = pygame.math.Vector2(entry_x, entry_y)
            # O ponto final é o início do círculo (no lado correto)
            self.entry_target_pos = pygame.math.Vector2(
                self.circle_center_x + self.circle_radius * math.cos(self.circle_angle),
                self.circle_center_y + self.circle_radius * math.sin(self.circle_angle)
            )
            # O ponto de controle garante que a curva comece horizontal e termine tangencialmente
            self.entry_control_pos = pygame.math.Vector2(self.entry_target_pos.x, self.entry_start_pos.y)
            self.rect = self.image.get_rect(center=self.entry_start_pos)
            self.total_angle_traveled = 0.0

        elif self.type == 'weaving':
            # Movimento senoidal para curvas suaves
            self.rect = self.image.get_rect(center=(random.randint(40, SCREEN_WIDTH - 40), random.randint(-150, -80)))
            self.wave_amplitude = random.randint(100, (SCREEN_WIDTH - 100) // 2)
            self.wave_frequency = random.uniform(0.005, 0.01)
            max_x = SCREEN_WIDTH - self.wave_amplitude - 40
            min_x = self.wave_amplitude + 40
            self.wave_center_x = random.randint(min_x, max_x)
        else: # straight
            self.rect = self.image.get_rect(center=(random.randint(40, SCREEN_WIDTH - 40), random.randint(-100, -40)))

        self.last_anim_time: int = 0
        self.anim_delay: int = self.durations[self.current_frame]

        self.last_shot_time: int = pygame.time.get_ticks()
        self.shoot_delay: int = random.randint(self.difficulty_settings["enemy_shoot_delay"][0], self.difficulty_settings["enemy_shoot_delay"][1])

    @classmethod
    def _load_enemy_assets(cls, *args, **kwargs) -> None:
        if cls._is_loaded:
            return
        enemy_gifs: Dict[str, str] = {
            'straight': "assets/images/Enemy.gif",
            'weaving': "assets/images/Enemy2.gif",
            'diving': "assets/images/Enemy3.gif"
        }
        for enemy_type, path in enemy_gifs.items():
            cls.animation_frames[enemy_type] = []
            cls.frame_durations[enemy_type] = []
            try:
                pil_image: Image.Image = Image.open(path)
            except Exception as e:
                print(f"Erro ao carregar a imagem do inimigo '{path}': {e}")
                pygame.quit()
                sys.exit()
            for frame in ImageSequence.Iterator(pil_image):
                duration: int = frame.info.get('duration', 50)
                cls.frame_durations[enemy_type].append(duration)
                frame_image: Image.Image = frame.convert('RGBA')
                pygame_image: pygame.Surface = pygame.image.fromstring(frame_image.tobytes(), frame_image.size, frame_image.mode).convert_alpha()
                target_width: int = 50
                aspect_ratio: float = pygame_image.get_height() / pygame_image.get_width() if pygame_image.get_width() > 0 else 1.0
                target_height: int = int(target_width * aspect_ratio)
                scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (target_width, target_height))
                flipped_image: pygame.Surface = pygame.transform.flip(scaled_image, False, True)
                cls.animation_frames[enemy_type].append(flipped_image)
        cls._is_loaded = True

    def _move(self, player_pos: Tuple[int, int]) -> None:
        if self.type == 'straight':
            self.rect.y += self.speed_y
        elif self.type == 'weaving':
            self.rect.y += self.speed_y
            offset_x = self.wave_amplitude * math.sin(self.rect.y * self.wave_frequency)
            self.rect.centerx = self.wave_center_x + offset_x
        elif self.type == 'diving':
            if self.movement_state == 'entering':
                if self.entry_t < 1.0:
                    self.entry_t += self.entry_speed
                    t = min(self.entry_t, 1.0)
                    pos = self.entry_start_pos.lerp(self.entry_control_pos, t).lerp(self.entry_control_pos.lerp(self.entry_target_pos, t), t)
                    self.rect.center = pos
                else:
                    self.movement_state = 'circling'
                    self.rect.center = self.entry_target_pos
            elif self.movement_state == 'circling':
                self.circle_angle += self.circle_speed
                self.total_angle_traveled += abs(self.circle_speed)
                if self.total_angle_traveled >= 2 * math.pi:
                    self.movement_state = 'exiting'
                new_x = self.circle_center_x + self.circle_radius * math.cos(self.circle_angle)
                new_y = self.circle_center_y + self.circle_radius * math.sin(self.circle_angle)
                self.rect.center = (new_x, new_y)
            elif self.movement_state == 'exiting':
                self.rect.y += self.speed_y

    def _shoot(self, player_pos: Tuple[int, int]) -> None:
        now: int = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, player_pos, self.difficulty_settings["enemy_bullet_speed"])
            self.game_instance.all_sprites.add(bullet)
            self.game_instance.enemy_bullets.add(bullet)

    def update(self, player_pos: Tuple[int, int]) -> None:
        old_center = self.rect.center
        self._move(player_pos)
        new_center = self.rect.center

        now = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.anim_delay = self.durations[self.current_frame]
        self.base_image = self.frames[self.current_frame]

        dx = new_center[0] - old_center[0]
        dy = new_center[1] - old_center[1]
        
        if self.type in ['weaving', 'diving'] and (dx != 0 or dy != 0):
            angle = math.degrees(math.atan2(dx, dy))
            self.image = pygame.transform.rotate(self.base_image, angle)
        else:
            self.image = self.base_image
        
        self.rect = self.image.get_rect(center=new_center)

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        can_shoot = True
        if self.type == 'diving':
            if dy > 0.1:
                flight_angle_deg = math.degrees(math.atan2(dy, dx))
                if not (45 < flight_angle_deg < 135):
                    can_shoot = False
            else:
                can_shoot = False
        
        if can_shoot:
            self._shoot(player_pos)
