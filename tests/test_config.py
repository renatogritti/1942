"""
Testes para o módulo de configuração.
"""
import pytest
import sys
import os

# Adiciona o diretório pai ao path para permitir imports dos módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    FPS, 
    DIFFICULTY_STAGES,
    INITIAL_DIFFICULTY_STAGE_INDEX
)


class TestConfig:
    """Testes das configurações do jogo."""
    
    def test_screen_dimensions_are_positive(self):
        """Testa se as dimensões da tela são valores positivos."""
        assert SCREEN_WIDTH > 0
        assert SCREEN_HEIGHT > 0
        assert isinstance(SCREEN_WIDTH, int)
        assert isinstance(SCREEN_HEIGHT, int)
    
    def test_fps_is_valid(self):
        """Testa se FPS é um valor válido."""
        assert FPS > 0
        assert FPS <= 120  # Limite razoável
        assert isinstance(FPS, int)
    
    def test_difficulty_stages_structure(self):
        """Testa a estrutura dos estágios de dificuldade."""
        assert isinstance(DIFFICULTY_STAGES, list)
        assert len(DIFFICULTY_STAGES) > 0
        
        # Testa se todos os estágios têm as chaves necessárias
        required_keys = {
            "score_threshold", "enemy_spawn_delay", "enemy_speed_y",
            "enemy_speed_x", "enemy_shoot_delay", "enemy_bullet_speed",
            "enemy_types_available"
        }
        
        for stage in DIFFICULTY_STAGES:
            assert isinstance(stage, dict)
            assert required_keys.issubset(stage.keys())
            assert stage["score_threshold"] >= 0
            assert isinstance(stage["enemy_types_available"], list)
    
    def test_difficulty_progression(self):
        """Testa se a dificuldade aumenta progressivamente."""
        for i in range(1, len(DIFFICULTY_STAGES)):
            current = DIFFICULTY_STAGES[i]
            previous = DIFFICULTY_STAGES[i-1]
            
            # Score threshold deve aumentar
            assert current["score_threshold"] > previous["score_threshold"]
    
    def test_initial_difficulty_index(self):
        """Testa se o índice inicial de dificuldade é válido."""
        assert 0 <= INITIAL_DIFFICULTY_STAGE_INDEX < len(DIFFICULTY_STAGES)