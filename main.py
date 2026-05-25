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
            for dr in range(-1, 2): # gera -1, 0, 1 e não entra em 2
                for dc in range(-1, 2): # vai varrer todas casas ao redor
                    nr = r + dr
                    nc = c + dc # calcula vizinho da peça 
                    if nr < 0 or nr >= SIZE or nc < 0 or nc >= SIZE: # evita sair da matriz
                        continue
                    if board.grid[nr][nc] == EMPTY:
                        if (nr, nc) not in candidates: # evita duplicados
                            candidates.append((nr, nc))
    if has_piece == False:
        return [(4, 4)] # retorna o cento do tabuleiro caso o tab esteja vazio
    return candidates


#-----------------------------------
## beginner level functions
#-----------------------------------

# Conta os pontos de sequências de peças do jogador em todas as direções — usado pela heurística
def count_sequences(board, player):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)] # horizontal, vertical e diagonais
    total = 0 # pontuação total do jogador
    for r in range(SIZE):
        for c in range(SIZE): # percorre todo tabuleiro
            if board.grid[r][c] != player: # ignora peças que não são do jogador atual
                continue
            for dr, dc in directions: # testa todas direções possíveis
                count = 0 # contador da sequência encontrada
                nr = r
                nc = c # começa na posição atual
                while nr >= 0 and nr < SIZE and nc >= 0 and nc < SIZE: # enquanto estiver dentro da matriz
                    if board.grid[nr][nc] != player: # se sequência parar
                        break
                    count = count + 1 # aumenta tamanho da sequência
                    nr = nr + dr # anda linha na direção
                    nc = nc + dc # anda coluna na direção
                if count > 5:
                    count = 5 # limita em 5 porque SCORE_TABLE vai até 5
                if count > 0:
                    total = total + SCORE_TABLE[count] # soma pontuação da sequência
    return total


# Avalia o estado do tabuleiro e retorna uma nota — positivo é bom para a IA, negativo é bom para o humano
def heuristic_beginner(board):
    if board.check_win(WHITE):
        return 100000 # estado extremamente bom para IA
    if board.check_win(BLACK):
        return -100000 # estado extremamente ruim para IA
    ai_pts = count_sequences(board, WHITE) # calcula força da IA
    hum_pts = count_sequences(board, BLACK) # calcula força do humano
    return ai_pts - hum_pts # positivo favorece IA, negativo favorece humano


# Algoritmo minimax sem poda alfa-beta — explora todas as jogadas até a profundidade definida
def minimax(board, depth, maximizing):
    if board.check_win(WHITE): # verifica vitória da IA
        return 100000
    if board.check_win(BLACK): # verifica vitória do humano
        return -100000
    if depth == 0 or board.is_full(): # condição de parada da recursão
        return heuristic_beginner(board) # avalia estado atual do tabuleiro
    
    moves = get_candidates(board) # pega jogadas relevantes próximas das peças
    
    if maximizing == True: # turno da IA (MAX)
        best = -math.inf # começa no menor valor possível
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy() # cria cópia do tabuleiro
            copy.place(r, c, WHITE) # simula jogada da IA
            val = minimax(copy, depth - 1, False) # próxima camada será humano (MIN)
            if val > best:
                best = val # IA escolhe maior valor possível
        return best
    else: # turno do humano (MIN)
        best = math.inf # começa no maior valor possível
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy() # cria cópia do tabuleiro
            copy.place(r, c, BLACK) # simula jogada do humano
            val = minimax(copy, depth - 1, True) # próxima camada será IA (MAX)
            if val < best:
                best = val # humano escolhe pior cenário para IA
        return best


