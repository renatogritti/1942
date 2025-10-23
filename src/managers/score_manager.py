"""
Projeto: Clone 1942
Descrição: Módulo responsável por gerenciar o recorde de pontuação do jogo.
           Inclui funcionalidades para carregar e salvar o recorde em um arquivo.
Autoria: Renato Gritti
"""

class ScoreManager:
    """
    Gerencia o recorde de pontuação do jogo.

    Responsável por carregar o recorde de um arquivo e salvá-lo quando um novo recorde é atingido.
    """
    def __init__(self) -> None:
        """
        Inicializa o ScoreManager e carrega o recorde existente.
        """
        self.highscore: int = 0
        self._load_highscore()

    def _load_highscore(self) -> None:
        """
        Carrega o recorde de pontuação de um arquivo.

        Se o arquivo não existir ou o conteúdo for inválido, o recorde é definido como 0.
        """
        try:
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read())
        except (FileNotFoundError, ValueError):
            self.highscore = 0

    def save_highscore(self, current_score: int) -> None:
        """
        Salva a pontuação atual como novo recorde se for maior que o recorde existente.

        O recorde é salvo em um arquivo de texto.

        Args:
            current_score (int): A pontuação atual do jogador.
        """
        if current_score > self.highscore:
            self.highscore = current_score
            with open("highscore.txt", "w") as f:
                f.write(str(self.highscore))

    def get_highscore(self) -> int:
        """
        Retorna o recorde de pontuação atual.

        Returns:
            int: O recorde de pontuação.
        """
        return self.highscore
