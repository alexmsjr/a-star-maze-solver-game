import pygame
import sys
import os
import copy
import AuxFunctions
from NPsearch import NPsearch

pygame.init()
pygame.mixer.init()
np_searcher = NPsearch()

### DISPLAY SETUP
display_l = 1400
display_h = 900
display = pygame.display.set_mode((display_l, display_h))
pygame.display.set_caption("Lab de IA - oLabirinto")

### FONTS
title_font = pygame.font.SysFont("terminal", 32, bold=True)
button_font = pygame.font.SysFont("terminal", 18, bold=True)
default_font = pygame.font.SysFont("terminal", 18)
small_font = pygame.font.SysFont("terminal", 14)

### COLORS
bg_main = (30, 30, 30)
bg_panel = (20, 20, 20)
white = (250, 250, 250)
white_dark = (180, 180, 180)
red_btn = (235, 60, 60)
red_btn_dark = (160, 30, 30)
green_box = (150, 200, 180)
green_box_dark = (110, 160, 140)
text_dark = (20, 20, 20)
text_gray = (80, 80, 80)
yellow = (226, 183, 20)
dark_gray = (50, 52, 55)
gray = (90, 90, 90)

### CORES DO LABIRINTO
color_maze_wall = (90, 90, 90)
color_maze_path = white
color_maze_start = (46, 135, 10)
color_maze_end = (255, 0, 0)
color_maze_explored = (50, 100, 200)
color_maze_path_found = yellow


### --- SISTEMA DE ARQUIVOS ---
def load_sound(path): return pygame.mixer.Sound(path) if os.path.exists(path) else None


SFX = {'click': load_sound(r'sounds\click_sfx.ogg'), 'success': load_sound(r'sounds\success_sfx.ogg'),
       'error': load_sound(r'sounds\error_sfx.ogg')}


def play_sfx(sound_name):
    if SFX.get(sound_name): SFX[sound_name].play()


LOGO_PATH = ('logo.png')
LOGO_MAX_SIZE = (250, 50)


def load_logo(path, max_size):
    if os.path.exists(path):
        try:
            return pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), max_size)
        except:
            return None
    return None


logo_img = load_logo(LOGO_PATH, LOGO_MAX_SIZE)

ASSETS = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}


def get_color(val): return {0: color_maze_path, 1: color_maze_wall, 2: color_maze_start, 3: color_maze_end,
                            4: color_maze_explored, 5: color_maze_path_found}.get(val, white)


### --- SISTEMA DE BOTÕES 3D FÍSICOS ---
def draw_3d_button(screen, rect, color, dark_color, text, pressed, text_color=white, font=button_font):
    if pressed:
        pygame.draw.rect(screen, dark_color, rect, border_radius=10)
        if text:
            text_surf = font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=(rect.centerx, rect.centery + 2))
            screen.blit(text_surf, text_rect)
    else:
        shadow_rect = pygame.Rect(rect.x, rect.y, rect.w, rect.h)
        pygame.draw.rect(screen, dark_color, shadow_rect, border_radius=10)
        top_rect = pygame.Rect(rect.x, rect.y - 4, rect.w, rect.h)
        pygame.draw.rect(screen, color, top_rect, border_radius=10)
        if text:
            text_surf = font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=top_rect.center)
            screen.blit(text_surf, text_rect)


class CaixaTexto:
    def __init__(self, x, y, w, h, text, bg_color=green_box, text_color=text_dark):
        self.rect = pygame.Rect(x, y, w, h)
        self.bg_color = bg_color
        self.bg_color_dark = (max(0, bg_color[0] - 40), max(0, bg_color[1] - 40), max(0, bg_color[2] - 40))
        self.text_color = text_color
        self.text = text
        self.txt_surface = button_font.render(text, True, text_color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isnumeric() and len(self.text) < 4:
                self.text += event.unicode
            self.txt_surface = button_font.render(self.text, True, self.text_color)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color_dark, self.rect, border_radius=4)
        pygame.draw.rect(screen, self.bg_color, (self.rect.x + 1, self.rect.y + 1, self.rect.w - 2, self.rect.h - 2),
                         border_radius=4)
        if self.active: pygame.draw.rect(screen, yellow, self.rect, 2, border_radius=4)
        text_rect = self.txt_surface.get_rect(midright=(self.rect.right - 8, self.rect.centery))
        screen.blit(self.txt_surface, text_rect)


