import pygame
import sys
import os
import copy
import AuxFunctions
from NPsearch import NPsearch

# Inicializações
pygame.init()
pygame.mixer.init()
np_searcher = NPsearch()

### DISPLAY SETUP
display_l = 1200
display_h = 800
display = pygame.display.set_mode((display_l, display_h))
pygame.display.set_caption("Laboratório de Inteligência Artificial - oLabirinto")

### FONTS
title_font = pygame.font.SysFont("terminal", 36, bold=True)
button_font = pygame.font.SysFont("terminal", 24)
default_font = pygame.font.SysFont("terminal", 20)
small_font = pygame.font.SysFont("terminal", 16)

### COLORS
back_gray = (30, 32, 35)
sidebar_color = (40, 42, 45)
dark_gray = (50, 52, 55)
gray = (90, 90, 90)
text_gray = (150, 150, 150)
white = (255, 255, 255)
yellow = (226, 183, 20)
green = (46, 135, 10)
red = (255, 0, 0)
blue_explored = (50, 100, 200)


### SISTEMA DE ÁUDIO
def load_sound(path):
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None


SFX = {
    'click': load_sound(r'sounds\click_sfx.ogg'),
    'success': load_sound(r'sounds\success_sfx.ogg'),
    'error': load_sound(r'sounds\error_sfx.ogg'),
}


def play_sfx(sound_name):
    if SFX.get(sound_name):
        SFX[sound_name].play()


### SISTEMA DE ASSETS
ASSETS = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}


def get_color(cell_value):
    colors = {0: white, 1: gray, 2: green, 3: red, 4: blue_explored, 5: yellow}
    return colors.get(cell_value, white)


# --- CLASSE CAIXA DE TEXTO ATUALIZADA (Com Cursor | ) ---
class CaixaTexto:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = dark_gray
        self.text = text
        self.txt_surface = default_font.render(text, True, white)
        self.active = False
        self.cursor_visible = True
        self.last_cursor_blink = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
                self.color = gray if self.active else dark_gray

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isnumeric() and len(self.text) < 3:
                self.text += event.unicode
            self.txt_surface = default_font.render(self.text, True, white)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)
        if self.active:
            pygame.draw.rect(screen, yellow, self.rect, 2, border_radius=6)

            # Lógica do Cursor Piscante
            if pygame.time.get_ticks() - self.last_cursor_blink > 500:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_blink = pygame.time.get_ticks()

            if self.cursor_visible:
                # Desenha a barra após o texto
                text_w = self.txt_surface.get_width()
                start_x = self.rect.centerx + (text_w // 2) + 2
                pygame.draw.line(screen, white, (start_x, self.rect.y + 5), (start_x, self.rect.bottom - 5), 2)

        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)


# Configurando os Inputs da Sidebar
inputs = {
    'tamanho': CaixaTexto(200, 70, 60, 30, '31'),
    'start_l': CaixaTexto(200, 110, 45, 30, '0'),
    'start_c': CaixaTexto(255, 110, 45, 30, '0'),
    'end_l': CaixaTexto(200, 150, 45, 30, '30'),
    'end_c': CaixaTexto(255, 150, 45, 30, '30'),
    'limite': CaixaTexto(200, 190, 60, 30, '20')
}

### ESTADO GLOBAL DO LABORATÓRIO
lines_cols = int(inputs['tamanho'].text)
maze_start = (int(inputs['start_l'].text), int(inputs['start_c'].text))
maze_end = (int(inputs['end_l'].text), int(inputs['end_c'].text))

maze_base = AuxFunctions.profundidade_grid_topeira(maze_start, maze_end, lines_cols, lines_cols)
maze_display = copy.deepcopy(maze_base)

### CONFIGURAÇÃO DOS ALGORITMOS
ALGORITMOS = [
    {'id': 'bfs', 'name': 'Amplitude (BFS)'},
    {'id': 'dfs', 'name': 'Profundidade (DFS)'},
    {'id': 'dls', 'name': 'Prof. Limitada (DLS)'},
    {'id': 'ids', 'name': 'Prof. Iterativa (IDS)'},
    {'id': 'bi', 'name': 'Bidirecional'},
    {'id': 'ucs', 'name': 'Custo Uniforme (UCS)'},
    {'id': 'greedy', 'name': 'Greedy (Gulosa)'},
    {'id': 'astar', 'name': 'A-Star (A*)'},
    {'id': 'ida', 'name': 'IDA*'}
]