# Escolhe a melhor jogada para o nível iniciante — testa cada candidato com o minimax e retorna o melhor
def best_move_beginner(board):
    best_val = -math.inf # melhor valor encontrado até agora
    best_move = None # melhor jogada encontrada
    moves = get_candidates(board) # pega jogadas relevantes
    for move in moves:
        r = move[0]
        c = move[1]
        copy = board.copy() # cria cópia do tabuleiro
        copy.place(r, c, WHITE) # simula jogada da IA
        val = minimax(copy, BEGINNER_DEPTH - 1, False) # calcula valor da jogada usando minimax
        if val > best_val:
            best_val = val # atualiza melhor valor
            best_move = move # atualiza melhor jogada
    return best_move, best_val # retorna jogada escolhida e valor heurístico


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
    # essencialmente vou fazer a mesma coisa do beginner, mas tbm olhar as pontas
    # a depender se ela foi aberta ou fechada eu penalizo ou beneficio a sequencia
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

                ## sequencias abertas e fechadas
                value = 0
                # se tem duas peças em sequência, é relativamente fraco, mas se tiver as duas pontas abertas é um pouco mais forte
                if count == 2:
                    if open_ends == 2:
                        value = PENALTY_OPEN_END*SCORE_TABLE[count]
                    elif open_ends == 1:
                        value = (1/2)*SCORE_TABLE[count]
                # se tiver três peças em sequência, é uma ameaça, mas se tiver as duas pontas abertas é uma ameaça imediata
                elif count == 3:
                    if open_ends == 2:
                        value = PENALTY_OPEN_END*SCORE_TABLE[count]
                    elif open_ends == 1:
                        value = (1/2)*SCORE_TABLE[count]
                # se tiver quatro peças em sequência, é uma ameaça gravíssima, mas se tiver as duas pontas abertas é uma ameaça de vitória
                elif count == 4:
                    if open_ends == 2:
                        value = PENALTY_OPEN_END*SCORE_TABLE[count]
                    elif open_ends == 1:
                        value = (1/2)*SCORE_TABLE[count]
                # se tiver cinco ou mais peças em sequência, ganhou
                elif count >= 5:
                    value = SCORE_TABLE[count]

                ## bonus pela centralidade
                # aqui a ideia é usar o analogo da formula de distancia ao centro de uma circunferencia
                # com posicao centrada em (4,4)
                center_bonus = (
                    (4 - abs(4 - r)) +
                    (4 - abs(4 - c)))
                value += center_bonus

                ## bloqueio imediato, para isso
                # forte penalização para o humano
                if player == BLACK:
                    if count == 4 and open_ends >= 1:
                        value *= 4
                    elif count == 3 and open_ends == 2:
                        value *= 2

                # calculo score final
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

# aqui a ideia é pegar a heuristica intermediate e expandir ela um pouco mais
def heuristic_pro(board):
    # checando se ja ha vencedor
    if board.check_win(WHITE):
        return 100000
    if board.check_win(BLACK):
        return -100000
    
    # inicializa sem nada de score
    score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]


    # contador para detectar forks / ameaças múltiplas
    # com 3 abertas
    white_open_threes = 0
    black_open_threes = 0
    # com 4 abertas
    white_open_fours = 0
    black_open_fours = 0

    # iterando nas rows e columns do tabuleiro
    # essencialmente vou fazer a mesma coisa do beginner, mas tbm olhar as pontas
    # a depender se ela foi aberta ou fechada eu penalizo ou beneficio a sequencia
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

                ## sequencias abertas e fechadas
                value = 0
                # se tem duas peças em sequência, é relativamente fraco, mas se tiver as duas pontas abertas é um pouco mais forte
                if count == 2:
                    if open_ends == 2:
                        value = PENALTY_OPEN_END*SCORE_TABLE[count]
                    elif open_ends == 1:
                        value = (1/2)*SCORE_TABLE[count]
                # se tiver três peças em sequência, é uma ameaça, mas se tiver as duas pontas abertas é uma ameaça imediata
                elif count == 3:
                    if open_ends == 2:
                        value = PENALTY_OPEN_END*SCORE_TABLE[count]
                        # indo um nivel extra e contando o nro de seq de 3s
                        if player == WHITE:
                            white_open_threes += 1
                        else:
                            black_open_threes += 1
                    elif open_ends == 1:
                        value = (1/2)*SCORE_TABLE[count]
                # se tiver quatro peças em sequência, é uma ameaça gravíssima, mas se tiver as duas pontas abertas é uma ameaça de vitória
                elif count == 4:
                    if open_ends == 2:
                        value = PENALTY_OPEN_END*SCORE_TABLE[count]
                        # agora contando o nro de seq de 4s
                        if player == WHITE:
                            white_open_fours += 1
                        else:
                            black_open_fours += 1
                    elif open_ends == 1:
                        value = (1/2)*SCORE_TABLE[count]
                # se tiver cinco ou mais peças em sequência, ganhou
                elif count >= 5:
                    value = SCORE_TABLE[min(5,count)] #maximo eh 5

                ## bonus pela centralidade
                # aqui a ideia é usar o analogo da formula de distancia ao centro de uma circunferencia
                # com posicao centrada em (4,4)
                center_bonus = (
                    (4 - abs(4 - r)) +
                    (4 - abs(4 - c)))
                value += center_bonus

                ## bloqueio imediato, para isso
                # forte penalização para o humano
                if player == BLACK:
                    if count == 4 and open_ends >= 1:
                        value *= 4
                    elif count == 3 and open_ends == 2:
                        value *= 2

                # calculo score final
                if player == WHITE:
                    score += value
                else:
                    score -= value

    # contamos as seq de 3s e 4s abertas, agora penalizamos elas
    # pego a ordem atual delas pra calcular a penalidade e incrementa ele de uma potencia
    # porem pega apenas metade para a soma
    if white_open_threes >= 2:
        score += (1/2)*SCORE_TABLE[min(5,white_open_threes+1)]
    if black_open_threes >= 2:
        score -= (1/2)*SCORE_TABLE[min(5,black_open_threes+1)]
    if white_open_fours >= 2:
        score += (1/2)*SCORE_TABLE[min(5,white_open_fours+1)]
    if black_open_fours >= 2:
        score -= (1/2)*SCORE_TABLE[min(5,black_open_fours+1)]

    return score


