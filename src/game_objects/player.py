"""
Projeto: Clone 1942
Descrição: Módulo responsável por definir a classe Player, que representa o avião controlável pelo jogador.
           Gerencia a movimentação do jogador, disparo de projéteis, coleta de itens (moedas),
           e sua interação com o ambiente e inimigos.
Autoria: Renato Gritti
"""

import pygame
import sys
from src.config import *
from src.game_objects.bullet import Bullet # Atualizado o import
from PIL import Image, ImageSequence
from typing import List, Tuple, Any


class MiniPlane(pygame.sprite.Sprite):
    """
    Representa um dos aviões menores que acompanham o jogador no modo de tiro triplo.
    """
    def __init__(self, player_instance: 'Player', offset_x: int, mini_plane_frames: List[pygame.Surface], frame_durations: List[int]) -> None:
        super().__init__()
        self.player = player_instance # Referência à instância do Player
        self.mini_plane_frames = mini_plane_frames
        self.frame_durations = frame_durations
        self.current_frame = 0
        self.image = self.mini_plane_frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.offset_x = offset_x # Deslocamento em X em relação ao centro do player

        self.last_anim_time: int = 0
        self.anim_delay: int = self.frame_durations[0] if self.frame_durations else 50

        self.update_position() # Define a posição inicial

    def update_position(self) -> None:
        # Posiciona o mini-avião em relação ao player
        self.rect.centerx = self.player.rect.centerx + self.offset_x
        self.rect.centery = self.player.rect.centery + 20 # Ligeiramente atrás e abaixo do player

    def update(self) -> None:
        # Lógica de animação (similar à do player principal)
        now: int = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.mini_plane_frames)
            self.anim_delay = self.frame_durations[self.current_frame]
            self.image = self.mini_plane_frames[self.current_frame]

        self.update_position()