results = {}
sidebar_w = 400
margin = 20
btn_gen_maze = pygame.Rect(margin, 240, 360, 40)

start_y_algos = 330
btn_height = 36
btn_spacing = 8

for index, algo in enumerate(ALGORITMOS):
    y_pos = start_y_algos + (index * (btn_height + btn_spacing))
    algo['rect'] = pygame.Rect(margin, y_pos, 210, btn_height)
    results[algo['id']] = {'cost': '--', 'nodes': '--'}


############################################## MATEMÁTICA DO GRID #################################################
def get_grid_offsets():
    """Calcula tamanho e posição exata do labirinto na tela"""
    available_w = (display_l - sidebar_w) - 40
    available_h = display_h - 40

    cell_size = min(available_w // lines_cols, available_h // lines_cols)
    maze_w = cell_size * lines_cols
    maze_h = cell_size * lines_cols

    offset_x = sidebar_w + ((display_l - sidebar_w) - maze_w) // 2
    offset_y = (display_h - maze_h) // 2

    return offset_x, offset_y, cell_size


############################################## DESENHO #################################################
def draw_text(surface, text, font, color, rect, align='center'):
    text_surf = font.render(text, True, color)
    if align == 'center':
        text_rect = text_surf.get_rect(center=rect.center)
    elif align == 'left':
        text_rect = text_surf.get_rect(midleft=(rect.left + 10, rect.centery))
    surface.blit(text_surf, text_rect)


def draw_sidebar(mouse_pos):
    pygame.draw.rect(display, sidebar_color, (0, 0, sidebar_w, display_h))
    display.blit(title_font.render("Lab de IA - oLabirinto", True, yellow), (margin, margin))

    display.blit(default_font.render("Tamanho (N x N):", True, text_gray), (margin, 75))
    inputs['tamanho'].draw(display)

    display.blit(default_font.render("Início (Lin, Col):", True, text_gray), (margin, 115))
    inputs['start_l'].draw(display)
    inputs['start_c'].draw(display)

    display.blit(default_font.render("Saída (Lin, Col):", True, text_gray), (margin, 155))
    inputs['end_l'].draw(display)
    inputs['end_c'].draw(display)

    display.blit(default_font.render("Lim. Profundidade:", True, yellow), (margin, 195))
    inputs['limite'].draw(display)

    color_gen = gray if btn_gen_maze.collidepoint(mouse_pos) else dark_gray
    pygame.draw.rect(display, color_gen, btn_gen_maze, border_radius=8)
    draw_text(display, "GERAR NOVO LABIRINTO", default_font, white, btn_gen_maze)

    display.blit(small_font.render("Algoritmos", True, text_gray), (margin, 305))
    display.blit(small_font.render("Custo", True, text_gray), (margin + 230, 305))
    display.blit(small_font.render("Nós", True, text_gray), (margin + 310, 305))

    for algo in ALGORITMOS:
        btn = algo['rect']
        res = results[algo['id']]

        color_btn = gray if btn.collidepoint(mouse_pos) else dark_gray
        pygame.draw.rect(display, color_btn, btn, border_radius=6)
        draw_text(display, algo['name'], button_font, white, btn, align='left')

        box_cost = pygame.Rect(margin + 220, btn.y, 60, btn_height)
        box_nodes = pygame.Rect(margin + 290, btn.y, 70, btn_height)

        pygame.draw.rect(display, dark_gray, box_cost, border_radius=6)
        pygame.draw.rect(display, dark_gray, box_nodes, border_radius=6)

        c_color = yellow if res['cost'] != '--' else text_gray
        draw_text(display, str(res['cost']), default_font, c_color, box_cost, align='center')
        draw_text(display, str(res['nodes']), default_font, c_color, box_nodes, align='center')


# --- FUNÇÃO DE DESENHO CORRIGIDA (Preenchimento Total) ---
def draw_maze():
    pygame.draw.rect(display, back_gray, (sidebar_w, 0, display_l - sidebar_w, display_h))

    # Área útil total (600x600 ou o que sobrar da tela)
    area_w = (display_l - sidebar_w) - 40
    area_h = display_h - 40

    offset_x = sidebar_w + 20
    offset_y = 20

    for r in range(lines_cols):
        for c in range(lines_cols):
            cell = maze_display[r][c]

            # CÁLCULO DE PROPORÇÃO (Evita o encolhimento)
            # Calculamos o X inicial e o X final de cada célula na área total
            x1 = offset_x + (c * area_w) // lines_cols
            y1 = offset_y + (r * area_h) // lines_cols
            x2 = offset_x + ((c + 1) * area_w) // lines_cols
            y2 = offset_y + ((r + 1) * area_h) // lines_cols

            cell_rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)

            # Desenha com Sprites ou Cores
            if ASSETS[cell]:
                display.blit(pygame.transform.scale(ASSETS[cell], (x2 - x1, y2 - y1)), (x1, y1))
            else:
                pygame.draw.rect(display, get_color(cell), cell_rect)


