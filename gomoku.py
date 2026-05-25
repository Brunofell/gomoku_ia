from param import *


# Classe principal do jogo — guarda o estado do tabuleiro e tem os métodos para jogar
class Board:

    # Cria o tabuleiro vazio 9x9, célula por célula
    def __init__(self):
        self.grid = []
        self.last_move = None
        for row in range(9):
            empty_row = []
            for col in range(9):
                empty_row.append(0)
            self.grid.append(empty_row)

    # Cria uma cópia independente do tabuleiro — o minimax usa isso para testar jogadas sem alterar o original
    def copy(self):
        new_board = Board()
        new_board.grid = []
        for row in self.grid:
            new_row = []
            for cell in row:
                new_row.append(cell)
            new_board.grid.append(new_row)
        new_board.last_move = self.last_move
        return new_board

    # Coloca uma peça na posição (row, col) — retorna False se a posição já estiver ocupada
    def place(self, row, col, player):
        if self.grid[row][col] != EMPTY:
            return False
        self.grid[row][col] = player
        self.last_move = (row, col)
        return True

    # Verifica se o tabuleiro está completamente cheio — usado para detectar empate
    def is_full(self):
        for row in range(SIZE):
            for col in range(SIZE):
                if self.grid[row][col] == EMPTY:
                    return False
        return True

    # Imprime o tabuleiro no console com as coordenadas A-I e 1-9, destacando a última jogada com [ ]
    def display(self):
        print("    ", end="")
        for letter in COLS:
            print(letter, end="  ")
        print()
        for row in range(SIZE):
            line = str(row + 1) + "  "
            for col in range(SIZE):
                piece = SYMBOLS[self.grid[row][col]]
                if self.last_move == (row, col):
                    line = line + "[" + piece + "]"
                else:
                    line = line + " " + piece + " "
            print(line)

    # Verifica se o jogador fez cinco em linha em qualquer direção (horizontal, vertical ou diagonal)
    def check_win(self, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)] 
        for r in range(SIZE):
            for c in range(SIZE):# visita todas as cel
                if self.grid[r][c] != player:  # ignora vazio
                    continue
                for dr, dc in directions:
                    count = 1
                    nr = r + dr
                    nc = c + dc
                    while nr >= 0 and nr < SIZE and nc >= 0 and nc < SIZE:
                        if self.grid[nr][nc] != player:
                            break
                        count = count + 1
                        nr = nr + dr
                        nc = nc + dc
                    if count >= 5:
                        return True
        return False