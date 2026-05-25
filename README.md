# TDE 2 - Gomoku utilizando IA

O objetivo do trabalho é desenvolver um Agente Inteligente capaz de jogar **Gomoku (Cinco‑em‑Linha)** em um tabuleiro de 9×9, enfrentando um jogador humano. O trabalho tem como foco aplicar técnicas de busca adversária, especialmente Minimax, poda alfa‑beta, heurísticas, ordenação de movimentos, controle de tempo e profundidade de busca, conforme apresentado na disciplina.

## Requisitos

- O tabuleiro deve ter dimensão 9x9.
- O primeiro movimento sempre será do Agente Humano (peças pretas), que escolhe a coordenada (linha e coluna) de jogada pressionando (como A5, D7, etc.).
- O Agente Inteligente (peças brancas) deverá ter três níveis de capacidade de jogo, sendo definido antes da partida:
  1. iniciante
  2. intermediário
  3. profissional


Após cada jogada, devem ser apresentadas três informações:

1. Estado atual do tabuleiro em formato visual:
   - matriz
   - indicações dos jogadores

2. Tempo gasto na jogada.

3. Valor obtido pela função de avaliação para o estado atual.

Ao final da partida, deve ser indicado quem venceu a partida ou se houve empate

---