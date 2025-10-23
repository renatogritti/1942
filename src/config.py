# src/config.py

"""Configurações globais e estágios de dificuldade para o jogo 1942 Clone."""

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Player settings
PLAYER_SPEED = 5

# Difficulty Settings
DIFFICULTY_STAGES = [
    # Stage 0: Very Easy (Initial)
    {
        "score_threshold": 0,
        "enemy_spawn_delay": (1500, 2500), # ms (min, max)
        "enemy_speed_y": (3, 4),
        "enemy_speed_x": (1, 2),
        "enemy_shoot_delay": (1000, 1500),
        "enemy_bullet_speed": 5,
        "enemy_types_available": ["straight", "weaving"],    },
    # Stage 1: Easy
    {
        "score_threshold": 500,
        "enemy_spawn_delay": (1200, 2000),
        "enemy_speed_y": (4, 5),
        "enemy_speed_x": (2, 3),
        "enemy_shoot_delay": (900, 1400),
        "enemy_bullet_speed": 6,
        "enemy_types_available": ["straight", "weaving"],
    },
    # Stage 2: Medium
    {
        "score_threshold": 1500,
        "enemy_spawn_delay": (1000, 1800),
        "enemy_speed_y": (5, 6),
        "enemy_speed_x": (2, 4),
        "enemy_shoot_delay": (800, 1300),
        "enemy_bullet_speed": 7,
        "enemy_types_available": ["straight", "weaving", "diving"],
    },
    # Stage 3: Hard
    {
        "score_threshold": 3000,
        "enemy_spawn_delay": (800, 1500),
        "enemy_speed_y": (6, 7),
        "enemy_speed_x": (3, 5),
        "enemy_shoot_delay": (700, 1200),
        "enemy_bullet_speed": 8,
        "enemy_types_available": ["straight", "weaving", "diving"],
    },
    # Stage 4: Very Hard (and beyond, difficulty caps here for now)
    {
        "score_threshold": 5000,
        "enemy_spawn_delay": (600, 1200),
        "enemy_speed_y": (7, 8),
        "enemy_speed_x": (4, 6),
        "enemy_shoot_delay": (600, 1100),
        "enemy_bullet_speed": 9,
        "enemy_types_available": ["straight", "weaving", "diving"],
    },
]

# Initial difficulty stage
INITIAL_DIFFICULTY_STAGE_INDEX = 0