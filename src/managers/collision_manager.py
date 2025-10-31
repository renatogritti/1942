import pygame
import random
from typing import Any, Dict, Tuple, Callable

from src.game_objects.player import Player
from src.game_objects.enemy import Enemy
from src.game_objects.bullet import Bullet, EnemyBullet
from src.game_objects.coin import Coin
from src.game_objects.effects import Explosion, GifExplosion
from src.game_objects.powerups import BombPowerUp, AmmoPowerUp # Novo import

class CollisionManager:
    def __init__(self, all_sprites_group: pygame.sprite.Group,
                 player_bullets_group: pygame.sprite.Group,
                 enemies_group: pygame.sprite.Group,
                 enemy_bullets_group: pygame.sprite.Group,
                 coins_group: pygame.sprite.Group,
                 powerups_group: pygame.sprite.Group, # Novo grupo
                 sound_manager: Any, # Pode ser mais específico se SoundManager for um tipo
                 score_callback: Callable[[int], None], # Callback para adicionar pontuação
                 game_over_callback: Callable[[], None], # Callback para game over
                 player_instance: Player,
                 get_current_phase_index: Callable[[], int]): # Adiciona o getter da fase
        
        self.all_sprites = all_sprites_group
        self.player_bullets = player_bullets_group
        self.enemies = enemies_group
        self.enemy_bullets = enemy_bullets_group
        self.coins = coins_group
        self.powerups = powerups_group # Armazena o novo grupo
        self.sound_manager = sound_manager
        self.score_callback = score_callback
        self.game_over_callback = game_over_callback
        self.player = player_instance
        self.get_current_phase_index = get_current_phase_index # Armazena o getter da fase

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

    def check_all_collisions(self, current_phase_index: int) -> None:
        """
        Verifica e processa todas as colisões entre os diferentes elementos do jogo.
        Inclui colisões entre tiros do jogador e inimigos, tiros do jogador e tiros inimigos,
        jogador e inimigos, jogador e tiros inimigos, e jogador e moedas.
        """
        # Tiros do jogador com inimigos
        hits: Dict[pygame.sprite.Sprite, Any] = pygame.sprite.groupcollide(self.player_bullets, self.enemies, True, True)
        for enemies_hit in hits.values():
            for enemy in enemies_hit:
                if enemy.type == 'straight':
                    self.score_callback(10)
                elif enemy.type == 'weaving':
                    self.score_callback(20)
                elif enemy.type == 'diving':
                    self.score_callback(30)
                else:
                    self.score_callback(10)

                self.sound_manager.play_sound('explosion')
                # Adiciona ambos os efeitos de explosão
                particle_explosion = Explosion(enemy.rect.center)
                gif_explosion = GifExplosion(enemy.rect.center, size=64)
                self.all_sprites.add(particle_explosion, gif_explosion)
                
                # Lógica para dropar power-ups ou moedas
                drop_chance = random.random()
                if drop_chance < 0.2: # 20% de chance de dropar um power-up
                    powerup_type_chance = random.random()
                    if powerup_type_chance < 0.5: # 50% de chance de ser bomba
                        new_powerup = BombPowerUp(enemy.rect.center)
                    else: # 50% de chance de ser munição
                        new_powerup = AmmoPowerUp(enemy.rect.center)
                    self.all_sprites.add(new_powerup)
                    self.powerups.add(new_powerup)
                elif drop_chance < 0.5:  # 30% de chance de dropar moeda (0.2 a 0.5)
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

        # Colisão do jogador com power-ups
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            self.sound_manager.play_sound('coin') # Reutiliza o som da moeda por enquanto
            if isinstance(powerup, BombPowerUp):
                self.player.add_bomb(1)
            elif isinstance(powerup, AmmoPowerUp):
                # Lógica de upgrade de arma baseada na fase
                current_phase = self.get_current_phase_index() + 1 # Fases são 1-indexed para o usuário
                if current_phase >= 2 and self.player.weapon_type == "single":
                    self.player.change_weapon("double")
                elif current_phase >= 3 and self.player.weapon_type == "double":
                    self.player.change_weapon("triple")
                # Se já for triple ou fase < 2, não faz nada com AmmoPowerUp
