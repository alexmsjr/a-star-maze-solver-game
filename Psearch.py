from collections import deque
from Pnode import Pnode

TERRAIN_COSTS = {
    0:1, # Asfalto
    1:1, # Inicio
    2:1, # Fim
    6:10, # Terra
}

class Psearch(object):

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
                if maze[next_x][next_y] in [0, 2, 3, 4, 5, 6]:
                    cost = TERRAIN_COSTS.get(maze[next_x][next_y], 1)
                    # Add to successors list
                    q.append([[next_x, next_y], cost])
        return q[::-1]

    def insert_ordered(self,queue, node):
        for i, n in enumerate(queue):
            if node.v1 < n.v1:
                queue.insert(i, node)
                break
        else:
            queue.append(node)


    ### Draw Path
    def show_path(self, node):
        path = []
        while node is not None:
            path.append(node.state)
            node = node.parent
        path.reverse()
        return path

    def find_node(self, valor, queue):
        for no in reversed(queue):
            if no.state == valor:
                return no

    def heuristic(self, start, end):
        #print(start, end)
        #print(start)
        x = abs(start[0] - end[0])
        y = abs(start[1] - end[1])
        return x + y

    def uniform_cost(self, start, end, nx, ny, maze, update_ui):
        # Origem igual a destino
        if start == end:
            return [start], 0, 0
        total_nodes = 0

        # Fila de prioridade baseada em deque + inserção ordenada
        queue = deque()
        t_start = tuple(start)
        root = Pnode(None, t_start, 0, None, None, 0)
        queue.append(root)

        # Controle de nós visitados
        visited = {tuple(start): root}

        # loop de busca
        while queue:
            # remove o primeiro nó
            current = queue.popleft()
            total_nodes += 1
            current_value = current.v2

            # Chegou ao objetivo
            if current.state == end:
                return self.show_path(current), current.v2, total_nodes

            # Gera sucessores - grid
            neighbors = self.neighbors(current.state, nx, ny, maze)
            # 3. Visualization check:
            # ONLY change to 4 if it's floor. This keeps the exit (3) visible.
            if maze[current.state[0]][current.state[1]] in [0,6]:
                maze[current.state[0]][current.state[1]] = 4

            if update_ui:
                update_ui()

            for new in neighbors:
                # custo acumulado até o sucessor
                v2 = current_value + new[1]
                v1 = v2

                # Não visited ou custo melhor
                t_new = tuple(new[0])
                if (t_new not in visited) or (v2 < visited[t_new].v2):
                    neigh = Pnode(current, t_new, v1, None, None, v2)
                    visited[t_new] = neigh
                    self.insert_ordered(queue,  neigh)
        return None

    def greedy(self, start, end, nx, ny, maze, update_ui):  # grid
        # Origem igual a destino
        if start == end:
            return [start], 0, 0
        total_nodes = 0

        # Fila de prioridade baseada em deque + inserção ordenada
        queue = deque()
        t_start = tuple(start)
        root = Pnode(None, t_start, 0, None, None, 0)
        queue.append(root)

        # Controle de nós visitados
        visited = {tuple(start): root}

        # loop de busca
        while queue:
            # remove o primeiro nó
            current = queue.popleft()
            total_nodes += 1
            current_value = current.v2

            # Chegou ao objetivo
            if current.state == end:
                return self.show_path(current), current.v2,  total_nodes

            # Gera sucessores
            neighbors = self.neighbors(current.state, nx, ny, maze)

            # 3. Visualization check:
            # ONLY change to 4 if it's floor. This keeps the exit (3) visible.
            if maze[current.state[0]][current.state[1]] == 0:
                maze[current.state[0]][current.state[1]] = 4

            if update_ui:
                update_ui()

            for new in neighbors:
                # custo acumulado até o sucessor
                v2 = current_value + new[1]
                v1 = self.heuristic(new[0], end)

                # Não visited ou custo melhor
                t_new = tuple(new[0])
                if (t_new not in visited) or (v2 < visited[t_new].v2):
                    neigh = Pnode(current, t_new, v1, None, None, v2)
                    visited[t_new] = neigh
                    self.insert_ordered(queue, neigh)
        return None

    def a_star(self, start, end, nx, ny, maze, update_ui):
        # Origem igual a destino
        if start == end:
            return [start], 0, 0
        total_nodes = 0

        # Fila de prioridade baseada em deque + inserção ordenada
        queue = deque()
        t_start = tuple(start)
        root = Pnode(None, t_start, 0, None, None, 0)
        queue.append(root)

        # Controle de nós visitados
        visited = {tuple(start): root}

        # loop de busca
        while queue:
            # remove o primeiro nó
            current = queue.popleft()
            total_nodes += 1
            current_value = current.v2

            # Chegou ao objetivo
            if current.state == end:
                return self.show_path(current), current.v2, total_nodes

            # Gera sucessores
            neighbors = self.neighbors(current.state, nx, ny, maze)

            # 3. Visualization check:
            # ONLY change to 4 if it's floor. This keeps the exit (3) visible.
            if maze[current.state[0]][current.state[1]] == 0:
                maze[current.state[0]][current.state[1]] = 4

            if update_ui:
                update_ui()

            for new in neighbors:
                # custo acumulado até o sucessor
                v2 = current_value + new[1]
                v1 = v2 + self.heuristic(new[0], end)

                # Não visited ou custo melhor
                t_new = tuple(new[0])
                if (t_new not in visited) or (v2 < visited[t_new].v2):
                    neigh = Pnode(current, t_new, v1, None, None, v2)
                    visited[t_new] = neigh
                    self.insert_ordered(queue, neigh)
        return None

    def ida_star(self, start, end, nx, ny, maze, update_ui):
        # Origem igual a destino
        if start == end:
            return [start], 0, 0
        lim = self.heuristic(start, end)
        total_nodes = 0

        while True:

            for r in range(nx):
                for c in range(ny):
                    if maze[r][c] == 4:
                        maze[r][c] = 0

            # Fila de prioridade baseada em deque + inserção ordenada
            queue = deque()
            t_start = tuple(start)
            root = Pnode(None, t_start, 0, None, None, 0)
            queue.append(root)

            # Controle de nós visitados
            visited = {tuple(start): root}

            # loop de busca
            new_lim = []
            while queue:
                # remove o primeiro nó
                current = queue.popleft()
                current_value = current.v2

                total_nodes += 1

                # Chegou ao objetivo
                if current.state == end:
                    return self.show_path(current), current.v2, total_nodes

                # Gera sucessores
                neighbors = self.neighbors(current.state, nx, ny, maze)

                # 3. Visualization check:
                # ONLY change to 4 if it's floor. This keeps the exit (3) visible.
                if maze[current.state[0]][current.state[1]] == 0:
                    maze[current.state[0]][current.state[1]] = 4

                if update_ui:
                    update_ui()

                for new in neighbors:
                    # custo acumulado até o sucessor
                    v2 = current_value + new[1]
                    v1 = v2 + self.heuristic(new[0], end)

                    if v1 <= lim:
                        # Não visited ou custo melhor
                        t_new = tuple(new[0])
                        if (t_new not in visited) or (v2 < visited[t_new].v2):
                            neigh = Pnode(current, t_new, v1, None, None, v2)
                            visited[t_new] = neigh
                            self.insert_ordered(queue, neigh)
                    else:
                        new_lim.append(v1)
            lim = (int)(sum(new_lim) / (len(new_lim)))
            queue.clear()
            visited.clear()
            new_lim.clear()
        return None