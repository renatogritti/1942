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

        # Atributos específicos do inimigo baseados nas configurações de dificuldade
        self.type: str = random.choice(self.difficulty_settings["enemy_types_available"])
        
        # Seleciona os frames de animação e durações corretos para o tipo de inimigo
        self.frames: List[pygame.Surface] = Enemy.animation_frames[self.type]
        self.durations: List[int] = Enemy.frame_durations[self.type]

        self.current_frame: int = random.randint(0, len(self.frames) - 1)
        # A imagem base (self.frames) aponta para baixo. A rotação será aplicada no update.
        self.base_image: pygame.Surface = self.frames[self.current_frame]
        self.image: pygame.Surface = self.base_image
        
        self.speed_y: int = random.randint(self.difficulty_settings["enemy_speed_y"][0], self.difficulty_settings["enemy_speed_y"][1])
        self.speed_x: int = random.randint(self.difficulty_settings["enemy_speed_x"][0], self.difficulty_settings["enemy_speed_x"][1]) if self.type in ['weaving', 'diving'] else 0
        self.direction_x: int = random.choice([-1, 1])

        if self.type == 'diving':
            self.movement_state = 'entering'
            self.entry_side = random.choice(['left', 'right'])
            entry_y = random.randint(150, SCREEN_HEIGHT // 2)
            entry_x = -50 if self.entry_side == 'left' else SCREEN_WIDTH + 50
            self.rect = self.image.get_rect(center=(entry_x, entry_y))

            self.circle_center_x = random.randint(200, SCREEN_WIDTH - 200)
            self.circle_center_y = entry_y + 50
            self.circle_radius = random.randint(80, 120)
            self.circle_direction = 1 if self.entry_side == 'left' else -1
            self.circle_speed = random.uniform(0.02, 0.04) * self.circle_direction
            
            if self.entry_side == 'left':
                self.circle_angle = math.pi
            else:
                self.circle_angle = 0
            
            self.total_angle_traveled = 0.0

        else:
            self.rect: pygame.Rect = self.image.get_rect(
                center=(random.randint(40, SCREEN_WIDTH - 40), random.randint(-100, -40))
            )

        self.last_anim_time: int = 0
        self.anim_delay: int = self.durations[self.current_frame]

        self.last_shot_time: int = pygame.time.get_ticks()
        self.shoot_delay: int = random.randint(self.difficulty_settings["enemy_shoot_delay"][0], self.difficulty_settings["enemy_shoot_delay"][1])

    @classmethod
    def _load_enemy_assets(cls) -> None:
        """
        Método de classe para carregar os frames de animação de todos os GIFs de inimigos.

        Carrega as imagens GIF de diferentes tipos de inimigos, as processa em superfícies Pygame,
        redimensiona e inverte verticalmente para a orientação correta no jogo.
        """
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
                pygame_image: pygame.Surface = pygame.image.fromstring(
                    frame_image.tobytes(), frame_image.size, frame_image.mode
                ).convert_alpha()

                original_width: int = pygame_image.get_width()
                original_height: int = pygame_image.get_height()
                target_width: int = 50
                aspect_ratio: float = original_height / original_width if original_width > 0 else 1.0
                target_height: int = int(target_width * aspect_ratio)
                scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (target_width, target_height))
                
                # Inverte a imagem para que a frente do avião aponte para baixo
                flipped_image: pygame.Surface = pygame.transform.flip(scaled_image, False, True)
                
                cls.animation_frames[enemy_type].append(flipped_image)
        cls._is_loaded = True

    def _move(self, player_pos: Tuple[int, int]) -> None:
        """
        Gerencia o movimento do inimigo com base no seu tipo (reto, zigue-zague ou mergulho).

        Args:
            player_pos (Tuple[int, int]): A posição (x, y) atual do jogador, usada para o movimento de mergulho.
        """
        if self.type == 'straight':
            self.rect.y += self.speed_y
        elif self.type == 'weaving':
            self.rect.y += self.speed_y
            self.rect.x += self.speed_x * self.direction_x
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.direction_x *= -1
        elif self.type == 'diving':
            if self.movement_state == 'entering':
                target_x = self.circle_center_x - self.circle_radius * math.cos(self.circle_angle)
                if (self.entry_side == 'left' and self.rect.centerx < target_x) or \
                   (self.entry_side == 'right' and self.rect.centerx > target_x):
                    self.rect.x += self.speed_x if self.entry_side == 'left' else -self.speed_x
                else:
                    self.movement_state = 'circling'

            elif self.movement_state == 'circling':
                self.circle_angle += self.circle_speed
                self.total_angle_traveled += abs(self.circle_speed)

                if self.total_angle_traveled >= 2 * math.pi:
                    self.movement_state = 'exiting'
                
                new_x = self.circle_center_x - self.circle_radius * math.cos(self.circle_angle)
                new_y = self.circle_center_y - self.circle_radius * math.sin(self.circle_angle)
                self.rect.center = (new_x, new_y)

            elif self.movement_state == 'exiting':
                self.rect.y += self.speed_y

    def _shoot(self, player_pos: Tuple[int, int]) -> None:
        """
        Gerencia o disparo de projéteis pelo inimigo.

        Inimigos atiram em intervalos definidos pelas configurações de dificuldade.

        Args:
            player_pos (Tuple[int, int]): A posição (x, y) atual do jogador, usada para o disparo.
        """
        now: int = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, player_pos, self.difficulty_settings["enemy_bullet_speed"])
            self.game_instance.all_sprites.add(bullet)
            self.game_instance.enemy_bullets.add(bullet)

    def update(self, player_pos: Tuple[int, int]) -> None:
        """
        Atualiza o estado do inimigo, incluindo animação, movimento e disparo.

        Args:
            player_pos (Tuple[int, int]): A posição (x, y) atual do jogador, usada para o movimento e disparo.
        """
        old_center = self.rect.center

        # --- Movimento ---
        self._move(player_pos)
        
        new_center = self.rect.center

        # --- Animação ---
        now = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.anim_delay = self.durations[self.current_frame]
        
        self.base_image = self.frames[self.current_frame]

        # --- Rotação ---
        dx = new_center[0] - old_center[0]
        dy = new_center[1] - old_center[1]
        
        if self.type in ['weaving', 'diving'] and (dx != 0 or dy != 0):
            # A imagem base aponta para baixo (eixo Y positivo).
            # math.atan2(dx, dy) calcula o ângulo do vetor de movimento (dx, dy) em relação ao eixo Y.
            # Uma rotação positiva em Pygame é anti-horária.
            # Se dx > 0 (movendo para a direita), o ângulo é positivo, resultando em uma rotação anti-horária (correto).
            # Se dx < 0 (movendo para a esquerda), o ângulo é negativo, resultando em uma rotação horária (correto).
            # Isso corrige a inclinação invertida e o voo de ré.
            angle = math.degrees(math.atan2(dx, dy))
            self.image = pygame.transform.rotate(self.base_image, angle)
        else:
            self.image = self.base_image
        
        self.rect = self.image.get_rect(center=new_center)

        # --- Condição de Saída ---
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        # --- Disparo ---
        can_shoot = True
        if self.type == 'diving':
            # Só permite atirar quando o avião está virado predominantemente para baixo.
            # O vetor de movimento dy deve ser positivo (movendo para baixo).
            # O ângulo de voo (em relação ao eixo X) deve estar entre 45 e 135 graus.
            if dy > 0.1:  # Usamos 0.1 para evitar problemas com dy sendo exatamente 0
                flight_angle_deg = math.degrees(math.atan2(dy, dx))
                if not (45 < flight_angle_deg < 135):
                    can_shoot = False
            else:
                can_shoot = False
        
        if can_shoot:
            self._shoot(player_pos)
