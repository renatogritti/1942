"""
Projeto: Clone 1942
Descrição: Módulo responsável por gerenciar os efeitos visuais do jogo, como explosões (partículas e GIF),
           efeitos de bomba e nuvens de fundo. Estes efeitos contribuem para a imersão visual do jogo.
Autoria: Renato Gritti
"""

import pygame
import random
import math
from src.config import *
from PIL import Image, ImageSequence # Importar Pillow
from typing import List, Dict, Any, Tuple


class BombEffect(pygame.sprite.Sprite):
    """
    Representa o efeito visual de uma bomba explodindo na tela com um sistema de partículas.

    Cria e gerencia múltiplas partículas que se espalham e desvanecem, simulando uma explosão.
    """
    def __init__(self, center: Tuple[int, int]) -> None:
        """
        Inicializa o efeito da bomba com partículas.

        Args:
            center (Tuple[int, int]): A posição central (x, y) onde a bomba explode.
        """
        super().__init__()
        self.center: Tuple[int, int] = center
        self.frame: int = 0
        self.max_frames: int = 45  # Duração do efeito da bomba
        self.particles: List[Dict[str, Any]] = []
        self.num_particles: int = 80  # Número de partículas para o efeito da bomba
        self.colors: List[Tuple[int, int, int]] = [
            (255, 255, 200), (255, 200, 0), (255, 100, 0), (200, 50, 0)
        ]  # Cores para a explosão da bomba

        # Gerar partículas iniciais
        for _ in range(self.num_particles):
            angle: float = random.uniform(0, 2 * math.pi)
            speed: float = random.uniform(5, 15)  # Velocidade inicial das partículas
            size: int = random.randint(5, 12)  # Tamanho das partículas
            lifetime: int = random.randint(20, 40)  # Tempo de vida das partículas
            color: Tuple[int, int, int] = random.choice(self.colors)
            self.particles.append({
                'pos': list(center),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': size,
                'lifetime': lifetime,
                'color': color,
                'alpha': 255
            })

        self.image: pygame.Surface = pygame.Surface((1, 1), pygame.SRCALPHA)  # Superfície dummy, será redesenhada a cada frame
        self.rect: pygame.Rect = self.image.get_rect(center=center)

    def update(self) -> None:
        """
        Atualiza o estado do efeito da bomba, movendo e desvanecendo as partículas.

        O efeito é removido quando todas as partículas desaparecem ou o tempo máximo de frames é atingido.
        """
        self.frame += 1
        if self.frame > self.max_frames and not self.particles:
            self.kill()
            return

        # Atualizar partículas
        for p in self.particles[:]:  # Iterar sobre uma cópia para permitir remoção
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['lifetime'] -= 1
            p['alpha'] = max(0, min(255, int(255 * (p['lifetime'] / self.max_frames))))  # Ajustar alpha com base no tempo de vida
            if p['lifetime'] <= 0:
                self.particles.remove(p)

        # Redimensionar superfície da imagem para abranger todas as partículas para desenho
        if self.particles:
            min_x: float = min(p['pos'][0] for p in self.particles)
            max_x: float = max(p['pos'][0] + p['size'] for p in self.particles)
            min_y: float = min(p['pos'][1] for p in self.particles)
            max_y: float = max(p['pos'][1] + p['size'] for p in self.particles)

            new_width: int = max(1, int(max_x - min_x))
            new_height: int = max(1, int(max_y - min_y))
            self.image = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            self.rect = self.image.get_rect(topleft=(min_x, min_y))

            # Desenhar partículas na nova superfície
            for p in self.particles:
                draw_color: Tuple[int, int, int, int] = (p['color'][0], p['color'][1], p['color'][2], p['alpha'])
                pygame.draw.circle(self.image, draw_color, (int(p['pos'][0] - min_x), int(p['pos'][1] - min_y)), p['size'] // 2)
        else:
            self.image = pygame.Surface((1, 1), pygame.SRCALPHA)  # Superfície vazia se não houver mais partículas


class Explosion(pygame.sprite.Sprite):
    """
    Representa o efeito visual de uma explosão com partículas.

    Cria e gerencia partículas que se espalham e desvanecem, simulando uma explosão de impacto.
    """
    def __init__(self, center: Tuple[int, int]) -> None:
        """
        Inicializa a explosão com partículas.

        Args:
            center (Tuple[int, int]): A posição central (x, y) da explosão.
        """
        super().__init__()
        self.center: Tuple[int, int] = center
        self.frame: int = 0
        self.max_frames: int = 30  # Duração da explosão
        self.particles: List[Dict[str, Any]] = []
        self.num_particles: int = 30  # Número de partículas
        self.colors: List[Tuple[int, int, int]] = [
            (255, 255, 0), (255, 165, 0), (255, 69, 0), (139, 0, 0)
        ]  # Amarelo, Laranja, LaranjaAvermelhado, VermelhoEscuro

        # Gerar partículas iniciais
        for _ in range(self.num_particles):
            angle: float = random.uniform(0, 2 * math.pi)
            speed: float = random.uniform(3, 9)  # Velocidade da partícula
            size: int = random.randint(4, 8)  # Tamanho da partícula
            lifetime: int = random.randint(10, 25)  # Tempo de vida da partícula
            color: Tuple[int, int, int] = random.choice(self.colors)
            self.particles.append({
                'pos': list(center),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': size,
                'lifetime': lifetime,
                'color': color,
                'alpha': 255
            })

        self.image: pygame.Surface = pygame.Surface((1, 1), pygame.SRCALPHA)  # Superfície dummy, será redesenhada a cada frame
        self.rect: pygame.Rect = self.image.get_rect(center=center)

    def update(self) -> None:
        """
        Atualiza o estado da explosão, movendo e desvanecendo as partículas.

        O efeito é removido quando todas as partículas desaparecem ou o tempo máximo de frames é atingido.
        """
        self.frame += 1
        if self.frame > self.max_frames and not self.particles:
            self.kill()
            return

        # Atualizar partículas
        for p in self.particles[:]:  # Iterar sobre uma cópia para permitir remoção
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['lifetime'] -= 1
            p['alpha'] = max(0, min(255, int(255 * (p['lifetime'] / 15))))  # Limita o alpha entre 0 e 255
            if p['lifetime'] <= 0:
                self.particles.remove(p)

        # Redimensionar superfície da imagem para abranger todas as partículas para desenho
        if self.particles:
            min_x: float = min(p['pos'][0] for p in self.particles)
            max_x: float = max(p['pos'][0] + p['size'] for p in self.particles)
            min_y: float = min(p['pos'][1] for p in self.particles)
            max_y: float = max(p['pos'][1] + p['size'] for p in self.particles)

            new_width: int = max(1, int(max_x - min_x))
            new_height: int = max(1, int(max_y - min_y))
            self.image = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
            self.rect = self.image.get_rect(topleft=(min_x, min_y))

            # Desenhar partículas na nova superfície
            for p in self.particles:
                draw_color: Tuple[int, int, int, int] = (p['color'][0], p['color'][1], p['color'][2], p['alpha'])
                pygame.draw.circle(self.image, draw_color, (int(p['pos'][0] - min_x), int(p['pos'][1] - min_y)), p['size'] // 2)
        else:
            self.image = pygame.Surface((1, 1), pygame.SRCALPHA)  # Superfície vazia se não houver mais partículas


class GifExplosion(pygame.sprite.Sprite):
    """
    Representa uma explosão animada a partir de um GIF usando a biblioteca Pillow.

    Carrega e exibe os frames de um GIF sequencialmente para criar uma animação de explosão.
    """
    def __init__(self, center: Tuple[int, int], size: int = 64) -> None:
        """
        Inicializa uma nova explosão baseada em GIF.

        Args:
            center (Tuple[int, int]): A posição central (x, y) da explosão.
            size (int): O tamanho (largura e altura) para redimensionar cada frame do GIF.
        """
        super().__init__()
        self.frames: List[pygame.Surface] = []
        self.frame_durations: List[int] = []

        try:
            pil_image: Image.Image = Image.open("assets/images/Explosion.gif")
        except Exception as e:
            print(f"Erro ao carregar o GIF de explosão 'assets/images/Explosion.gif': {e}")
            self.kill()  # Remove o sprite se o GIF não puder ser carregado
            return

        for frame in ImageSequence.Iterator(pil_image):
            # Converte o frame PIL para superfície Pygame
            frame_image: Image.Image = frame.convert('RGBA')
            pygame_image: pygame.Surface = pygame.image.fromstring(
                frame_image.tobytes(), frame_image.size, frame_image.mode
            ).convert_alpha()

            # Redimensiona o frame para o tamanho quadrado desejado
            scaled_image: pygame.Surface = pygame.transform.scale(pygame_image, (size, size))
            self.frames.append(scaled_image)
            
            # Armazena a duração do frame, se disponível, caso contrário, usa um padrão
            self.frame_durations.append(frame.info.get('duration', 50))

        if not self.frames:
            print("Nenhum frame encontrado em Explosion.gif")
            self.kill()
            return

        self.current_frame: int = 0
        self.image: pygame.Surface = self.frames[self.current_frame]
        self.rect: pygame.Rect = self.image.get_rect(center=center)
        
        self.last_anim_time: int = pygame.time.get_ticks()
        self.anim_delay: int = self.frame_durations[0] if self.frame_durations else 50

    def update(self) -> None:
        """
        Atualiza a animação da explosão GIF.

        Avança para o próximo frame da animação com base no tempo.
        A explosão é removida quando a animação termina.
        """
        now: int = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_delay:
            self.last_anim_time = now
            self.current_frame += 1  # Incrementa o frame diretamente
            
            if self.current_frame < len(self.frames):
                self.image = self.frames[self.current_frame]
                self.anim_delay = self.frame_durations[self.current_frame]
            else:
                self.kill()  # Remove a explosão quando a animação termina


class Cloud(pygame.sprite.Sprite):
    """
    Representa uma nuvem de fundo que se move pela tela.

    As nuvens são geradas com tamanhos e formas aleatórias e se movem para baixo,
    saindo da tela e sendo removidas.
    """
    def __init__(self) -> None:
        """
        Inicializa uma nuvem com tamanho, forma e posição aleatórios.

        Cria uma superfície semi-transparente e desenha elipses para formar a nuvem.
        """
        super().__init__()
        # Cria uma superfície de nuvem branca semi-transparente
        cloud_width: int = random.randint(100, 200)
        cloud_height: int = random.randint(50, 100)
        self.image: pygame.Surface = pygame.Surface((cloud_width, cloud_height), pygame.SRCALPHA)
        
        # Desenha elipses mais variadas e orgânicas
        num_ellipses: int = random.randint(5, 10)
        for _ in range(num_ellipses):
            ellipse_width: int = random.randint(cloud_width // 4, cloud_width // 2)
            ellipse_height: int = random.randint(cloud_height // 4, cloud_height // 2)
            ellipse_x: int = random.randint(0, cloud_width - ellipse_width)
            ellipse_y: int = random.randint(0, cloud_height - ellipse_height)
            ellipse_rect: pygame.Rect = pygame.Rect(ellipse_x, ellipse_y, ellipse_width, ellipse_height)
            pygame.draw.ellipse(self.image, (255, 255, 255, random.randint(80, 150)), ellipse_rect)

        self.rect: pygame.Rect = self.image.get_rect(
            center=(random.randint(0, SCREEN_WIDTH), random.randint(-100, -50))  # Começa fora da tela, no topo
        )
        self.speed: int = random.randint(1, 2)

    def update(self) -> None:
        """
        Atualiza a posição da nuvem.

        Move a nuvem para baixo e a remove do grupo de sprites se ela sair da tela.
        """
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
