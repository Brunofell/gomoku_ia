import os # limpar a tela
import time  # medir o tempo de cada jogada
import math  # math.inf que o minimax precisa

# Constantes e Board do Gomoku
from param import *
from gomoku import Board

#-----------------------------------
## helpers
#-----------------------------------

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


#-----------------------------------
## beginner level functions
#-----------------------------------

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


#-----------------------------------
## intermediate level functions
#-----------------------------------


def heuristic_intermediate(board):
    # na descricao do trabalho, eram sugeridas:
    # - sequências abertas e fechadas -- vou implementar essa com penalizacao crescente
    # - bônus por centralidade -- vou manter essa relativamente simples, definir "zonas" e um peso
    # - bloqueios imediatos de ameaças do oponente -- ver se vai dar tempo ou se o primeiro caso contempla isso de forma indireta

    # checando se ja ha vencedor
    if board.check_win(WHITE):
        return 100000
    if board.check_win(BLACK):
        return -100000
    
    # inicializa sem nada de score
    score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    # iterando nas rows e columns do tabuleiro
    for r in range(SIZE):
        for c in range(SIZE):
            player = board.grid[r][c]
            if player == EMPTY:
                continue
            for dr, dc in directions:
                # evita contar mesma sequência múltiplas vezes
                prev_r = r - dr
                prev_c = c - dc
                if 0 <= prev_r < SIZE and 0 <= prev_c < SIZE:
                    if board.grid[prev_r][prev_c] == player:
                        continue
                # conta sequência
                count = 0
                nr = r
                nc = c
                while 0 <= nr < SIZE and 0 <= nc < SIZE:
                    if board.grid[nr][nc] != player:
                        break
                    count += 1
                    nr += dr
                    nc += dc
                # verifica extremidade final
                open_1 = False
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    if board.grid[nr][nc] == EMPTY:
                        open_1 = True
                # verifica extremidade inicial
                back_r = r - dr
                back_c = c - dc
                open_2 = False
                if 0 <= back_r < SIZE and 0 <= back_c < SIZE:
                    if board.grid[back_r][back_c] == EMPTY:
                        open_2 = True
                open_ends = 0
                if open_1:
                    open_ends += 1
                if open_2:
                    open_ends += 1
                value = 0

                # =================================================
                # SEQUÊNCIAS ABERTAS / FECHADAS
                # =================================================
                if count == 2:
                    if open_ends == 2:
                        value = 50
                    elif open_ends == 1:
                        value = 10
                elif count == 3:
                    if open_ends == 2:
                        value = 500
                    elif open_ends == 1:
                        value = 100
                elif count == 4:
                    if open_ends == 2:
                        value = 5000
                    elif open_ends == 1:
                        value = 2000
                elif count >= 5:
                    value = 100000

                # =================================================
                # BÔNUS POR CENTRALIDADE
                # =================================================

                center_bonus = (
                    (4 - abs(4 - r)) +
                    (4 - abs(4 - c))
                )
                value += center_bonus

                # =================================================
                # BLOQUEIO IMEDIATO DE AMEAÇAS
                # =================================================
                # forte penalização para ameaças do humano
                if player == BLACK:
                    if count == 4 and open_ends >= 1:
                        value *= 4
                    elif count == 3 and open_ends == 2:
                        value *= 2

                # =================================================
                # APLICA SCORE
                # =================================================
                if player == WHITE:
                    score += value
                else:
                    score -= value
    return score

def minimax_intermediate(board, depth, alpha, beta, maximizing, heuristic_fn):
    # checando condicaoes de parada
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
            val = minimax_intermediate(copy, depth - 1, alpha, beta, False, heuristic_fn)
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
            val = minimax_intermediate(copy, depth - 1, alpha, beta, True, heuristic_fn)
            if val < best:
                best = val
            if val < beta:
                beta = val
            if beta <= alpha:
                break
        return best


def best_move_intermediate(board, heuristic_fn):
    best_move = None
    best_val = -math.inf
    for move in get_candidates(board):
        r = move[0]
        c = move[1]
        copy = board.copy()
        copy.place(r, c, WHITE)
        val = minimax_intermediate(copy, INTERMEDIATE_DEPTH - 1, -math.inf, math.inf, False, heuristic_fn)
        if val > best_val:
            best_val = val
            best_move = move
    return best_move, best_val

#-----------------------------------
## pro level functions
#-----------------------------------


def heuristic_pro(board):
    pass


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


#-----------------------------------
## playing the game
#-----------------------------------


# Loop principal do jogo — alterna os turnos entre humano e IA até alguém vencer ou empatar
def play():
    os.system("cls")
    print("=== GOMOKU 9x9 ===")
    print("Voce: X (Preto) | IA: O (Branco)")
    print("Coordenadas: letra (A-I) + numero (1-9). Ex: E5")
    level = input("Escola o nivel de dificuldade (beginner / intermediate /  pro): ")

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
            # selecionando o nivel de dificuldade
            if level == "beginner":
                #heuristic_fn = heuristic_beginner
                #move, val = best_move_beginner(board, heuristic_fn)
                move, val = best_move_beginner(board)
            elif level == "intermediate":
                heuristic_fn = heuristic_intermediate
                move, val = best_move_intermediate(board, heuristic_fn)
            else:
                heuristic_fn = heuristic_pro
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