class Slider:
    def __init__(self, x, y, w, min_val, max_val, current_val):
        self.rect = pygame.Rect(x, y, w, 16)
        self.min_val, self.max_val, self.val = min_val, max_val, current_val
        self.handle_rect = pygame.Rect(x + int(w * (current_val / max_val)), y - 4, 24, 28)
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.handle_rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.left, min(event.pos[0], self.rect.right - self.handle_rect.w))
            self.handle_rect.x = pos_x
            self.val = int(self.min_val + ((pos_x - self.rect.left) / (self.rect.width - self.handle_rect.w) * (
                        self.max_val - self.min_val)))

    def draw(self, screen):
        pygame.draw.rect(screen, bg_main, self.rect, border_radius=8)
        pygame.draw.rect(screen, dark_gray, self.rect, 1, border_radius=8)
        draw_3d_button(screen, self.handle_rect, white, gray, "", pressed=self.dragging)
        val_box = pygame.Rect(self.handle_rect.centerx - 25, self.handle_rect.bottom + 6, 50, 22)
        pygame.draw.rect(screen, white, val_box, border_radius=4)
        val_surf = small_font.render(f"{self.val} ms", True, text_dark)
        screen.blit(val_surf, val_surf.get_rect(center=val_box.center))


### --- ESTADO GLOBAL E GEOMETRIA ---
sidebar_w = 550
margin = 20
top_margin = 100

SIZE_OPTIONS = [40, 60, 80, 100, 200]
ui_selected_size = 40
applied_size = 40

# INICIALIZAÇÃO CORRETA: O Labirinto inicia na paridade correta (40, 40)
inputs = {
    'st_x': CaixaTexto(margin + 175, top_margin + 70, 50, 35, '0'),
    'st_y': CaixaTexto(margin + 235, top_margin + 70, 50, 35, '0'),
    'en_x': CaixaTexto(margin + 175, top_margin + 120, 50, 35, '40'),
    'en_y': CaixaTexto(margin + 235, top_margin + 120, 50, 35, '40')
}

applied_start = (0, 0)
applied_end = (40, 40)


def get_safe_size(s): return s + 1 if s % 2 == 0 else s


maze_base = AuxFunctions.profundidade_grid_topeira(applied_start, applied_end, get_safe_size(applied_size),
                                                   get_safe_size(applied_size))
maze_display = copy.deepcopy(maze_base)

skip_anim = False
speed_slider = Slider(margin + 15, 815, sidebar_w - (margin * 2) - 30, 0, 100, 50)

right_edge = sidebar_w - margin - 15
btn_aplicar = pygame.Rect(right_edge - 200, top_margin + 70, 200, 85)

ALGORITMOS = [
    {'id': 'bfs', 'name': 'BUSCA EM AMPLITUDE'},
    {'id': 'dfs', 'name': 'BUSCA EM PROFUNDIDADE'},
    {'id': 'dls', 'name': 'PROFUNDIDADE LIMITADA', 'has_limit': True},
    {'id': 'ids', 'name': 'PROFUNDIDADE ITERATIVA', 'has_limit': True},
    {'id': 'bi', 'name': 'BUSCA BIDIRECIONAL'},
    {'id': 'ucs', 'name': 'CUSTO UNIFORME'},
    {'id': 'greedy', 'name': 'BUSCA GULOSA'},
    {'id': 'astar', 'name': 'A-STAR (A*)'},
    {'id': 'ida', 'name': 'IDA*'}
]
results = {}

box_w = 75
gap = 10
box3_x = right_edge - box_w
box2_x = box3_x - gap - box_w
box1_x = box2_x - gap - box_w
algo_w = box1_x - gap - (margin + 15)

