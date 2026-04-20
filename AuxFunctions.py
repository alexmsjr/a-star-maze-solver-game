import numpy as np
import random as rd
from collections import deque
from NPnode import NPnode

### RANDOM MAZE GENERATOR
#def gen_randon_maze(nx, ny, maze_in, maze_out, walls):
def gen_randon_maze(nx, ny, walls):
    maze = np.zeros((nx, ny), int)

    maze_start = [0][0]
    maze_end = [0][0]
    while maze_end == maze_start: # garante que a entrada e a saida sempre sejam diferentes
        maze_start = (rd.randrange(0,nx-1), rd.randrange(0,ny-1)) # defining maze entrance loc
        maze_end = (rd.randrange(0,nx-1), rd.randrange(0,ny-1)) # defining maze exit loc


    maze[maze_start[0]][[maze_start[1]]] = 2 # defining maze entrance
    maze[maze_end[0]][maze_end[1]] = 3 # defining maze exit

    counter = 0
    while counter < walls:
        x = rd.randrange(0, nx - 1)
        y = rd.randrange(0, ny - 1)

        if maze[x][y] == 0:
            maze[x][y] = 1
            counter += 1
    return maze, maze_start, maze_end

def create_maze(size):

        maze = []
        for i in range(size):
            line = []
            for j in range(size):
                line.append(1)
            maze.append(line)
        return maze


def print_maze(maze):
    for row in maze:
        print(row)


def sucessores_grid_topeira(st, nx, ny, mapa, parede):
    f = []
    x, y = st[0], st[1]

    # DIREITA
    if y + 2 < ny:
        if mapa[x][y + 2] == parede:
            suc = []
            suc.append(x)
            suc.append(y + 2)
            f.append(suc)
    # ESQUERDA
    if y - 2 >= 0:
        if mapa[x][y - 2] == parede:
            suc = []
            suc.append(x)
            suc.append(y - 2)
            f.append(suc)
    # ABAIXO
    if x + 2 < nx:
        if mapa[x + 2][y] == parede:
            suc = []
            suc.append(x + 2)
            suc.append(y)
            f.append(suc)
    # ACIMA
    if x - 2 >= 0:
        if mapa[x - 2][y] == parede:
            suc = []
            suc.append(x - 2)
            suc.append(y)
            f.append(suc)
    rd.shuffle(f)
    return f


def profundidade_grid_topeira(inicio, fim, nx, ny):
    caminhoPrincipal = []

    mapa = create_maze(nx)

    # Finaliza se início for igual a objetivo
    if inicio == fim:
        return [inicio]

    # GRID: transforma em tupla
    t_inicio = tuple(inicio)
    t_fim = tuple(fim)

    # ZERA O INICIO
    mapa[t_inicio[0]][t_inicio[1]] = 0

    # Lista para árvore de busca - PILHA
    pilha = deque()

    # Inclui início como nó raíz da árvore de busca
    raiz = NPnode(None, t_inicio, 0, None, None)
    pilha.append(raiz)

    while pilha:
        # Pega o último da PILHA
        atual = pilha[-1]

        # Gera sucessores a partir do grid
        filhos = sucessores_grid_topeira(atual.state, nx, ny, mapa, 1)  # grid

        if filhos:
            novo = filhos[0]  # Pega o primeiro filho aleatorio
            t_novo = tuple(novo)

            # ZERAR VALORES DO MAPA
            mapa[novo[0]][novo[1]] = 0  # FILHO DUAS CASA DE DISTANCIA
            xIntermediario = int((atual.state[0] + novo[0]) / 2)
            yIntermediario = int((atual.state[1] + novo[1]) / 2)
            mapa[xIntermediario][yIntermediario] = 0  # FILHO UMA CASA DE DISTANCIA

            novo_no = NPnode(atual, t_novo, atual.depth + 1, None, None)
            pilha.append(novo_no)

            if (t_novo == t_fim):  # Se encontrar o fim, retorna e continua escavando
                caminhoPrincipal = pilha.copy()
                pilha.pop()

        else:
            pilha.pop()  # Se nao encontar sucessores, volta no caminho e tenta escavar de novo

    # CRIAR MAIS CAMINHOS
    qtdCaminhos = 5  # Quantidade estimada de caminhos
    indexCaminho = int(
        len(caminhoPrincipal) / qtdCaminhos - 2)  # Cria um index para escolher pontos do caminho principal de forma espaçada
    indexAtual = indexCaminho  # Ex: Caminho principal com 30 pontos e 3 qtdCaminhos--> 30/3-2 = 8 --> Pontos escolidos (8,16,24)

    for i in range(qtdCaminhos):  # Percorre todos os pontos escolidos
        atual = caminhoPrincipal[indexAtual]
        filhos = sucessores_grid_topeira(atual.state, nx, ny, mapa,
                                         0)  # Sucessores sao caminhos que valem 0 a dois blocos de ditancia do atual

        # Dos sucessores, se existir um parede entre eles, ela é removida
        for novo in filhos:
            xIntermediario = int((atual.state[0] + novo[0]) / 2)
            yIntermediario = int((atual.state[1] + novo[1]) / 2)
            if mapa[xIntermediario][yIntermediario] == 1:
                mapa[xIntermediario][yIntermediario] = 0
                break

        indexAtual += indexCaminho

    mapa[t_inicio[0]][t_inicio[1]] = 2
    mapa[t_fim[0]][t_fim[1]] = 3

    return mapa