# Exceção usada para interromper o minimax quando o tempo limite é atingido
class TimeOut(Exception):
    pass


# Minimax com poda alfa-beta e verificação de tempo — interrompe a busca se o deadline for ultrapassado
def minimax_pro(board, depth, alpha, beta, maximizing, deadline, heuristic_fn):
    if time.time() >= deadline:
        raise TimeOut() # interrompe toda busca caso tempo acabe
    if board.check_win(WHITE):
        return 100000 # vitória da IA
    if board.check_win(BLACK):
        return -100000 # vitória do humano
    if depth == 0 or board.is_full():
        return heuristic_fn(board) # usa heurística recebida como parâmetro
    moves = get_candidates(board) # gera jogadas relevantes
    if maximizing == True: # turno da IA (MAX)
        best = -math.inf # menor valor possível inicialmente
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy() # copia tabuleiro
            copy.place(r, c, WHITE) # simula jogada da IA
            val = minimax_pro(copy, depth - 1, alpha, beta, False, deadline, heuristic_fn)
            if val > best:
                best = val # IA escolhe maior valor
            if val > alpha:
                alpha = val # atualiza melhor valor encontrado pela IA
            if beta <= alpha:
                break # poda alfa-beta: ramo inútil é cortado
        return best
    else: # turno do humano (MIN)
        best = math.inf # maior valor possível inicialmente
        for move in moves:
            r = move[0]
            c = move[1]
            copy = board.copy() # copia tabuleiro
            copy.place(r, c, BLACK) # simula jogada do humano
            val = minimax_pro(copy, depth - 1, alpha, beta, True, deadline, heuristic_fn)
            if val < best:
                best = val # humano escolhe menor valor
            if val < beta:
                beta = val # atualiza melhor valor encontrado pelo humano
            if beta <= alpha:
                break # poda alfa-beta
        return best


# Iterative Deepening — vai aumentando a profundidade enquanto houver tempo, usa o melhor resultado completo
def best_move_pro(board, heuristic_fn):
    start = time.time() # salva horário inicial
    deadline = start + TIME_LIMIT # calcula horário limite
    best_move = None # melhor jogada final
    best_val = -math.inf # melhor valor final
    depth_reached = 0 # profundidade máxima concluída
    depth = 1 # começa busca em profundidade 1
    while depth < 20: # continua aprofundando enquanto houver tempo
        move_this_depth = None # melhor jogada da profundidade atual
        val_this_depth = -math.inf # melhor valor da profundidade atual
        failed = False # controla timeout
        try:
            for move in get_candidates(board): # testa cada jogada possível
                r = move[0]
                c = move[1]
                copy = board.copy() # cria cópia do tabuleiro
                copy.place(r, c, WHITE) # simula jogada da IA
                val = minimax_pro(copy, depth - 1, -math.inf, math.inf, False, deadline, heuristic_fn ) # executa minimax profissional
                if val > val_this_depth:
                    val_this_depth = val # guarda melhor valor encontrado
                    move_this_depth = move # guarda melhor jogada encontrada
            best_move = move_this_depth # salva melhor jogada COMPLETA da profundidade
            best_val = val_this_depth # salva melhor valor
            depth_reached = depth # salva profundidade concluída
        except TimeOut:
            failed = True # timeout interrompe busca
        if failed == True:
            break # sai do loop se tempo acabar
        depth = depth + 1 # aumenta profundidade da busca
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
                # esse aqui foi um teste bem interessante!
                #heuristic_fn = heuristic_intermediate
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