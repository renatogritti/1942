import pygame
import random
from typing import Any, Dict, Tuple, Callable

from src.game_objects.player import Player
from src.game_objects.enemy import Enemy
from src.game_objects.bullet import Bullet, EnemyBullet
from src.game_objects.coin import Coin
from src.game_objects.effects import Explosion, GifExplosion

class CollisionManager:
    def __init__(self, all_sprites_group: pygame.sprite.Group,
                 player_bullets_group: pygame.sprite.Group,
                 enemies_group: pygame.sprite.Group,
                 enemy_bullets_group: pygame.sprite.Group,
                 coins_group: pygame.sprite.Group,
                 sound_manager: Any, # Pode ser mais específico se SoundManager for um tipo
                 score_callback: Callable[[int], None], # Callback para adicionar pontuação
                 game_over_callback: Callable[[Any], None], # Callback para game over
                 player_instance: Player): # Passa a instância do player para atualizar energia/bombas
        
        self.all_sprites = all_sprites_group
        self.player_bullets = player_bullets_group
        self.enemies = enemies_group
        self.enemy_bullets = enemy_bullets_group
        self.coins = coins_group
        self.sound_manager = sound_manager
        self.score_callback = score_callback
        self.game_over_callback = game_over_callback
        self.player = player_instance

    def _bullet_hit_enemy_bullet(self, player_bullet: Bullet, enemy_bullet: EnemyBullet) -> bool:
        """
        Callback de colisão para pygame.sprite.groupcollide.
        Esta função é usada para determinar a colisão entre um tiro do jogador e um tiro inimigo.
        Ela infla o retângulo (rect) do tiro inimigo para uma área de colisão maior,
        simulando uma área de impacto mais generosa para o tiro inimigo.
        Args:
            player_bullet (Bullet): O sprite do tiro disparado pelo jogador.
            enemy_bullet (EnemyBullet): O sprite do tiro disparado por um inimigo.
        Returns:
            bool: True se houver colisão entre os retângulos inflados, False caso contrário.
        """
        inflated_rect = enemy_bullet.rect.inflate(20, 20)
        return inflated_rect.colliderect(player_bullet.rect)

    def check_all_collisions(self) -> None:
        """
        Verifica e processa todas as colisões entre os diferentes elementos do jogo.
        Inclui colisões entre tiros do jogador e inimigos, tiros do jogador e tiros inimigos,
        jogador e inimigos, jogador e tiros inimigos, e jogador e moedas.
        """
        # Tiros do jogador com inimigos
        hits: Dict[pygame.sprite.Sprite, Any] = pygame.sprite.groupcollide(self.player_bullets, self.enemies, True, True)
        for enemies_hit in hits.values():
            for enemy in enemies_hit:
                self.score_callback(10) # Adiciona 10 pontos
                self.sound_manager.play_sound('explosion')
                # Adiciona ambos os efeitos de explosão
                particle_explosion = Explosion(enemy.rect.center)
                gif_explosion = GifExplosion(enemy.rect.center, size=64)
                self.all_sprites.add(particle_explosion, gif_explosion)
                if random.random() > 0.7:  # 30% de chance de dropar moeda
                    coin = Coin(enemy.rect.center)
                    self.all_sprites.add(coin)
                    self.coins.add(coin)

        # Tiros do jogador com tiros inimigos
        pygame.sprite.groupcollide(self.player_bullets, self.enemy_bullets, True, True, self._bullet_hit_enemy_bullet)

        # Colisão do jogador com inimigos
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            self.player.energy -= 30
            # Adiciona ambos os efeitos de explosão
            particle_explosion = Explosion(hit.rect.center)
            gif_explosion = GifExplosion(hit.rect.center, size=64)
            self.all_sprites.add(particle_explosion, gif_explosion)
            if self.player.energy <= 0:
                self.game_over_callback()

        # Colisão do jogador com tiros inimigos
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for hit in hits:
            self.player.energy -= 10
            if self.player.energy <= 0:
                self.game_over_callback()

        # Colisão do jogador com moedas
        hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for hit in hits:
            self.sound_manager.play_sound('coin')
            self.player.energy = min(self.player.max_energy, self.player.energy + 20)
