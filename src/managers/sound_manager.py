"""
Projeto: Clone 1942
Descrição: Módulo responsável por gerenciar todos os efeitos sonoros e músicas do jogo.
           Permite carregar, reproduzir, parar e ajustar o volume dos sons de forma centralizada.
Autoria: Renato Gritti
"""

import pygame
from typing import Dict, Optional

class SoundManager:
    """
    Gerencia o carregamento e a reprodução de sons e músicas no jogo.

    Centraliza a lógica de áudio, permitindo fácil acesso e controle sobre os recursos sonoros.
    """
    def __init__(self) -> None:
        """
        Inicializa o SoundManager e carrega todos os sons do jogo.
        """
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._load_sounds()

    def _load_sounds(self) -> None:
        """
        Carrega todos os arquivos de som necessários para o jogo.

        Os sons são armazenados em um dicionário para fácil acesso.
        Define o volume para alguns sons.
        """
        try:
            self.sounds['splash'] = pygame.mixer.Sound("assets/sounds/Splash.wav")
            self.sounds['initial'] = pygame.mixer.Sound("assets/sounds/Inicial.wav")
            self.sounds['motor'] = pygame.mixer.Sound("assets/sounds/Motor.wav")
            self.sounds['explosion'] = pygame.mixer.Sound("assets/sounds/Explosao.wav")
            self.sounds['gameover'] = pygame.mixer.Sound("assets/sounds/Gameover.wav")
            self.sounds['tiro'] = pygame.mixer.Sound("assets/sounds/Tiro.wav")
            self.sounds['coin'] = pygame.mixer.Sound("assets/sounds/Coin.wav")
            self.sounds['newphase'] = pygame.mixer.Sound("assets/sounds/Newphase.wav")

            self.sounds['motor'].set_volume(0.3)
        except pygame.error as e:
            print(f"Erro ao carregar som: {e}")

    def play_sound(self, name: str, loops: int = 0) -> None:
        """
        Reproduz um som específico pelo nome.

        Args:
            name (str): O nome do som a ser reproduzido (chave no dicionário self.sounds).
            loops (int): Número de vezes para repetir o som. -1 para loop infinito, 0 para tocar uma vez.
        """
        if name in self.sounds:
            self.sounds[name].play(loops=loops)

    def stop_sound(self, name: str) -> None:
        """
        Para a reprodução de um som específico pelo nome.

        Args:
            name (str): O nome do som a ser parado.
        """
        if name in self.sounds:
            self.sounds[name].stop()

    def stop_all_sounds(self) -> None:
        """
        Para a reprodução de todos os sons, mas não a música de fundo.
        """
        for sound in self.sounds.values():
            sound.stop()

    def play_background_music(self, filename: str, loops: int = -1, volume: float = 1.0) -> None:
        """
        Carrega e reproduz uma música de fundo em loop.

        Args:
            filename (str): O caminho para o arquivo de música.
            loops (int): Número de vezes para repetir a música. -1 para loop infinito.
            volume (float): O volume da música (0.0 a 1.0).
        """
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=loops)
        except pygame.error as e:
            print(f"Erro ao carregar ou tocar a música de fundo: {e}")

    def stop_background_music(self) -> None:
        """
        Para a reprodução da música de fundo.
        """
        pygame.mixer.music.stop()
