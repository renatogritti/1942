# 1942 Clone

Um clone simples do clássico jogo de arcade 1942, desenvolvido com Pygame.

## Funcionalidades

*   **Controles:** Movimento do jogador, tiro e bombas.
*   **Inimigos:** Diferentes tipos de inimigos com padrões de movimento variados (reto, ziguezague, mergulho).
*   **Dificuldade Dinâmica:** A dificuldade do jogo aumenta progressivamente com a pontuação, ajustando a velocidade dos inimigos, frequência de spawn e padrões de tiro.
*   **Recorde:** Salva e exibe o recorde de pontuação.
*   **Tela de Splash:** Uma tela inicial com o logo do jogo.
*   **Tela de Game Over:** Exibida ao perder todas as vidas, com pontuação, recorde e opções de reiniciar ou sair.
*   **Sair do Jogo:** Pressione 'Q' a qualquer momento para sair.

## Como Rodar

Para executar o jogo, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd 1942
    ```
    (Substitua `<URL_DO_REPOSITORIO>` pela URL real do seu repositório Git.)

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv .venv
    # No Windows
    .venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o jogo:**
    Certifique-se de estar no diretório raiz do projeto (`1942/`) e execute:
    ```bash
    python main.py
    ```

## Controles

*   **Setas do Teclado (CIMA, BAIXO, ESQUERDA, DIREITA):** Mover o avião do jogador.
*   **CTRL (Esquerdo ou Direito):** Atirar.
*   **ALT (Esquerdo ou Direito):** Usar bomba (limite de uso).
*   **Q:** Sair do jogo (a qualquer momento).
*   **N (na tela de Game Over):** Iniciar um novo jogo.

## Requisitos

*   Python 3.x
*   Pygame
*   Pillow (PIL Fork)

As dependências exatas estão listadas em `requirements.txt`.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