start_y_algos = top_margin + 245
btn_height, btn_spacing = 32, 10

for index, algo in enumerate(ALGORITMOS):
    y_pos = start_y_algos + (index * (btn_height + btn_spacing))
    algo['rect'] = pygame.Rect(margin + 15, y_pos, algo_w, btn_height)
    if algo.get('has_limit'):
        algo['limit_box'] = CaixaTexto(box1_x, y_pos, box_w, btn_height, '20')
    results[algo['id']] = {'cost': '--', 'nodes': '--'}


def draw_text(s, t, f, c, pos, align='left'):
    surf = f.render(t, True, c)
    rect = surf.get_rect(topleft=pos) if align == 'left' else surf.get_rect(center=pos)
    s.blit(surf, rect)


def draw_sidebar(mouse_pos, pending_changes):
    pygame.draw.rect(display, bg_main, (0, 0, sidebar_w, display_h))

    # ÁREA DA LOGO
    logo_rect = pygame.Rect(margin, margin, LOGO_MAX_SIZE[0], LOGO_MAX_SIZE[1])
    if logo_img:
        display.blit(logo_img, logo_rect.topleft)
    else:
        pygame.draw.rect(display, bg_panel, logo_rect, border_radius=6)
        pygame.draw.rect(display, dark_gray, logo_rect, 2, border_radius=6)
        draw_text(display, "LOGO AQUI", default_font, text_gray, logo_rect.center, align='center')

    # PAINEL 1
    panel1_rect = pygame.Rect(margin, top_margin, sidebar_w - (margin * 2), 175)
    pygame.draw.rect(display, bg_panel, panel1_rect, border_radius=10)

    lbl_tam = pygame.Rect(margin + 15, top_margin + 15, 200, 35)
    draw_3d_button(display, lbl_tam, white, dark_gray, "TAMANHO DO LABIRINTO", pressed=False, text_color=text_dark,
                   font=button_font)

    lbl_ent = pygame.Rect(margin + 15, top_margin + 70, 150, 35)
    draw_3d_button(display, lbl_ent, white, dark_gray, "ENTRADA (X,Y)", pressed=False, text_color=text_dark,
                   font=button_font)

    lbl_sai = pygame.Rect(margin + 15, top_margin + 120, 150, 35)
    draw_3d_button(display, lbl_sai, white, dark_gray, "SAÍDA (X,Y)", pressed=False, text_color=text_dark, font=button_font)

    btn_w = 46
    gap_w = 10
    start_x = 245
    for i, size in enumerate(SIZE_OPTIONS):
        btn_rect = pygame.Rect(start_x + (i * (btn_w + gap_w)), top_margin + 15, btn_w, 35)
        is_selected = (size == ui_selected_size)
        is_hover = btn_rect.collidepoint(mouse_pos)

        btn_color = white_dark if (is_hover and not is_selected) else white
        draw_3d_button(display, btn_rect, btn_color, gray, str(size), pressed=is_selected, text_color=text_dark)

    for i in inputs.values(): i.draw(display)

    draw_3d_button(display, btn_aplicar, red_btn, red_btn_dark, "APLICAR MODIFICAÇÕES", pressed=not pending_changes,
                   font=button_font)

    # PAINEL 2
    panel2_rect = pygame.Rect(margin, top_margin + 190, sidebar_w - (margin * 2), 440)
    pygame.draw.rect(display, bg_panel, panel2_rect, border_radius=10)

    draw_text(display, "Algoritmo", default_font, white, (margin + 15, top_margin + 205))
    draw_text(display, "Lim", default_font, white, (box1_x + (box_w // 2), top_margin + 210), align='center')
    draw_text(display, "Custo", default_font, white, (box2_x + (box_w // 2), top_margin + 210), align='center')
    draw_text(display, "Nós", default_font, white, (box3_x + (box_w // 2), top_margin + 210), align='center')
    pygame.draw.line(display, gray, (margin + 15, top_margin + 225), (right_edge, top_margin + 225), 2)

    for algo in ALGORITMOS:
        btn, res = algo['rect'], results[algo['id']]
        is_hover = btn.collidepoint(mouse_pos)
        draw_3d_button(display, btn, white if not is_hover else white_dark, gray, algo['name'], pressed=False,
                       text_color=text_dark, font=button_font)

        if algo.get('has_limit'): algo['limit_box'].draw(display)

        box_cost = CaixaTexto(box2_x, btn.y, box_w, btn.h, str(res['cost']))
        box_nodes = CaixaTexto(box3_x, btn.y, box_w, btn.h, str(res['nodes']))
        box_cost.draw(display);
        box_nodes.draw(display)

    # PAINEL 3
    panel3_rect = pygame.Rect(margin, 740, sidebar_w - (margin * 2), 135)
    pygame.draw.rect(display, bg_panel, panel3_rect, border_radius=10)

    skip_btn = pygame.Rect(margin + 15, 760, panel3_rect.w - 30, 40)
    txt_skip = "PULAR ANIMAÇÃO: ATIVADO" if skip_anim else "PULAR ANIMAÇÃO: DESATIVADO"
    draw_3d_button(display, skip_btn, red_btn, red_btn_dark, txt_skip, pressed=skip_anim)

    speed_slider.draw(display)


def draw_maze():
    pygame.draw.rect(display, bg_main, (sidebar_w, 0, display_l - sidebar_w, display_h))
    area_w, area_h = (display_l - sidebar_w) - 10, display_h - 10
    offset_x, offset_y = sidebar_w + 5, 5

    pygame.draw.rect(display, white, (offset_x, offset_y, area_w, area_h))

    s_lines = get_safe_size(applied_size)
    for r in range(s_lines):
        for c in range(s_lines):
            x1 = offset_x + (c * area_w) // s_lines
            y1 = offset_y + (r * area_h) // s_lines
            x2 = offset_x + ((c + 1) * area_w) // s_lines
            y2 = offset_y + ((r + 1) * area_h) // s_lines

            cell = maze_display[r][c]
            if cell != 0:
                pygame.draw.rect(display, get_color(cell), (x1, y1, x2 - x1, y2 - y1))


def show_popup(message):
    overlay = pygame.Surface((display_l, display_h), pygame.SRCALPHA);
    overlay.fill((0, 0, 0, 180));
    display.blit(overlay, (0, 0))
    p_r = pygame.Rect((display_l // 2 - 200), (display_h // 2 - 100), 400, 200)
    pygame.draw.rect(display, bg_panel, p_r, border_radius=15);
    pygame.draw.rect(display, white, p_r, width=2, border_radius=15)
    draw_text(display, message, default_font, yellow, p_r.center, align='center')
    draw_text(display, "Clique para fechar", small_font, text_gray, (p_r.centerx, p_r.bottom - 20), align='center')
    pygame.display.flip()
    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]: waiting = False


# --- LOOP PRINCIPAL ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    try:
        current_st = (int(inputs['st_x'].text), int(inputs['st_y'].text))
        current_en = (int(inputs['en_x'].text), int(inputs['en_y'].text))
        pending_changes = (ui_selected_size != applied_size) or (current_st != applied_start) or (
                    current_en != applied_end)
    except ValueError:
        pending_changes = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

        for i in inputs.values(): i.handle_event(event)
        for algo in ALGORITMOS:
            if algo.get('has_limit'): algo['limit_box'].handle_event(event)

        speed_slider.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                btn_w = 46
                gap_w = 10
                start_x = 245
                for i, size in enumerate(SIZE_OPTIONS):
                    btn_rect = pygame.Rect(start_x + (i * (btn_w + gap_w)), top_margin + 15, btn_w, 35)

                    if btn_rect.collidepoint(mouse_pos):
                        ui_selected_size = size

                        s_lines = get_safe_size(size)
                        inputs['st_x'].text, inputs['st_y'].text = '0', '0'
                        inputs['en_x'].text, inputs['en_y'].text = str(s_lines - 1), str(s_lines - 1)

                        inputs['st_x'].txt_surface = button_font.render('0', True, text_dark)
                        inputs['st_y'].txt_surface = button_font.render('0', True, text_dark)
                        inputs['en_x'].txt_surface = button_font.render(str(s_lines - 1), True, text_dark)
                        inputs['en_y'].txt_surface = button_font.render(str(s_lines - 1), True, text_dark)

                        play_sfx('click')

                skip_btn_rect = pygame.Rect(margin + 15, 760, sidebar_w - (margin * 2) - 30, 40)
                if skip_btn_rect.collidepoint(mouse_pos):
                    skip_anim = not skip_anim
                    play_sfx('click')

            if mouse_pos[0] > sidebar_w:
                area_w, area_h = (display_l - sidebar_w) - 10, display_h - 10
                offset_x, offset_y = sidebar_w + 5, 5
                s_lines = get_safe_size(applied_size)

                if offset_x <= mouse_pos[0] <= offset_x + area_w and offset_y <= mouse_pos[1] <= offset_y + area_h:
                    col, row = ((mouse_pos[0] - offset_x) * s_lines) // area_w, (
                                (mouse_pos[1] - offset_y) * s_lines) // area_h
                    if 0 <= row < s_lines and 0 <= col < s_lines:

                        if event.button == 1:
                            maze_base[applied_start[0]][applied_start[1]] = 0
                            applied_start = (row, col)
                            maze_base[row][col] = 2
                            inputs['st_x'].text, inputs['st_y'].text = str(row), str(col)

                        elif event.button == 3:
                            maze_base[applied_end[0]][applied_end[1]] = 0
                            applied_end = (row, col)
                            maze_base[row][col] = 3
                            inputs['en_x'].text, inputs['en_y'].text = str(row), str(col)

                        inputs['st_x'].txt_surface = button_font.render(str(applied_start[0]), True, text_dark)
                        inputs['st_y'].txt_surface = button_font.render(str(applied_start[1]), True, text_dark)
                        inputs['en_x'].txt_surface = button_font.render(str(applied_end[0]), True, text_dark)
                        inputs['en_y'].txt_surface = button_font.render(str(applied_end[1]), True, text_dark)

                        maze_display = copy.deepcopy(maze_base)
                        play_sfx('click')

            if event.button == 1 and btn_aplicar.collidepoint(mouse_pos) and pending_changes:
                try:
                    new_st = (int(inputs['st_x'].text), int(inputs['st_y'].text))
                    new_en = (int(inputs['en_x'].text), int(inputs['en_y'].text))
                    s_lines = get_safe_size(ui_selected_size)

                    if max(new_st[0], new_st[1], new_en[0], new_en[1]) >= s_lines:
                        # Auto-correção passiva de limites
                        inputs['st_x'].text, inputs['st_y'].text = '0', '0'
                        inputs['en_x'].text, inputs['en_y'].text = str(s_lines - 1), str(s_lines - 1)
                        inputs['st_x'].txt_surface = button_font.render('0', True, text_dark)
                        inputs['st_y'].txt_surface = button_font.render('0', True, text_dark)
                        inputs['en_x'].txt_surface = button_font.render(str(s_lines - 1), True, text_dark)
                        inputs['en_y'].txt_surface = button_font.render(str(s_lines - 1), True, text_dark)
                        raise ValueError(f"Fora dos limites. Corrigido automaticamente.")

                    # --- CHECAGEM DE PARIDADE MATEMÁTICA (A SALVAÇÃO DA TOPEIRA) ---
                    # A topeira só escava em pulos de 2. Logo, a paridade (Par/Ímpar) do fim DEVE ser igual a do Início.
                    en_x, en_y = new_en
                    if new_st[0] % 2 != en_x % 2:
                        en_x = en_x - 1 if en_x > 0 else en_x + 1
                    if new_st[1] % 2 != en_y % 2:
                        en_y = en_y - 1 if en_y > 0 else en_y + 1
                    new_en = (en_x, en_y)

                    # Atualiza as caixinhas na interface caso a correção tenha sido feita
                    inputs['en_x'].text, inputs['en_y'].text = str(en_x), str(en_y)
                    inputs['en_x'].txt_surface = button_font.render(str(en_x), True, text_dark)
                    inputs['en_y'].txt_surface = button_font.render(str(en_y), True, text_dark)

                    applied_size = ui_selected_size
                    applied_start = new_st
                    applied_end = new_en

                    maze_base = AuxFunctions.profundidade_grid_topeira(applied_start, applied_end, s_lines, s_lines)
                    maze_display = copy.deepcopy(maze_base)
                    for k in results: results[k] = {'cost': '--', 'nodes': '--'}
                    play_sfx('click')

                except ValueError as e:
                    play_sfx('error')
                    show_popup(f"Aviso: {e}")

            if event.button == 1 and mouse_pos[0] <= sidebar_w:
                for algo in ALGORITMOS:
                    if 'rect' in algo and algo['rect'].collidepoint(mouse_pos):
                        play_sfx('click')
                        algo_id = algo['id']
                        maze_display = copy.deepcopy(maze_base)
                        s_lines = get_safe_size(applied_size)


                        def animar_busca(current_lim=None):
                            global skip_anim
                            if skip_anim: return
                            current_mouse_pos = pygame.mouse.get_pos()
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                                speed_slider.handle_event(ev)
                                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and skip_btn_rect.collidepoint(
                                        ev.pos):
                                    skip_anim = True;
                                    play_sfx('click')

                            if current_lim is not None and algo_id == 'ids':
                                algo['limit_box'].text = str(current_lim)
                                algo['limit_box'].txt_surface = button_font.render(str(current_lim), True, text_dark)

                            draw_sidebar(current_mouse_pos, pending_changes)
                            draw_maze()
                            pygame.display.flip()
                            if speed_slider.val > 0: pygame.time.delay(speed_slider.val)


                        try:
                            path = None
                            if algo.get('has_limit') and not algo['limit_box'].text:
                                raise ValueError("Defina um limite")

                            if algo_id == 'bfs':
                                path = np_searcher.breadth_first_search(applied_start, applied_end, s_lines, s_lines,
                                                                        maze_display, animar_busca)
                            elif algo_id == 'dfs':
                                path = np_searcher.depth_first_search(applied_start, applied_end, s_lines, s_lines,
                                                                      maze_display, animar_busca)
                            elif algo_id == 'dls':
                                lim_dls = int(algo['limit_box'].text)
                                path = np_searcher.depth_limited_search(applied_start, applied_end, s_lines, s_lines,
                                                                        maze_display, lim_dls, animar_busca)
                            elif algo_id == 'ids':
                                lim_max_ids = int(algo['limit_box'].text)
                                path = np_searcher.aprof_iterativo_grid(applied_start, applied_end, s_lines, s_lines,
                                                                        maze_display, lim_max_ids, animar_busca)
                                algo['limit_box'].text = str(lim_max_ids)
                                algo['limit_box'].txt_surface = button_font.render(str(lim_max_ids), True, text_dark)

                            if path:
                                path.pop(0)
                                for step in path:
                                    if maze_display[step[0]][step[1]] not in [2, 3]: maze_display[step[0]][step[1]] = 5
                                results[algo_id]['cost'] = str(len(path))
                                results[algo_id]['nodes'] = str(sum(row.count(4) for row in maze_display) + len(path))
                                play_sfx('success')
                                if skip_anim: draw_maze(); pygame.display.flip()
                            elif algo_id in ['bfs', 'dfs', 'dls', 'ids']:
                                play_sfx('error');
                                show_popup('Nenhum caminho encontrado')

                        except Exception as e:
                            show_popup(f"Erro: {e}")

    draw_sidebar(mouse_pos, pending_changes)
    draw_maze()
    pygame.display.flip()

pygame.quit()
sys.exit()