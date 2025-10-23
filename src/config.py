"""
Projeto: Clone 1942
Descrição: Módulo de configuração global para o jogo 1942 Clone.
           Define constantes para dimensões da tela, cores, configurações do jogador
           e os diferentes estágios de dificuldade do jogo.
Autoria: Renato Gritti
"""

from typing import List, Dict, Any, Tuple

# Dimensões da tela
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60

# Cores
BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)

# Configurações do jogador
PLAYER_SPEED: int = 5

# Estágios de Dificuldade
DIFFICULTY_STAGES: List[Dict[str, Any]] = [
    # Estágio 0: Muito Fácil (Inicial)
    {
        "score_threshold": 0,
        "enemy_spawn_delay": (1500, 2500),  # ms (min, max)
        "enemy_speed_y": (3, 4),
        "enemy_speed_x": (1, 2),
        "enemy_shoot_delay": (1000, 1500),
        "enemy_bullet_speed": 5,
        "enemy_types_available": ["straight", "weaving"],
    },
    # Estágio 1: Fácil
    {
        "score_threshold": 100,
        "enemy_spawn_delay": (1200, 2000),
        "enemy_speed_y": (4, 5),
        "enemy_speed_x": (2, 3),
        "enemy_shoot_delay": (900, 1400),
        "enemy_bullet_speed": 6,
        "enemy_types_available": ["straight", "weaving"],
    },
    # Estágio 2: Médio
    {
        "score_threshold": 300,
        "enemy_spawn_delay": (1000, 1800),
        "enemy_speed_y": (5, 6),
        "enemy_speed_x": (2, 4),
        "enemy_shoot_delay": (800, 1300),
        "enemy_bullet_speed": 7,
        "enemy_types_available": ["straight", "weaving", "diving"],
    },
    # Estágio 3: Difícil
    {
        "score_threshold": 500,
        "enemy_spawn_delay": (800, 1500),
        "enemy_speed_y": (6, 7),
        "enemy_speed_x": (3, 5),
        "enemy_shoot_delay": (700, 1200),
        "enemy_bullet_speed": 8,
        "enemy_types_available": ["straight", "weaving", "diving"],
    },
    # Estágio 4: Muito Difícil (e além, a dificuldade se limita aqui por enquanto)
    {
        "score_threshold": 1000,
        "enemy_spawn_delay": (600, 1200),
        "enemy_speed_y": (7, 8),
        "enemy_speed_x": (4, 6),
        "enemy_shoot_delay": (600, 1100),
        "enemy_bullet_speed": 9,
        "enemy_types_available": ["straight", "weaving", "diving"],
    },
]

# Índice do estágio de dificuldade inicial
INITIAL_DIFFICULTY_STAGE_INDEX: int = 0