class Player(pygame.sprite.Sprite):
    """
    Representa o avião do jogador no jogo.

    Gerencia a posição, energia, bombas, animação e ações do jogador, como mover e atirar.
    """
    def __init__(self, all_sprites: pygame.sprite.Group) -> None:
        """
        Inicializa o jogador com suas propriedades, como posição, energia e bombas.

        Args:
            all_sprites (pygame.sprite.Group): O grupo de todos os sprites do jogo,
                                               usado para adicionar projéteis do jogador.
        """
        super().__init__()
        self.all_sprites: pygame.sprite.Group = all_sprites
        self.bullets: pygame.sprite.Group = pygame.sprite.Group()
        
        self.animation_frames: List[pygame.Surface] = []
        self.frame_durations: List[int] = []
        self.mini_plane_frames: List[pygame.Surface] = [] # Nova lista para frames dos mini-aviões
        self.mini_plane_frame_durations: List[int] = [] # Nova lista para durações dos frames dos mini-aviões
        self.load_animated_gif()

        self.current_frame: int = 0
        self.image: pygame.Surface = self.animation_frames[self.current_frame]
        self.rect: pygame.Rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60))
        
        self.max_energy: int = 100
        self.energy: int = self.max_energy
        self.bombs: int = 1
        self.last_anim_time: int = 0
        self.anim_delay: int = self.frame_durations[0] if self.frame_durations else 50

        self.weapon_type: str = "single" # Novo atributo para o tipo de tiro
        self.left_mini_plane: MiniPlane = None # Atributo para o mini-avião esquerdo
        self.right_mini_plane: MiniPlane = None # Atributo para o mini-avião direito

    def load_animated_gif(self) -> None:
        """
        Carrega todos os frames de um GIF animado do avião do jogador e os converte para superfícies Pygame.
        Também carrega e redimensiona os frames para os mini-aviões.
        """
        self.animation_frames = []
        self.frame_durations = []
        self.mini_plane_frames = []
        self.mini_plane_frame_durations = []
        
        try:
            pil_image: Image.Image = Image.open("assets/images/plane.gif")
        except Exception as e:
            print(f"Erro ao carregar a imagem do avião do jogador 'assets/images/plane.gif': {e}")
            pygame.quit()
            sys.exit()

        for frame in ImageSequence.Iterator(pil_image):
            duration: int = frame.info.get('duration', 50)
            
            # Frames do avião principal
            self.frame_durations.append(duration)
            frame_image: Image.Image = frame.convert('RGBA')
            pygame_image: pygame.Surface = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()
            original_width: int = pygame_image.get_width()
            original_height: int = pygame_image.get_height()
            target_width: int = 64
            aspect_ratio: float = original_height / original_width if original_width > 0 else 1.0
            target_height: int = int(target_width * aspect_ratio)
            scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (target_width, target_height))
            self.animation_frames.append(scaled_image)

            # Frames dos mini-aviões (redimensionados)
            self.mini_plane_frame_durations.append(duration) # Usar as mesmas durações
            mini_target_width: int = 32 # Metade do tamanho do avião principal
            mini_target_height: int = int(mini_target_width * aspect_ratio)
            mini_scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (mini_target_width, mini_target_height))
            self.mini_plane_frames.append(mini_scaled_image)

    def update(self) -> None:
        """
        Atualiza o estado do jogador, incluindo animação, movimento e restrição de tela.
        Também gerencia a visibilidade e posição dos mini-aviões.
        """
        # --- Loop de Animação ---
        now: int = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.anim_delay = self.frame_durations[self.current_frame]
            
            # Atualiza a imagem e preserva o centro
            center: Tuple[int, int] = self.rect.center
            self.image = self.animation_frames[self.current_frame]
            self.rect = self.image.get_rect(center=center)

        # --- Manuseio de Movimento ---
        keys: Any = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

        # Mantém o jogador na tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # Gerencia a visibilidade e posição dos mini-aviões
        if self.weapon_type == "triple":
            if self.left_mini_plane is None:
                self.left_mini_plane = MiniPlane(self, -40, self.mini_plane_frames, self.mini_plane_frame_durations)
                self.right_mini_plane = MiniPlane(self, 40, self.mini_plane_frames, self.mini_plane_frame_durations)
                self.all_sprites.add(self.left_mini_plane, self.right_mini_plane)
            # Os mini-aviões atualizam sua própria posição e animação através do all_sprites.update()
        else:
            if self.left_mini_plane is not None:
                self.left_mini_plane.kill() # Remove do grupo all_sprites
                self.right_mini_plane.kill()
                self.left_mini_plane = None
                self.right_mini_plane = None

    def reset(self) -> None:
        """
        Reinicia a posição do jogador para o local inicial e o tipo de arma.
        Remove os mini-aviões se existirem.
        """
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60)
        self.weapon_type = "single" # Resetar tipo de arma
        if self.left_mini_plane is not None:
            self.left_mini_plane.kill()
            self.right_mini_plane.kill()
            self.left_mini_plane = None
            self.right_mini_plane = None
        self.bombs = 1 # Resetar bombas
        self.energy = self.max_energy # Resetar energia

    def shoot(self) -> None:
        """
        Cria e dispara projéteis do jogador, dependendo do tipo de arma.
        """
        if self.weapon_type == "single":
            bullet: Bullet = Bullet(self.rect.centerx, self.rect.top)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
        elif self.weapon_type == "double":
            bullet1: Bullet = Bullet(self.rect.centerx - 15, self.rect.top)
            bullet2: Bullet = Bullet(self.rect.centerx + 15, self.rect.top)
            self.all_sprites.add(bullet1, bullet2)
            self.bullets.add(bullet1, bullet2)
        elif self.weapon_type == "triple":
            # Tiro do avião principal
            bullet_main: Bullet = Bullet(self.rect.centerx, self.rect.top)
            self.all_sprites.add(bullet_main)
            self.bullets.add(bullet_main)
            # Tiros dos mini-aviões
            if self.left_mini_plane:
                bullet_left: Bullet = Bullet(self.left_mini_plane.rect.centerx, self.left_mini_plane.rect.top)
                self.all_sprites.add(bullet_left)
                self.bullets.add(bullet_left)
            if self.right_mini_plane:
                bullet_right: Bullet = Bullet(self.right_mini_plane.rect.centerx, self.right_mini_plane.rect.top)
                self.all_sprites.add(bullet_right)
                self.bullets.add(bullet_right)

    def change_weapon(self, weapon: str) -> None:
        """
        Muda o tipo de arma do jogador.
        Args:
            weapon (str): O novo tipo de arma ("single", "double", "triple").
        """
        self.weapon_type = weapon

    def add_bomb(self, amount: int) -> None:
        """
        Adiciona uma quantidade de bombas ao jogador.
        Args:
            amount (int): A quantidade de bombas a ser adicionada.
        """
        self.bombs += amount
