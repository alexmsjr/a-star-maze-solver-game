import AuxFunctions as AuxFunc
from collections import deque
from NPnode import NPnode


class NPsearch(object):
    ### NEIGHBORS
    def neighbors(self, state, nx, ny, maze):
        q = []
        # Current position: x = row, y = column
        curr_x, curr_y = state[0], state[1]

        # Define directions: (delta_x, delta_y)
        # (0, 1) = Right, (1, 0) = Down, (0, -1) = Left, (-1, 0) = Up
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            next_x = curr_x + dx
            next_y = curr_y + dy

            # 1. Bounds check (Ensures we stay inside the grid)
            if 0 <= next_x < nx and 0 <= next_y < ny:

                # 2. Path check (Only moves through floor (0) or exit (3))
                if maze[next_x][next_y] in [0, 3]:

                    # Add to successors list
                    q.append([next_x, next_y])

                    # 3. Visualization check:
                    # ONLY change to 4 if it's floor. This keeps the exit (3) visible.
                    if maze[next_x][next_y] == 0:
                        maze[next_x][next_y] = 4

        # Returning reversed list to maintain search order consistency
        return q[::-1]

    ### Draw Path
    def show_path(self, node):
        path = []
        while node is not None:
            path.append(node.state)
            node = node.parent
        path.reverse()
        return path


    ### Find nodes inside of queue
    def find_node(self, value, queue):
        for node in reversed(queue):
            if node.state == value:
                return node

    ### Draw path found in search tree - bidirection
    def show_path_b(self, join, queue_1, queue_2):

        join_1 = self.findNode(join, queue_1)  # Source node side
        join_2 = self.findNode(join, queue_2)  # Target node side

        path_1 = self.showPath(join_1)
        path_2 = self.showPath(join_2)
        path_2 = list(reversed(path_2[::-1]))  # Path_2 inversion
        return path_1 + path_2

    # amplitude
    def breadth_first_search(self, start, end, nx, ny, maze, update_ui):
        # Check if start and goal are the same
        if start == end:
            return [start]

        # Create tuples
        start_t = tuple(start)
        end_t = tuple(end)

        # Search tree queue
        queue = deque()

        # Initialize search tree with start_t as root node
        root = NPnode(None, start_t, 0, None, None)
        queue.append(root)

        # mark start node as visited
        visited = {}  # mapping
        visited[start_t] = 0

        # Run the search
        while queue:
            # Pop the next node from the queue
            current = queue.popleft()

            # Search for neighbors
            neigh = self.neighbors(current.state, nx, ny, maze)

            if update_ui:
                update_ui()

            for new in neigh:
                new_t = tuple(new)
                flag = True
                if new_t in visited:
                    if visited[new_t] <= current.depth + 1:
                        flag = False
                if flag:
                    neigh = NPnode(current, new, current.depth + 1, None, None)
                    queue.append(neigh)
                    visited[new_t] = current.depth + 1

                    # Check if new_t is the goal
                    if new_t == end_t:
                        return self.show_path(neigh)
        return None

    # profundidade
    def depth_first_search(self, start, end, nx, ny, maze, update_ui):
        # Check if start and goal are the same
        if start == end:
            return [start]

        # Create tuples
        start_t = tuple(start)
        end_t = tuple(end)

        # Search tree queue
        stack = deque()

        # Initialize search tree with start_t as root node
        root = NPnode(None, start_t, 0, None, None)
        stack.append(root)

        # mark start node as visited
        visited = {}  # mapping
        visited[start_t] = 0

        # Run the search
        while stack:
            # Pop the next node from the queue
            current = stack.pop()

            # Search for neighbors
            neighs = self.neighbors(current.state, nx, ny, maze)

            if update_ui:
                update_ui()

            for new in neighs:
                new_t = tuple(new)
                flag = True
                if new_t in visited:
                    if visited[new_t] <= current.depth + 1:
                        flag = False
                if flag:
                    neigh = NPnode(current, new, current.depth + 1, None, None)
                    stack.append(neigh)
                    visited[new_t] = current.depth + 1

                    # Check if new_t is the goal
                    if new_t == end_t:
                        return self.show_path(neigh)
        return None

    # Profundidade Limitada
    def depth_limited_search(self, start, end, nx, ny, maze, lim, update_ui):
        # Check if start and goal are the same
        if start == end:
            return [start]

        # Create tuples
        t_start = tuple(start)
        t_end = tuple(end)

        # Search tree queue
        stack = deque()

        # Initialize search tree with start_t as root node
        root = NPnode(None, t_start, 0, None, None)
        stack.append(root)

        # mark start node as visited
        visited = {}
        visited[t_start] = 0

        while stack:
            # Pop the next node from the queue
            current = stack.pop()

            if current.depth < lim:
                # Search for neighbors
                neighs = self.neighbors(current.state, nx, ny, maze)

                if update_ui:
                    update_ui()

                for new in neighs:
                    new_t = tuple(new)
                    flag = True
                    if new_t in visited:
                        if visited[new_t] <= current.state + 1:
                            flag = False
                    if flag:
                        neigh = NPnode(current, new, current.depth + 1, None, None)
                        stack.append(neigh)
                        visited[new_t] = current.depth + 1

                        # Check if new_t is the goal - multiobjetve
                        if new_t == t_end:
                            return self.show_path(neigh)
        return None


def aprof_iterativo_grid(self, inicio, fim, nx, ny, mapa, lim_max):
    # Finaliza se início for igual a objetivo
    if inicio == fim:
        return [inicio]

    for lim in range(1, lim_max):
        # GRID: transforma em tupla
        t_inicio = tuple(inicio)
        t_fim = tuple(fim)

        # Lista para árvore de busca - FILA
        pilha = deque()

        # Inclui início como nó raíz da árvore de busca
        raiz = Node(None, t_inicio, 0, None, None)
        pilha.append(raiz)

        # Marca início como visitado
        visitado = {}
        visitado[t_inicio] = 0

        while pilha:
            # Remove o primeiro da FILA
            atual = pilha.pop()

            if atual.v1 < lim:
                # Gera sucessores a partir do grid
                filhos = self.sucessores_grid(atual.estado, nx, ny, mapa)

                for novo in filhos:
                    t_novo = tuple(novo)
                    flag = True
                    if t_novo in visitado:
                        if visitado[t_novo] <= atual.v1 + 1:
                            flag = False
                    if flag:
                        filho = Node(atual, novo, atual.v1 + 1, None, None)
                        pilha.append(filho)
                        visitado[t_novo] = atual.v1 + 1

                        # Verifica se encontrou o objetivo
                        if t_novo == t_fim:
                            return self.exibirCaminho(filho)
        visitado.clear()
        pilha.clear()
    return None