############################################## POPUP #################################################
def show_popup(message):
    overlay = pygame.Surface((display_l, display_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    display.blit(overlay, (0, 0))

    popup_w, popup_h = 400, 200
    popup_rect = pygame.Rect((display_l // 2 - popup_w // 2), (display_h // 2 - popup_h // 2), popup_w, popup_h)

    pygame.draw.rect(display, sidebar_color, popup_rect, border_radius=15)
    pygame.draw.rect(display, white, popup_rect, width=2, border_radius=15)

    draw_text(display, message, default_font, yellow, pygame.Rect(popup_rect.x, popup_rect.y, popup_w, popup_h - 40))
    draw_text(display, "Clique em qualquer lugar para fechar", small_font, text_gray,
              pygame.Rect(popup_rect.x, popup_rect.bottom - 40, popup_w, 40))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                waiting = False


############################################## MAIN LOOP #################################################
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        for key in inputs:
            inputs[key].handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:

            # --- LÓGICA DE CLIQUE NO LABIRINTO (ESCOLHER ENTRADA/SAÍDA) ---
            if mouse_pos[0] > sidebar_w:
                offset_x, offset_y, cell_size = get_grid_offsets()

                # Traduz pixel para Linha e Coluna
                col = (mouse_pos[0] - offset_x) // cell_size
                row = (mouse_pos[1] - offset_y) // cell_size

                # Verifica se clicou DENTRO dos blocos válidos
                if 0 <= row < lines_cols and 0 <= col < lines_cols:

                    if event.button == 1:  # BOTÃO ESQUERDO = MOVER INÍCIO
                        maze_base[maze_start[0]][maze_start[1]] = 0  # Limpa anterior
                        maze_start = (row, col)
                        maze_base[row][col] = 2  # Seta o novo

                        # Atualiza UI
                        inputs['start_l'].text = str(row)
                        inputs['start_c'].text = str(col)
                        inputs['start_l'].txt_surface = default_font.render(str(row), True, white)
                        inputs['start_c'].txt_surface = default_font.render(str(col), True, white)

                        maze_display = copy.deepcopy(maze_base)
                        play_sfx('click')

                    elif event.button == 3:  # BOTÃO DIREITO = MOVER FIM
                        maze_base[maze_end[0]][maze_end[1]] = 0  # Limpa anterior
                        maze_end = (row, col)
                        maze_base[row][col] = 3  # Seta o novo

                        # Atualiza UI
                        inputs['end_l'].text = str(row)
                        inputs['end_c'].text = str(col)
                        inputs['end_l'].txt_surface = default_font.render(str(row), True, white)
                        inputs['end_c'].txt_surface = default_font.render(str(col), True, white)

                        maze_display = copy.deepcopy(maze_base)
                        play_sfx('click')

            # --- LÓGICA DE CLIQUE NOS BOTÕES (Painel Esquerdo) ---
            if event.button == 1 and mouse_pos[0] <= sidebar_w:

                if btn_gen_maze.collidepoint(mouse_pos):
                    play_sfx('click')
                    try:
                        new_size = int(inputs['tamanho'].text)
                        new_st = (int(inputs['start_l'].text), int(inputs['start_c'].text))
                        new_end = (int(inputs['end_l'].text), int(inputs['end_c'].text))

                        # Travas e Efeito Ímã (Paridade)
                        if new_size < 5: raise ValueError("Tamanho mínimo é 5")
                        if new_size % 2 == 0:
                            new_size += 1
                            inputs['tamanho'].text = str(new_size)
                            inputs['tamanho'].txt_surface = default_font.render(str(new_size), True, white)

                        if max(new_st[0], new_st[1], new_end[0], new_end[1]) >= new_size:
                            raise ValueError("Coordenadas fora dos limites do mapa")

                        end_l, end_c = new_end[0], new_end[1]
                        if new_st[0] % 2 != end_l % 2:
                            end_l = end_l - 1 if end_l > 0 else end_l + 1
                        if new_st[1] % 2 != end_c % 2:
                            end_c = end_c - 1 if end_c > 0 else end_c + 1
                        new_end = (end_l, end_c)

                        inputs['end_l'].text, inputs['end_c'].text = str(end_l), str(end_c)
                        inputs['end_l'].txt_surface = default_font.render(str(end_l), True, white)
                        inputs['end_c'].txt_surface = default_font.render(str(end_c), True, white)

                        lines_cols = new_size
                        maze_start = new_st
                        maze_end = new_end

                        maze_base = AuxFunctions.profundidade_grid_topeira(maze_start, maze_end, lines_cols, lines_cols)
                        maze_display = copy.deepcopy(maze_base)

                        for key in results: results[key] = {'cost': '--', 'nodes': '--'}

                    except ValueError as e:
                        play_sfx('error')
                        show_popup(f"Erro: {e}")

                # CHAMA OS ALGORITMOS
                for algo in ALGORITMOS:
                    if algo['rect'].collidepoint(mouse_pos):
                        play_sfx('click')
                        algo_id = algo['id']

                        maze_display = copy.deepcopy(maze_base)


                        def animar_busca():
                            draw_sidebar(mouse_pos)
                            draw_maze()
                            pygame.display.flip()
                            #pygame.time.delay(1)
                            pygame.event.pump()


                        try:
                            path = None

                            if algo_id == 'bfs':
                                path = np_searcher.breadth_first_search(maze_start, maze_end, lines_cols, lines_cols,
                                                                        maze_display, animar_busca)

                            elif algo_id == 'dfs':
                                path = np_searcher.depth_first_search(maze_start, maze_end, lines_cols, lines_cols,
                                                                      maze_display, animar_busca)

                            elif algo_id == 'dls':
                                limite_dls = int(inputs['limite'].text)
                                print(f"Executando DLS com limite: {limite_dls}")
                                # path = np_searcher.depth_limited_search(maze_start, maze_end, lines_cols, lines_cols, maze_display, animar_busca, limite_dls)

                            else:
                                print(f"{algo['name']} aguardando implementação.")

                            if path:
                                path.pop(0)
                                for step in path:
                                    if maze_display[step[0]][step[1]] not in [2, 3]:
                                        maze_display[step[0]][step[1]] = 5

                                results[algo_id]['cost'] = len(path)
                                results[algo_id]['nodes'] = sum(row.count(4) for row in maze_display) + len(path)
                                play_sfx('success')
                            elif algo_id in ['bfs', 'dfs']:
                                play_sfx('error')
                                show_popup(f'[{algo["name"]}] Nenhum caminho encontrado!')

                        except Exception as e:
                            print(f"Erro no algoritmo {algo_id}: {e}")
                            show_popup('Erro ao buscar caminho.')

    # RENDERIZAÇÃO A CADA FRAME
    display.fill(back_gray)
    draw_maze()
    draw_sidebar(mouse_pos)
    pygame.display.flip()

pygame.quit()
sys.exit()