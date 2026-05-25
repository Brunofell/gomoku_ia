import time  # Medir o tempo de cada jogada
import math  # math.inf que o minimax precisa

# Constantes e Board do Gomoku
from param import *
from gomoku import Board

# Converte o texto digitado pelo usuário (ex: "E5") em (row, col) — retorna None se for inválido
def parse_move(text):
    text = text.strip().upper()
    if len(text) < 2:
        return None
    letter = text[0]
    if letter not in COLS:
        return None
    number = int(text[1:])
    col = COLS.index(letter)
    row = number - 1
    return (row, col)


# Retorna o oponente do jogador atual — se for BLACK retorna WHITE e vice-versa
def opponent(player):
    if player == BLACK:
        return WHITE
    else:
        return BLACK


# Retorna a lista de casas vazias próximas às peças já jogadas — reduz o espaço de busca do minimax
def get_candidates(board):
    candidates = [] # jogadas relevantes
    has_piece = False # detecta tabuleiro vazio
    for r in range(SIZE):
        for c in range(SIZE): # percorre tabuleiro
            if board.grid[r][c] == EMPTY: # ignora vazios
                continue
            has_piece = True # se achar peça
            for dr in range(-1, 2):
                for dc in range(-1, 2): # vai varrer todas casas ao redor
                    nr = r + dr
                    nc = c + dc # calcula vizinho da peça 
                    if nr < 0 or nr >= SIZE or nc < 0 or nc >= SIZE: # evita sair da matriz
                        continue
                    if board.grid[nr][nc] == EMPTY:
                        if (nr, nc) not in candidates:
                            candidates.append((nr, nc))
    if has_piece == False:
        return [(4, 4)]
    return candidates


# Conta os pontos de sequências de peças do jogador em todas as direções — usado pela heurística
def count_sequences(board, player):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    total = 0
    for r in range(SIZE):
        for c in range(SIZE):
            if board.grid[r][c] != player:
                continue
            for dr, dc in directions:
                count = 0
                nr = r
                nc = c
                while nr >= 0 and nr < SIZE and nc >= 0 and nc < SIZE:
                    if board.grid[nr][nc] != player:
                        break
                    count = count + 1
                    nr = nr + dr
                    nc = nc + dc
                if count > 5:
                    count = 5
                if count > 0:
                    total = total + SCORE_TABLE[count]
    return total


# Avalia o estado do tabuleiro e retorna uma nota — positivo é bom para a IA, negativo é bom para o humano
def heuristic_beginner(board):
    if board.check_win(WHITE):
        return 100000
    if board.check_win(BLACK):
        return -100000
    ai_pts = count_sequences(board, WHITE)
    hum_pts = count_sequences(board, BLACK)
    return ai_pts - hum_pts


# Algoritmo minimax sem poda alfa-beta — explora todas as jogadas até a profundidade definida
def minimax(board, depth, maximizing):
    if board.check_win(WHITE): # checa vitória
        return 100000
    if board.check_win(BLACK):
        return -100000
    if depth == 0 or board.is_full():
        return heuristic_beginner(board)

    moves = get_candidates(board)

    if maximizing == True:
        best = -math.inf
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy()
            copy.place(r, c, WHITE)
            val = minimax(copy, depth - 1, False)
            if val > best:
                best = val
        return best
    else:
        best = math.inf
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy()
            copy.place(r, c, BLACK)
            val = minimax(copy, depth - 1, True)
            if val < best:
                best = val
        return best


# Escolhe a melhor jogada para o nível iniciante — testa cada candidato com o minimax e retorna o melhor
def best_move_beginner(board):
    best_val = -math.inf
    best_move = None
    moves = get_candidates(board)
    for move in moves:
        r = move[0]
        c = move[1]
        copy = board.copy()
        copy.place(r, c, WHITE)
        val = minimax(copy, BEGINNER_DEPTH - 1, False)
        if val > best_val:
            best_val = val
            best_move = move
    return best_move, best_val


# Exceção usada para interromper o minimax quando o tempo limite é atingido
class TimeOut(Exception):
    pass


# Minimax com poda alfa-beta e verificação de tempo — interrompe a busca se o deadline for ultrapassado
def minimax_pro(board, depth, alpha, beta, maximizing, deadline, heuristic_fn):
    if time.time() >= deadline:
        raise TimeOut()
    if board.check_win(WHITE):
        return 100000
    if board.check_win(BLACK):
        return -100000
    if depth == 0 or board.is_full():
        return heuristic_fn(board)
    moves = get_candidates(board)
    if maximizing == True:
        best = -math.inf
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy()
            copy.place(r, c, WHITE)
            val = minimax_pro(copy, depth - 1, alpha, beta, False, deadline, heuristic_fn)
            if val > best:
                best = val
            if val > alpha:
                alpha = val
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy()
            copy.place(r, c, BLACK)
            val = minimax_pro(copy, depth - 1, alpha, beta, True, deadline, heuristic_fn)
            if val < best:
                best = val
            if val < beta:
                beta = val
            if beta <= alpha:
                break
        return best


# Iterative Deepening — vai aumentando a profundidade enquanto houver tempo, usa o melhor resultado completo
def best_move_pro(board, heuristic_fn):
    start = time.time()
    deadline = start + TIME_LIMIT
    best_move = None
    best_val = -math.inf
    depth_reached = 0
    depth = 1
    while depth < 20:
        move_this_depth = None
        val_this_depth = -math.inf
        failed = False
        try:
            for move in get_candidates(board):
                r = move[0]
                c = move[1]
                copy = board.copy()
                copy.place(r, c, WHITE)
                val = minimax_pro(copy, depth - 1, -math.inf, math.inf, False, deadline, heuristic_fn)
                if val > val_this_depth:
                    val_this_depth = val
                    move_this_depth = move
            best_move = move_this_depth
            best_val = val_this_depth
            depth_reached = depth
        except TimeOut:
            failed = True
        if failed == True: 
            break
        depth = depth + 1
    return best_move, best_val, depth_reached


# Loop principal do jogo — alterna os turnos entre humano e IA até alguém vencer ou empatar
def play():
    print("=== GOMOKU 9x9 ===")
    print("Voce: X (Preto) | IA: O (Branco)")
    print("Coordenadas: letra (A-I) + numero (1-9). Ex: E5")
    level = input("Nivel (beginner / pro): ")

    board = Board()
    turn = BLACK
    board.display()

    while True:
        if turn == BLACK:
            raw = input("Sua jogada: ")
            move = parse_move(raw)
            if move == None:
                print("Formato invalido! Use ex: E5")
                continue
            ok = board.place(move[0], move[1], BLACK)
            if ok == False:
                print("Posicao ocupada!")
                continue
            board.display()
            if board.check_win(BLACK):
                print("Voce venceu!")
                break
        else:
            print("IA calculando...")
            start = time.time()
            if level == "beginner":
                move, val = best_move_beginner(board)
            else:
                move, val, depth = best_move_pro(board, heuristic_fn)
            elapsed = time.time() - start
            board.place(move[0], move[1], WHITE)
            board.display()
            print("Tempo: " + str(round(elapsed, 4)) + "s")
            print("Valor heuristico: " + str(val))
            if board.check_win(WHITE):
                print("IA venceu!")
                break
        if board.is_full():
            print("Empate!")
            break
        if turn == BLACK:
            turn = WHITE
        else:
            turn = BLACK


if __name__ == "__main__":
    play()