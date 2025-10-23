"""
Projeto: Clone 1942
Descrição: Módulo responsável por gerar e gerenciar as ilhas de fundo no jogo.
           As ilhas são geradas processualmente com texturas de areia, grama e floresta,
           e se movem para baixo na tela, criando um efeito de rolagem de cenário.
Autoria: Renato Gritti
"""

import pygame
import random
import math
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from typing import Tuple, List, Dict, Any


class Island(pygame.sprite.Sprite):
    """
    Representa uma ilha de fundo gerada processualmente que se move pela tela.

    As ilhas são compostas por múltiplas camadas de texturas (areia, grama, floresta)
    e possuem uma forma orgânica gerada por um algoritmo fractal.
    """

    # Variáveis de classe para armazenar as texturas carregadas (para carregar apenas uma vez)
    SAND_TEXTURE: pygame.Surface = None
    GRASS_TEXTURE: pygame.Surface = None
    FOREST_TEXTURE: pygame.Surface = None

    @staticmethod
    def load_textures() -> None:
        """
        Carrega as texturas da ilha se ainda não foram carregadas.

        Este método estático garante que as texturas sejam carregadas apenas uma vez,
        otimizando o uso de memória e o tempo de inicialização.
        """
        if Island.SAND_TEXTURE is None:
            Island.SAND_TEXTURE = pygame.image.load("assets/images/Sand.jpg").convert()
            Island.GRASS_TEXTURE = pygame.image.load("assets/images/Grass.jpg").convert()
            Island.FOREST_TEXTURE = pygame.image.load("assets/images/Forest.jpg").convert()

    def __init__(self, opacity_range: Tuple[int, int] = (150, 200)) -> None:
        """
        Inicializa a ilha, criando sua imagem (superfície) com uma forma e textura aleatórias.

        Args:
            opacity_range (Tuple[int, int]): Uma tupla (min_opacity, max_opacity)
                                             para definir a opacidade aleatória da ilha (0-255).
        """
        super().__init__()

        # Garante que as texturas sejam carregadas antes de criar a ilha
        Island.load_textures()

        # Define um tamanho aleatório para a ilha
        width: int = random.randint(150, 300)
        height: int = random.randint(150, 350)

        # Cria a superfície da imagem com canal alfa para transparência
        self.image: pygame.Surface = pygame.Surface([width, height], pygame.SRCALPHA)

        # --- Algoritmo de Geração Fractal para Formas Orgânicas ---
        def generate_fractal_layer(base_surface: pygame.Surface, texture: pygame.Surface, radius_scaler: float, iterations: int, roughness: float) -> None:
            """
            Gera uma camada fractal para a ilha, aplicando uma textura com uma forma orgânica.

            Utiliza um algoritmo de deslocamento de ponto médio para criar formas irregulares.

            Args:
                base_surface (pygame.Surface): A superfície onde a camada será desenhada.
                texture (pygame.Surface): A textura a ser aplicada à camada.
                radius_scaler (float): Fator para escalar o raio médio da forma base.
                iterations (int): Número de iterações para o algoritmo fractal.
                roughness (float): Controla a irregularidade da forma gerada.
            """
            center_x, center_y = width / 2, height / 2
            avg_radius: float = min(width, height) * radius_scaler
            
            # 1. Cria a forma base (um círculo de pontos)
            num_initial_points: int = 8
            points: List[List[float]] = []
            for i in range(num_initial_points):
                angle: float = (i / num_initial_points) * 2 * math.pi
                radius: float = avg_radius * random.uniform(0.8, 1.2)
                x: float = center_x + radius * math.cos(angle)
                y: float = center_y + radius * math.sin(angle)
                points.append([x, y])

            # 2. Refinamento Iterativo (Deslocamento de Ponto Médio)
            for i in range(iterations):
                new_points: List[List[float]] = []
                # A magnitude do deslocamento diminui a cada iteração
                displacement_scaler: float = (roughness * avg_radius) / (2 ** i)

                for j in range(len(points)):
                    p1: List[float] = points[j]
                    p2: List[float] = points[(j + 1) % len(points)]  # Pega o próximo ponto, voltando ao início no final
                    
                    # Adiciona o ponto inicial do segmento
                    new_points.append(p1)

                    # Calcula o ponto médio
                    mid_x: float = (p1[0] + p2[0]) / 2
                    mid_y: float = (p1[1] + p2[1]) / 2

                    # Calcula o vetor normal ao segmento (para a direção do deslocamento)
                    dx: float = p2[0] - p1[0]
                    dy: float = p2[1] - p1[1]
                    normal: pygame.math.Vector2 = pygame.math.Vector2(-dy, dx).normalize()

                    # Gera o deslocamento aleatório
                    displacement: float = random.uniform(-1, 1) * displacement_scaler
                    
                    # Aplica o deslocamento ao ponto médio
                    displaced_mid_x: float = mid_x + normal.x * displacement
                    displaced_mid_y: float = mid_y + normal.y * displacement

                    new_points.append([displaced_mid_x, displaced_mid_y])
                points = new_points

            # 3. Desenha o polígono fractal final na máscara
            mask_layer: pygame.Surface = pygame.Surface(base_surface.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(mask_layer, (255, 255, 255, 255), points)

            # 4. Aplica a textura usando a máscara
            texture_layer: pygame.Surface = pygame.Surface(base_surface.get_size())
            tex_w, tex_h = texture.get_size()
            for x_tile in range(0, width, tex_w):
                for y_tile in range(0, height, tex_h):
                    texture_layer.blit(texture, (x_tile, y_tile))
            
            texture_layer.blit(mask_layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            texture_layer.set_colorkey((0, 0, 0))
            base_surface.blit(texture_layer, (0, 0))

        # 1. Camada de Areia (base) - Maior, menos iterações, mais "áspera"
        generate_fractal_layer(self.image, Island.SAND_TEXTURE, radius_scaler=0.4, iterations=5, roughness=0.8)

        # 2. Camada de Grama (sobre a areia) - Média, mais detalhada
        generate_fractal_layer(self.image, Island.GRASS_TEXTURE, radius_scaler=0.25, iterations=6, roughness=0.6)

        # 3. Camada de Floresta (sobre a grama) - Menor, mais "suave"
        generate_fractal_layer(self.image, Island.FOREST_TEXTURE, radius_scaler=0.15, iterations=4, roughness=0.4)

        # Define uma opacidade geral aleatória para a ilha
        self.image.set_alpha(random.randint(opacity_range[0], opacity_range[1]))  # 0 (transparente) a 255 (opaco)

        # Define a posição inicial da ilha
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = (
            random.randint(0, SCREEN_WIDTH),
            -self.rect.height // 2  # Inicia um pouco acima da tela
        )
        
        # Velocidade de rolagem, igual à do fundo
        self.speed_y: int = 1

    def update(self) -> None:
        """
        Atualiza a posição da ilha na tela.

        Move a ilha para baixo e a remove do grupo de sprites se ela sair completamente da tela.
        """
        self.rect.y += self.speed_y
        # Remove a ilha quando ela sai completamente da tela
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
