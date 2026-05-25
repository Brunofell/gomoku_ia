# Constantes / Parameters

SIZE = 9  # Tamanho do tabuleiro
EMPTY = 0  # Célula vazia
BLACK = 1  # Humano
WHITE = 2  # IA
COLS = "ABCDEFGHI"  # Colunas
SYMBOLS = {EMPTY: ".", BLACK: "X", WHITE: "O"}  # Depois da pra gente tentar colocar algo pra colorir no console de preto e branco, já ouvi falar que da pra fazer algo assim...
SCORE_TABLE = {
    1: 1,
    2: 10,
    3: 100,
    4: 1000,
    5: 100000
}
# Controles da profundidade da poda por nível de dificuldade
BEGINNER_DEPTH = 2
INTERMEDIATE_DEPTH = 4
PRO_DEPTH = 7
TIME_LIMIT = 3.0
