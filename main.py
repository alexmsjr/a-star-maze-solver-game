import pygame
import sys
import os
import copy
import random
import traceback
import AuxFunctions
from NPsearch import NPsearch
from Psearch import Psearch

pygame.init()
pygame.mixer.init()
np_searcher = NPsearch()
p_searcher = Psearch()

### =========================================================================
### SEÇÃO 1: CONFIGURAÇÃO DE TELA E RESPONSIVIDADE (Base 1920x1080)
### =========================================================================
infoObject = pygame.display.Info()
current_w, current_h = infoObject.current_w, infoObject.current_h
display = pygame.display.set_mode((current_w, current_h))
pygame.display.set_caption("")

sc_x = current_w / 1920.0
sc_y = current_h / 1080.0
sc_min = min(sc_x, sc_y)


def sx(val): return int(val * sc_x)


def sy(val): return int(val * sc_y)


def sm(val): return int(val * sc_min)


### =========================================================================
### SEÇÃO 2: CORES ESQUEUMÓRFICAS E FONTES
### =========================================================================
bg_maze = (40, 42, 45)
panel_base = (220, 220, 220)
tab_bg = (245, 245, 245)
panel_highlight = (255, 255, 255)
panel_shadow = (140, 140, 140)
panel_dark_shadow = (80, 80, 80)

display_bg = (35, 35, 35)
display_off_bg = (20, 20, 20)
led_green = (50, 220, 50)
led_blue = (50, 150, 255)
led_orange = (255, 120, 30)
led_off = (40, 40, 40)

btn_blue = (15, 80, 210)
btn_white = (250, 250, 250)
btn_pressed = (200, 200, 200)
btn_yellow = (235, 225, 15)
btn_red = (220, 25, 25)
text_dark = (40, 40, 40)
text_light = (180, 180, 180)
text_gray = (130, 130, 130)

font_large = pygame.font.SysFont("arial", sm(70), bold=True)
font_labels = pygame.font.SysFont("arial", sm(18), bold=True)
font_led = pygame.font.SysFont("consolas", sm(22), bold=True)
font_btn_algo = pygame.font.SysFont("arial", sm(12), bold=True)
font_btn_side = pygame.font.SysFont("arial", sm(18), bold=True)

color_maze_wall = (90, 90, 90)
color_maze_path = (250, 250, 250)
color_maze_start = (46, 135, 10)
color_maze_end = (255, 0, 0)
color_maze_explored = (50, 100, 200)
color_maze_path_found = (226, 183, 20)
color_maze_dirt = (160, 82, 45)

FOOTER_H = sy(280)
FOOTER_Y = current_h - FOOTER_H
maze_margin = sm(20)


### =========================================================================
### SEÇÃO 3: ASSETS E GERENCIADOR DE FROTA
### =========================================================================
def load_sound(path): return pygame.mixer.Sound(path) if os.path.exists(path) else None


SFX = {'click': load_sound(r'sounds\click_sfx.ogg'), 'success': load_sound(r'sounds\success_sfx.ogg'),
       'error': load_sound(r'sounds\error_sfx.ogg')}


def play_sfx(sound_name):
    if SFX.get(sound_name): SFX[sound_name].play()


def load_img_auto_crop(path):
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            img.set_colorkey((255, 255, 255))
            return img.subsurface(img.get_bounding_rect())
        except:
            return None
    return None


ASSETS = {
    2: {'up': load_img_auto_crop(os.path.join('maze', 'up.png')),
        'down': load_img_auto_crop(os.path.join('maze', 'down.png')),
        'left': load_img_auto_crop(os.path.join('maze', 'left.png')),
        'right': load_img_auto_crop(os.path.join('maze', 'right.png'))},
    3: {'h': load_img_auto_crop(os.path.join('maze', 'h_end.png')),
        'v': load_img_auto_crop(os.path.join('maze', 'v_end.png'))},
    6: load_img_auto_crop(os.path.join('maze', 'ground.png'))
}


class GerenciadorFrota:
    def __init__(self, base_path="vehicles"):
        self.catalogo = {}
        self.scan_vehicles(base_path)

    def scan_vehicles(self, base_path):
        if not os.path.exists(base_path): return
        for size_folder in os.listdir(base_path):
            if not size_folder.isdigit(): continue
            tamanho = int(size_folder)
            if tamanho not in self.catalogo: self.catalogo[tamanho] = []
            size_path = os.path.join(base_path, size_folder)
            for modelo in os.listdir(size_path):
                modelo_path = os.path.join(size_path, modelo)
                if not os.path.isdir(modelo_path): continue
                for cor in os.listdir(modelo_path):
                    cor_path = os.path.join(modelo_path, cor)
                    if not os.path.isdir(cor_path): continue
                    imgs = {}
                    for d in ['up.png', 'down.png', 'left.png', 'right.png']:
                        img_rec = load_img_auto_crop(os.path.join(cor_path, d))
                        if img_rec: imgs[d.replace('.png', '')] = img_rec
                    if imgs: self.catalogo[tamanho].append({"modelo": modelo, "cor": cor, "imagens": imgs})
        self.catalogo = {k: v for k, v in self.catalogo.items() if len(v) > 0}

    def sortear_veiculo_exato(self, tamanho, orientacao):
        if tamanho not in self.catalogo: return None
        comp = [v for v in self.catalogo[tamanho] if
                (orientacao == 'H' and ('left' in v['imagens'] or 'right' in v['imagens'])) or (
                            orientacao == 'V' and ('up' in v['imagens'] or 'down' in v['imagens']))]
        return random.choice(comp) if comp else None


gerenciador_frota = GerenciadorFrota("vehicles")
veiculos_estacionados = {}


def find_car_anchor(maze_grid, r, c, rows, cols):
    for r_idx in range(rows):
        for c_idx in range(cols):
            val = maze_grid[r_idx][c_idx]
            if val >= 100 and val in veiculos_estacionados:
                v = veiculos_estacionados[val]
                if r_idx <= r < r_idx + v['h'] and c_idx <= c < c_idx + v['w']: return r_idx, c_idx, val
    return None, None, None


def estacionar_carros(maze_grid, rows, cols, reparar=False):
    global veiculos_estacionados
    if not reparar:
        veiculos_estacionados.clear(); next_id = 100
    else:
        next_id = max(veiculos_estacionados.keys(), default=99) + 1

    tamanhos = sorted(gerenciador_frota.catalogo.keys(), reverse=True)
    for t in tamanhos:
        for r in range(rows):
            for c in range(cols):
                if maze_grid[r][c] == 1:
                    can_H = True
                    if c + t <= cols:
                        for i in range(t):
                            if maze_grid[r][c + i] != 1: can_H = False; break
                    else:
                        can_H = False

                    can_V = True
                    if r + t <= rows:
                        for i in range(t):
                            if maze_grid[r + i][c] != 1: can_V = False; break
                    else:
                        can_V = False

                    orientacao = None
                    if can_H and can_V:
                        orientacao = random.choice(['H', 'V'])
                    elif can_H:
                        orientacao = 'H'
                    elif can_V:
                        orientacao = 'V'

                    if orientacao:
                        v = gerenciador_frota.sortear_veiculo_exato(t, orientacao)
                        if v:
                            dirs = [d for d in ['left', 'right'] if d in v['imagens']] if orientacao == 'H' else [d for
                                                                                                                  d in
                                                                                                                  ['up',
                                                                                                                   'down']
                                                                                                                  if
                                                                                                                  d in
                                                                                                                  v[
                                                                                                                      'imagens']]
                            if dirs:
                                df = random.choice(dirs)
                                veiculos_estacionados[next_id] = {'surface': v['imagens'][df],
                                                                  'w': (t if orientacao == 'H' else 1),
                                                                  'h': (1 if orientacao == 'H' else t), 'direction': df}
                                maze_grid[r][c] = next_id
                                if orientacao == 'H':
                                    for i in range(1, t): maze_grid[r][c + i] = -1
                                else:
                                    for i in range(1, t): maze_grid[r + i][c] = -1
                                next_id += 1
    return maze_grid


### =========================================================================
### SEÇÃO 4: FUNÇÕES DE DESENHO FLAT 3D RETRO
### =========================================================================
def draw_raised_panel(surface, rect, base_color, border_width=5, pressed=False, is_tab=False):
    outline_color = (35, 35, 35)
    shadow_depth = sm(border_width)
    radius = sm(4)
    outline_thick = max(1, sm(2))

    if pressed:
        pressed_rect = pygame.Rect(rect.x, rect.y + shadow_depth, rect.w, rect.h - shadow_depth)
        pygame.draw.rect(surface, base_color, pressed_rect, border_radius=radius)
        pygame.draw.rect(surface, outline_color, pressed_rect, outline_thick, border_radius=radius)
    else:
        if is_tab:
            pygame.draw.rect(surface, outline_color, rect, border_radius=radius)
            top_rect = pygame.Rect(rect.x, rect.y, rect.w, rect.h - shadow_depth)
            pygame.draw.rect(surface, base_color, top_rect, border_radius=radius)
            pygame.draw.rect(surface, outline_color, top_rect, outline_thick, border_radius=radius)
        else:
            pygame.draw.rect(surface, outline_color, rect, border_radius=radius)
            top_rect = pygame.Rect(rect.x, rect.y, rect.w, rect.h - shadow_depth)
            pygame.draw.rect(surface, base_color, top_rect, border_radius=radius)
            pygame.draw.rect(surface, outline_color, top_rect, outline_thick, border_radius=radius)


def draw_sunken_panel(surface, rect, bg_color=display_bg, active_glow=False):
    pygame.draw.rect(surface, bg_color, rect, border_radius=sm(2))
    if active_glow:
        pygame.draw.rect(surface, led_orange, rect, max(1, sm(2)), border_radius=sm(2))


def draw_fieldset(surface, rect, title, font, color, bg_color):
    outline_color = (180, 180, 180)
    pygame.draw.rect(surface, outline_color, rect, max(1, sm(2)), border_radius=sm(4))
    t_surf = font.render("  " + title + "  ", True, color)
    t_rect = t_surf.get_rect(centerx=rect.centerx, centery=rect.top)
    pygame.draw.rect(surface, bg_color, t_rect)
    surface.blit(t_surf, t_rect)


def draw_multiline_text(surface, text, font, color, rect):
    lines = text.split('\n')
    line_h = font.get_linesize()
    total_h = line_h * len(lines)
    start_y = rect.y + (rect.h - total_h) // 2
    for i, line in enumerate(lines):
        t_surf = font.render(line, True, color)
        surface.blit(t_surf, t_surf.get_rect(centerx=rect.centerx, y=start_y + (i * line_h)))


def show_popup(message):
    overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    display.blit(overlay, (0, 0))

    p_w, p_h = sx(500), sy(200)
    p_r = pygame.Rect((current_w - p_w) // 2, (current_h - p_h) // 2, p_w, p_h)

    draw_raised_panel(display, p_r, panel_base, border_width=6)

    draw_multiline_text(display, message, font_btn_side, text_dark, pygame.Rect(p_r.x, p_r.y, p_r.w, p_r.h - sy(50)))
    draw_multiline_text(display, "CLIQUE PARA FECHAR", font_btn_algo, text_gray,
                        pygame.Rect(p_r.x, p_r.bottom - sy(50), p_r.w, sy(50)))

    pygame.display.flip()
    waiting = True
    while waiting:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]: waiting = False


class VerticalSlider:
    def __init__(self, rect, min_val, max_val, current_val):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.val = current_val
        self.handle_h = sy(30)
        self.handle_rect = pygame.Rect(rect.x + sx(6), 0, rect.w - sx(12), self.handle_h)
        self.dragging = False
        self.update_handle_pos()

    def update_handle_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val) if self.max_val > self.min_val else 0
        track_h = self.rect.h - self.handle_h
        self.handle_rect.y = self.rect.y + int(ratio * track_h)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.move_to_mouse(event.pos[1])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.move_to_mouse(event.pos[1])

    def move_to_mouse(self, mouse_y):
        pos_y = max(self.rect.top, min(mouse_y - self.handle_h // 2, self.rect.bottom - self.handle_h))
        self.handle_rect.y = pos_y
        track_h = self.rect.h - self.handle_h
        ratio = (pos_y - self.rect.top) / track_h
        self.val = int(self.min_val + ratio * (self.max_val - self.min_val))

    def draw(self, screen):
        track_rect = pygame.Rect(self.rect.centerx - sx(4), self.rect.y, sx(8), self.rect.h)
        pygame.draw.rect(screen, display_bg, track_rect, border_radius=sm(4))
        pygame.draw.rect(screen, (100, 100, 100), track_rect, sm(1), border_radius=sm(4))

        draw_raised_panel(screen, self.handle_rect, btn_yellow, border_width=4, pressed=self.dragging)
        ly = self.handle_rect.centery
        line_color = (35, 35, 35)
        lw = max(1, sm(2))
        pygame.draw.line(screen, line_color, (self.handle_rect.left + sx(4), ly - sy(4)),
                         (self.handle_rect.right - sx(4), ly - sy(4)), lw)
        pygame.draw.line(screen, line_color, (self.handle_rect.left + sx(4), ly), (self.handle_rect.right - sx(4), ly),
                         lw)
        pygame.draw.line(screen, line_color, (self.handle_rect.left + sx(4), ly + sy(4)),
                         (self.handle_rect.right - sx(4), ly + sy(4)), lw)


### =========================================================================
### SEÇÃO 5: DADOS E LÓGICA DO SIMULADOR
### =========================================================================
ALGORITMOS = [
    {"id": "bfs", "nome": "BUSCA EM\nAMPLITUDE", "has_limit": False},
    {"id": "dfs", "nome": "BUSCA EM\nPROFUNDID.", "has_limit": False},
    {"id": "dls", "nome": "PROFUND.\nLIMITADA", "has_limit": True},
    {"id": "ids", "nome": "PROFUND.\nITERATIVA", "has_limit": True},
    {"id": "bi", "nome": "BUSCA\nBIDIRECIONAL", "has_limit": False},
    {"id": "ucs", "nome": "CUSTO\nUNIFORME", "has_limit": False},
    {"id": "grd", "nome": "BUSCA\nGULOSA", "has_limit": False},
    {"id": "ast", "nome": "BUSCA\nA-STAR (A*)", "has_limit": False},
    {"id": "ida", "nome": "BUSCA\nIDA*", "has_limit": False}
]


class InterromperBusca(Exception): pass


results = {a['id']: {'cost': '--', 'nodes': '--'} for a in ALGORITMOS}
algo_limits = {'dls': '', 'ids': ''}
active_limit_input = None

running_algo_id, next_algo_id = None, None
show_custom_tab = False
custom_anim_offset = 0.0
skip_anim = False
pending_changes = False

SIZE_OPTIONS = [20, 30, 40, 50, 60]
ui_selected_size, applied_size = 20, 20
active_tool = None

maze_area_w = current_w - (maze_margin * 2)
maze_area_h = FOOTER_Y - (maze_margin * 2)


def get_safe_size(s): return s + 1 if s % 2 == 0 else s


def get_grid_dimensions(size):
    rows = get_safe_size(size)
    ratio = maze_area_w / float(maze_area_h)
    cols = get_safe_size(int(rows * ratio))
    return rows, cols


applied_start, applied_end = (0, 0), (20, 20)
s_rows, s_cols = get_grid_dimensions(applied_size)
applied_end = (s_rows - 1, s_cols - 1)

maze_base = AuxFunctions.profundidade_grid_topeira((0, 0), (s_rows - 1, s_cols - 1), s_rows, s_cols)
for r in range(s_rows):
    for c in range(s_cols):
        if maze_base[r][c] in [2, 3]: maze_base[r][c] = 0

maze_base[applied_start[0]][applied_start[1]] = 2
maze_base[applied_end[0]][applied_end[1]] = 3
maze_base = estacionar_carros(maze_base, s_rows, s_cols)
maze_display = copy.deepcopy(maze_base)


def draw_maze():
    display.fill(bg_maze, (0, 0, current_w, FOOTER_Y))

    rows, cols = get_grid_dimensions(applied_size)
    cell_w, cell_h = maze_area_w / cols, maze_area_h / rows
    offset_x, offset_y = maze_margin, maze_margin

    def get_center(r, c):
        return int(offset_x + c * cell_w + cell_w / 2), int(offset_y + r * cell_h + cell_h / 2)

    def get_rect(r, c):
        return int(offset_x + c * cell_w), int(offset_y + r * cell_h), int(offset_x + (c + 1) * cell_w), int(
            offset_y + (r + 1) * cell_h)

    thickness = max(4, int(min(cell_w, cell_h) * 0.35))
    if thickness % 2 != 0: thickness -= 1

    for r in range(rows):
        for c in range(cols):
            if maze_base[r][c] == 6:
                x1, y1, x2, y2 = get_rect(r, c)
                w_px, h_px = x2 - x1, y2 - y1
                img_terra = ASSETS.get(6)
                if img_terra:
                    display.blit(pygame.transform.scale(img_terra, (w_px, h_px)), (x1, y1))
                else:
                    pygame.draw.rect(display, color_maze_dirt, (x1, y1, w_px, h_px), border_radius=4)

    for r in range(rows):
        for c in range(cols):
            if maze_display[r][c] == 4:
                cx, cy = get_center(r, c)
                pygame.draw.circle(display, color_maze_explored, (cx, cy), thickness // 2)
                if c < cols - 1 and maze_display[r][c + 1] in [2, 3, 4, 5]:
                    nx, ny = get_center(r, c + 1)
                    pygame.draw.rect(display, color_maze_explored, (cx, cy - thickness // 2, nx - cx, thickness))
                if c > 0 and maze_display[r][c - 1] in [2, 3, 4, 5]:
                    nx, ny = get_center(r, c - 1)
                    pygame.draw.rect(display, color_maze_explored, (nx, cy - thickness // 2, cx - nx, thickness))
                if r < rows - 1 and maze_display[r + 1][c] in [2, 3, 4, 5]:
                    nx, ny = get_center(r + 1, c)
                    pygame.draw.rect(display, color_maze_explored, (cx - thickness // 2, cy, thickness, ny - cy))
                if r > 0 and maze_display[r - 1][c] in [2, 3, 4, 5]:
                    nx, ny = get_center(r - 1, c)
                    pygame.draw.rect(display, color_maze_explored, (cx - thickness // 2, ny, thickness, cy - ny))

    for r in range(rows):
        for c in range(cols):
            if maze_display[r][c] == 5:
                cx, cy = get_center(r, c)
                pygame.draw.circle(display, color_maze_path_found, (cx, cy), thickness // 2)
                if c < cols - 1 and maze_display[r][c + 1] in [2, 3, 5]:
                    nx, ny = get_center(r, c + 1)
                    pygame.draw.rect(display, color_maze_path_found, (cx, cy - thickness // 2, nx - cx, thickness))
                if c > 0 and maze_display[r][c - 1] in [2, 3, 5]:
                    nx, ny = get_center(r, c - 1)
                    pygame.draw.rect(display, color_maze_path_found, (nx, cy - thickness // 2, cx - nx, thickness))
                if r < rows - 1 and maze_display[r + 1][c] in [2, 3, 5]:
                    nx, ny = get_center(r + 1, c)
                    pygame.draw.rect(display, color_maze_path_found, (cx - thickness // 2, cy, thickness, ny - cy))
                if r > 0 and maze_display[r - 1][c] in [2, 3, 5]:
                    nx, ny = get_center(r - 1, c)
                    pygame.draw.rect(display, color_maze_path_found, (cx - thickness // 2, ny, thickness, cy - ny))

    for r in range(rows):
        for c in range(cols):
            x1, y1, x2, y2 = get_rect(r, c)
            cell = maze_display[r][c]

            if cell >= 100 and cell in veiculos_estacionados:
                v_data = veiculos_estacionados[cell]
                w_px, h_px = (x2 - x1) * v_data['w'], (y2 - y1) * v_data['h']
                surface, direction = v_data['surface'], v_data['direction']

                orig_w, orig_h = surface.get_size()
                multiplier = 2.3 if direction in ['up', 'down'] else 2.2
                scale = min(w_px / orig_w, h_px / orig_h) * multiplier

                new_w, new_h = int(orig_w * scale), int(orig_h * scale)
                img_scaled = pygame.transform.scale(surface, (new_w, new_h))

                draw_x = x1 + (w_px - new_w) // 2
                draw_y = y1 + (h_px - new_h) // 2

                shadow_surf = img_scaled.copy()
                shadow_surf.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)
                display.blit(shadow_surf, (draw_x + sx(3), draw_y + sy(4)))
                display.blit(img_scaled, (draw_x, draw_y))

            elif cell in [2, 3]:
                if cell == 2:
                    direcao = 'right'
                    if c < cols - 1 and maze_display[r][c + 1] in [0, 4, 5, 3]:
                        direcao = 'right'
                    elif c > 0 and maze_display[r][c - 1] in [0, 4, 5, 3]:
                        direcao = 'left'
                    elif r < rows - 1 and maze_display[r + 1][c] in [0, 4, 5, 3]:
                        direcao = 'down'
                    elif r > 0 and maze_display[r - 1][c] in [0, 4, 5, 3]:
                        direcao = 'up'
                    surface = ASSETS[cell].get(direcao)
                    if not surface: surface = next((img for img in ASSETS[cell].values() if img is not None), None)

                elif cell == 3:
                    orientacao = 'h'
                    if (r > 0 and maze_display[r - 1][c] in [0, 4, 5, 2]) or (
                            r < rows - 1 and maze_display[r + 1][c] in [0, 4, 5, 2]):
                        orientacao = 'h'
                    elif (c > 0 and maze_display[r][c - 1] in [0, 4, 5, 2]) or (
                            c < cols - 1 and maze_display[r][c + 1] in [0, 4, 5, 2]):
                        orientacao = 'v'
                    surface = ASSETS[cell].get(orientacao)
                    if not surface: surface = next((img for img in ASSETS[cell].values() if img is not None), None)

                if not surface:
                    cor = color_maze_start if cell == 2 else color_maze_end
                    pygame.draw.rect(display, cor, (x1, y1, x2 - x1, y2 - y1))
                    continue

                orig_w, orig_h = surface.get_size()
                w_px, h_px = (x2 - x1), (y2 - y1)
                multiplier = 2.5 if cell == 2 else 1
                scale = min(w_px / orig_w, h_px / orig_h) * multiplier
                new_w, new_h = int(orig_w * scale), int(orig_h * scale)
                img_scaled = pygame.transform.scale(surface, (new_w, new_h))
                draw_x = x1 + (w_px - new_w) // 2
                draw_y = y1 + (h_px - new_h) // 2

                if cell == 2:
                    shadow_surf = img_scaled.copy()
                    shadow_surf.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)
                    display.blit(shadow_surf, (draw_x + sx(3), draw_y + sy(4)))
                display.blit(img_scaled, (draw_x, draw_y))


def draw_footer(mouse_pos, mouse_click):
    global running, show_custom_tab, active_limit_input, active_tool, pending_changes, next_algo_id, running_algo_id, skip_anim

    # FLAG DE BLINDAGEM: Evita que o código pare de desenhar na metade
    interromper_agora = False

    pygame.draw.rect(display, panel_base, (0, FOOTER_Y, current_w, FOOTER_H))

    # --- Painel Lateral Esquerdo ---
    draw_raised_panel(display, p_left_rect, panel_base, pressed=False)

    draw_raised_panel(display, btn_blue_rect, btn_blue, pressed=show_custom_tab)
    draw_multiline_text(display, "CUSTOMIZAR\nLABIRINTO", font_btn_algo, btn_white, btn_blue_rect)
    if mouse_click and btn_blue_rect.collidepoint(mouse_pos):
        show_custom_tab = not show_custom_tab
        active_tool = None
        play_sfx('click')
        if running_algo_id is not None:
            next_algo_id = None
            interromper_agora = True  # Prepara para interromper

    # Toggle Escuro de Pular Animação
    draw_fieldset(display, skip_fs_rect, "PULAR ANIMAÇÕES", font_btn_algo, text_gray, panel_base)

    # ATUALIZAÇÃO: Checa o clique ANTES de desenhar para mudar a cor na hora
    if mouse_click and btn_skip_rect.collidepoint(mouse_pos):
        skip_anim = not skip_anim
        play_sfx('click')

    draw_sunken_panel(display, btn_skip_rect, bg_color=display_off_bg)
    knob_w = btn_skip_rect.w // 2 + sx(5)
    knob_h = btn_skip_rect.h

    if skip_anim:
        knob_rect = pygame.Rect(btn_skip_rect.right - knob_w, btn_skip_rect.y, knob_w, knob_h)
        t_on = font_labels.render("ON", True, panel_highlight)
        display.blit(t_on, t_on.get_rect(
            center=(btn_skip_rect.left + (btn_skip_rect.w - knob_w) // 2, btn_skip_rect.centery)))
        knob_color = led_green
    else:
        knob_rect = pygame.Rect(btn_skip_rect.left, btn_skip_rect.y, knob_w, knob_h)
        t_off = font_labels.render("OFF", True, panel_highlight)
        display.blit(t_off, t_off.get_rect(
            center=(btn_skip_rect.right - (btn_skip_rect.w - knob_w) // 2, btn_skip_rect.centery)))
        knob_color = panel_shadow

    draw_raised_panel(display, knob_rect, knob_color, pressed=False)

    lx, ly, lw = knob_rect.centerx, knob_rect.centery, knob_w // 3
    pygame.draw.line(display, panel_dark_shadow, (lx - lw // 2, ly - sy(6)), (lx + lw // 2, ly - sy(6)), sm(2))
    pygame.draw.line(display, panel_dark_shadow, (lx - lw // 2, ly), (lx + lw // 2, ly), sm(2))
    pygame.draw.line(display, panel_dark_shadow, (lx - lw // 2, ly + sy(6)), (lx + lw // 2, ly + sy(6)), sm(2))

    # --- Painel Slider ---
    draw_raised_panel(display, p_slider_rect, panel_base, pressed=False)
    speed_slider.draw(display)

    # --- Painel Lateral Direito (Help, About, Quit) ---
    draw_raised_panel(display, p_right_rect, panel_base, pressed=False)
    draw_raised_panel(display, btn_help, btn_white, pressed=(mouse_click and btn_help.collidepoint(mouse_pos)))
    draw_raised_panel(display, btn_about, btn_white, pressed=(mouse_click and btn_about.collidepoint(mouse_pos)))
    draw_raised_panel(display, btn_quit, btn_white, pressed=(mouse_click and btn_quit.collidepoint(mouse_pos)))

    display.blit(font_btn_side.render("AJUDA", True, text_gray),
                 font_btn_side.render("AJUDA", True, text_gray).get_rect(center=btn_help.center))
    display.blit(font_btn_side.render("SOBRE", True, text_gray),
                 font_btn_side.render("SOBRE", True, text_gray).get_rect(center=btn_about.center))
    display.blit(font_btn_side.render("SAIR", True, text_gray),
                 font_btn_side.render("SAIR", True, text_gray).get_rect(center=btn_quit.center))

    if mouse_click and btn_quit.collidepoint(mouse_pos):
        running = False
        if running_algo_id is not None:
            interromper_agora = True

    # --- Área Central (Displays e Algoritmos) ---
    draw_raised_panel(display, center_rect, panel_base, pressed=False)

    # ATUALIZAÇÃO DE LAYOUT: O texto agora tem tamanho fixo pequeno, o resto é pros algoritmos
    label_w = sx(80)
    col_w = (center_rect.w - label_w - sx(5)) / 9.0
    start_x_algo = center_rect.x + label_w
    align_labels_x = start_x_algo - sx(10)

    display.blit(font_labels.render("CUSTO", True, text_gray), font_labels.render("CUSTO", True, text_gray).get_rect(
        midright=(align_labels_x, row_cost_y + display_h // 2)))
    display.blit(font_labels.render("NÓS", True, text_gray), font_labels.render("NÓS", True, text_gray).get_rect(
        midright=(align_labels_x, row_nodes_y + display_h // 2)))
    display.blit(font_labels.render("LIMITE", True, text_gray), font_labels.render("LIMITE", True, text_gray).get_rect(
        midright=(align_labels_x, row_limit_y + display_h // 2)))

    t_algo = font_labels.render("ALGO", True, text_gray)
    t_rithm = font_labels.render("RITIMO", True, text_gray)
    algo_center_y = row_btn_y + btn_algo_h // 2
    line_spacing = font_labels.get_linesize() - sy(4)
    display.blit(t_algo, t_algo.get_rect(midright=(align_labels_x, algo_center_y - line_spacing // 2)))
    display.blit(t_rithm, t_rithm.get_rect(midright=(align_labels_x, algo_center_y + line_spacing // 2)))

    can_interact_algo = not show_custom_tab

    for i, algo in enumerate(ALGORITMOS):
        item_x = start_x_algo + (col_w * i) + sx(5)
        item_w = col_w - sx(10)
        res = results[algo['id']]

        rect_cost = pygame.Rect(item_x, row_cost_y, item_w, display_h)
        rect_nodes = pygame.Rect(item_x, row_nodes_y, item_w, display_h)
        rect_limit = pygame.Rect(item_x, row_limit_y, item_w, display_h)

        draw_sunken_panel(display, rect_cost)
        draw_sunken_panel(display, rect_nodes)

        c_green = led_green if can_interact_algo else panel_shadow
        c_blue = led_blue if can_interact_algo else panel_shadow

        display.blit(font_led.render(res['cost'], True, c_green), font_led.render(res['cost'], True, c_green).get_rect(
            midright=(rect_cost.right - sx(8), rect_cost.centery)))
        display.blit(font_led.render(res['nodes'], True, c_blue), font_led.render(res['nodes'], True, c_blue).get_rect(
            midright=(rect_nodes.right - sx(8), rect_nodes.centery)))

        if algo['has_limit']:
            is_active_input = (active_limit_input == algo['id'])
            draw_sunken_panel(display, rect_limit, active_glow=(is_active_input and can_interact_algo))
            c_orange = led_orange if can_interact_algo else panel_shadow
            val_txt = algo_limits[algo['id']] + ("_" if is_active_input else "")
            if val_txt == "" or val_txt == "_": val_txt = "0" + val_txt
            v_limit = font_led.render(val_txt, True, c_orange)

            if mouse_click and rect_limit.collidepoint(mouse_pos) and can_interact_algo:
                active_limit_input = algo['id'];
                play_sfx('click')
            elif mouse_click and not rect_limit.collidepoint(mouse_pos) and is_active_input:
                active_limit_input = None
        else:
            draw_sunken_panel(display, rect_limit, bg_color=display_off_bg)
            v_limit = font_led.render("-", True, led_off)

        display.blit(v_limit, v_limit.get_rect(midright=(rect_limit.right - sx(8), rect_limit.centery)))

        rect_btn = pygame.Rect(item_x, row_btn_y, item_w, btn_algo_h)
        algo['rect'] = rect_btn

        is_pressed = (mouse_click and rect_btn.collidepoint(
            mouse_pos) and can_interact_algo and not pending_changes) or (running_algo_id == algo['id'])
        btn_bg = btn_white if (can_interact_algo and not pending_changes) else (200, 200, 200)
        txt_col = text_dark if (can_interact_algo and not pending_changes) else text_gray

        draw_raised_panel(display, rect_btn, btn_bg, pressed=is_pressed)
        draw_multiline_text(display, algo['nome'], font_btn_algo, txt_col, rect_btn)

        if mouse_click and rect_btn.collidepoint(mouse_pos) and can_interact_algo:
            play_sfx('click')
            if running_algo_id is not None:
                # Interrompe e prepara o terreno para o novo algoritmo
                if running_algo_id == algo['id']:
                    next_algo_id = None
                else:
                    next_algo_id = algo['id']
                interromper_agora = True
            else:
                next_algo_id = algo['id']

    # Finaliza toda a renderização 100% da tela ANTES de interromper a busca
    if interromper_agora:
        raise InterromperBusca()


### =========================================================================
### SEÇÃO 6: LOOP PRINCIPAL E SETUP INICIAL DA GEOMETRIA
### =========================================================================
clock = pygame.time.Clock()

pad = sx(15)
btn_side_w_left = sx(160)
btn_side_w_right = sx(110)
slider_w = sx(50)

p_left_rect = pygame.Rect(pad, FOOTER_Y + pad, btn_side_w_left, FOOTER_H - (pad * 2))
p_slider_rect = pygame.Rect(p_left_rect.right + pad, FOOTER_Y + pad, slider_w, FOOTER_H - (pad * 2))
p_right_rect = pygame.Rect(current_w - btn_side_w_right - pad, FOOTER_Y + pad, btn_side_w_right, FOOTER_H - (pad * 2))

center_w = p_right_rect.left - pad - p_slider_rect.right - pad
center_rect = pygame.Rect(p_slider_rect.right + pad, FOOTER_Y + pad, center_w, FOOTER_H - (pad * 2))

# Sub-retângulos Esquerdo
btn_blue_rect = pygame.Rect(p_left_rect.x + sx(20), p_left_rect.y + sy(25), p_left_rect.w - sx(40), sy(90))
skip_fs_rect = pygame.Rect(p_left_rect.x + sx(15), btn_blue_rect.bottom + sy(30), p_left_rect.w - sx(30), sy(85))
btn_skip_rect = pygame.Rect(skip_fs_rect.x + sx(10), skip_fs_rect.y + sy(25), skip_fs_rect.w - sx(20), sy(45))

# Sub-retângulos Direito
btn_h = (p_right_rect.h - sy(50)) // 3
btn_help = pygame.Rect(p_right_rect.x + sx(10), p_right_rect.y + sy(15), p_right_rect.w - sx(20), btn_h)
btn_about = pygame.Rect(p_right_rect.x + sx(10), btn_help.bottom + sy(10), p_right_rect.w - sx(20), btn_h)
btn_quit = pygame.Rect(p_right_rect.x + sx(10), btn_about.bottom + sy(10), p_right_rect.w - sx(20), btn_h)

speed_slider = VerticalSlider(
    pygame.Rect(p_slider_rect.x + sx(10), p_slider_rect.y + sy(20), p_slider_rect.w - sx(20), p_slider_rect.h - sy(40)),
    0, 100, 50)

# MUDANÇA: Correção drástica do espaçamento dos Algoritmos e Rótulos
label_w = sx(95)
col_w = (center_rect.w - label_w - sx(5)) / 9.0
start_x = center_rect.x + label_w
align_labels_x = start_x - sx(10)

display_h = sy(32)
gap_y = sy(10)
row_cost_y = center_rect.y + sy(15)
row_nodes_y = row_cost_y + display_h + gap_y
row_limit_y = row_nodes_y + display_h + gap_y
row_btn_y = row_limit_y + display_h + gap_y
btn_algo_h = center_rect.bottom - row_btn_y - sy(15)

# Setup Aba Customização
tab_pad_x, tab_gap_x = center_rect.w * 0.016, center_rect.w * 0.016
w_size, w_tools, w_caution, w_random = center_rect.w * 0.38, center_rect.w * 0.23, center_rect.w * 0.23, center_rect.w * 0.08
x_size = center_rect.x + tab_pad_x
x_tools = x_size + w_size + tab_gap_x
x_caution = x_tools + w_tools + tab_gap_x
x_random = x_caution + w_caution + tab_gap_x

rects_sizes = [pygame.Rect(0, 0, 0, 0) for _ in range(5)]
rects_tools = {"START": pygame.Rect(0, 0, 0, 0), "END": pygame.Rect(0, 0, 0, 0), "DIRT": pygame.Rect(0, 0, 0, 0)}
rect_apply = pygame.Rect(0, 0, 0, 0)
rect_rand = pygame.Rect(0, 0, 0, 0)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        speed_slider.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True

            # --- Clicks no Labirinto (Atualização Instantânea) ---
            if mouse_pos[1] < FOOTER_Y and active_tool:
                rows, cols = get_grid_dimensions(applied_size)
                cell_w, cell_h = maze_area_w / cols, maze_area_h / rows

                adj_x = mouse_pos[0] - maze_margin
                adj_y = mouse_pos[1] - maze_margin

                if 0 <= adj_x < maze_area_w and 0 <= adj_y < maze_area_h:
                    col, row = int(adj_x // cell_w), int(adj_y // cell_h)

                    if 0 <= row < rows and 0 <= col < cols:
                        if active_tool == "START":
                            maze_base[applied_start[0]][applied_start[1]] = 0
                            ar, ac, aid = find_car_anchor(maze_base, row, col, rows, cols)
                            if aid:
                                v = veiculos_estacionados.pop(aid)
                                for i in range(v['h']):
                                    for j in range(v['w']): maze_base[ar + i][ac + j] = 1
                            applied_start = (row, col)
                            maze_base[row][col] = 2
                            estacionar_carros(maze_base, rows, cols, reparar=True)

                        elif active_tool == "END":
                            maze_base[applied_end[0]][applied_end[1]] = 0
                            ar, ac, aid = find_car_anchor(maze_base, row, col, rows, cols)
                            if aid:
                                v = veiculos_estacionados.pop(aid)
                                for i in range(v['h']):
                                    for j in range(v['w']): maze_base[ar + i][ac + j] = 1
                            applied_end = (row, col)
                            maze_base[row][col] = 3
                            estacionar_carros(maze_base, rows, cols, reparar=True)

                        elif active_tool == "DIRT":
                            ar, ac, aid = find_car_anchor(maze_base, row, col, rows, cols)
                            if aid:
                                v = veiculos_estacionados.pop(aid)
                                for i in range(v['h']):
                                    for j in range(v['w']): maze_base[ar + i][ac + j] = 0
                            if maze_base[row][col] == 6:
                                maze_base[row][col] = 0
                            elif maze_base[row][col] == 0:
                                maze_base[row][col] = 6

                        maze_display = copy.deepcopy(maze_base)
                        for k in results: results[k] = {'cost': '--', 'nodes': '--'}
                        play_sfx('click')

            # --- Clicks na Aba Animada ---
            if show_custom_tab and custom_anim_offset > center_rect.h - 5:
                for i, size in enumerate(SIZE_OPTIONS):
                    if rects_sizes[i].collidepoint(mouse_pos):
                        ui_selected_size = size
                        pending_changes = True
                        play_sfx('click')

                for tool_name, rect in rects_tools.items():
                    if rect.collidepoint(mouse_pos):
                        active_tool = None if active_tool == tool_name else tool_name
                        play_sfx('click')

                if (rect_apply.collidepoint(mouse_pos) and pending_changes) or rect_rand.collidepoint(mouse_pos):
                    applied_size = ui_selected_size
                    rows, cols = get_grid_dimensions(applied_size)

                    if applied_start[0] >= rows or applied_start[1] >= cols: applied_start = (0, 0)
                    if applied_end[0] >= rows or applied_end[1] >= cols: applied_end = (rows - 1, cols - 1)

                    maze_base = AuxFunctions.profundidade_grid_topeira((0, 0), (rows - 1, cols - 1), rows, cols)
                    for r in range(rows):
                        for c in range(cols):
                            if maze_base[r][c] in [2, 3]: maze_base[r][c] = 0

                    maze_base[applied_start[0]][applied_start[1]] = 2
                    maze_base[applied_end[0]][applied_end[1]] = 3
                    maze_base = estacionar_carros(maze_base, rows, cols)
                    maze_display = copy.deepcopy(maze_base)
                    for k in results: results[k] = {'cost': '--', 'nodes': '--'}

                    pending_changes = False
                    active_tool = None
                    play_sfx('success')

        if event.type == pygame.KEYDOWN and active_limit_input:
            if event.key == pygame.K_BACKSPACE:
                algo_limits[active_limit_input] = algo_limits[active_limit_input][:-1]
            elif event.unicode.isnumeric() and len(algo_limits[active_limit_input]) < 4:
                algo_limits[active_limit_input] += event.unicode

    # Matemática da Aba Animada
    tab_h = center_rect.h
    target_offset = tab_h if show_custom_tab else 0
    custom_anim_offset += (target_offset - custom_anim_offset) * 0.15

    curr_tab_y = center_rect.bottom - custom_anim_offset
    curr_tab_fs_h = sy(120)
    curr_tab_fs_y = curr_tab_y + (tab_h - curr_tab_fs_h) // 2

    bw_s = (w_size - sx(10) * 6) / 5
    bh_s = bw_s
    by_s = curr_tab_fs_y + (curr_tab_fs_h - bh_s) // 2
    for j in range(5): rects_sizes[j] = pygame.Rect(x_size + sx(10) + j * (bw_s + sx(10)), by_s, bw_s, bh_s)

    bw_t = (w_tools - sx(10) * 4) / 3
    bh_t = bw_t
    by_t = curr_tab_fs_y + (curr_tab_fs_h - bh_t) // 2
    rects_tools["START"] = pygame.Rect(x_tools + sx(10), by_t, bw_t, bh_t)
    rects_tools["END"] = pygame.Rect(x_tools + sx(10) + bw_t + sx(10), by_t, bw_t, bh_t)
    rects_tools["DIRT"] = pygame.Rect(x_tools + sx(10) + 2 * (bw_t + sx(10)), by_t, bw_t, bh_t)

    rect_apply = pygame.Rect(x_caution + sx(15), by_t, w_caution - sx(30), bh_t)
    rect_rand = pygame.Rect(x_random + (w_random - bh_t) / 2, by_t, bh_t, bh_t)

    draw_maze()
    draw_footer(mouse_pos, mouse_click)

    if custom_anim_offset > 1:
        tab_rect = pygame.Rect(center_rect.x, curr_tab_y, center_rect.w, tab_h)
        display.set_clip(center_rect)
        draw_raised_panel(display, tab_rect, tab_bg, border_width=6, pressed=False, is_tab=True)

        draw_fieldset(display, pygame.Rect(x_size, curr_tab_fs_y, w_size, curr_tab_fs_h), "MAZE SIZE", font_btn_algo,
                      text_gray, tab_bg)
        for j, val in enumerate(SIZE_OPTIONS):
            r = rects_sizes[j]
            is_active_size = (val == ui_selected_size)
            draw_raised_panel(display, r, btn_pressed if is_active_size else btn_white, pressed=is_active_size)
            display.blit(font_labels.render(str(val), True, text_dark),
                         font_labels.render(str(val), True, text_dark).get_rect(center=r.center))

        draw_fieldset(display, pygame.Rect(x_tools, curr_tab_fs_y, w_tools, curr_tab_fs_h), "TOOLS", font_btn_algo,
                      text_gray, tab_bg)
        for tool_name, r in rects_tools.items():
            is_active = (active_tool == tool_name)
            draw_raised_panel(display, r, (200, 220, 255) if is_active else btn_white, pressed=is_active)
            lbl = "CAR" if tool_name == "START" else "END" if tool_name == "END" else "BRK"
            display.blit(font_btn_algo.render(lbl, True, text_dark),
                         font_btn_algo.render(lbl, True, text_dark).get_rect(center=r.center))

        draw_fieldset(display, pygame.Rect(x_caution, curr_tab_fs_y, w_caution, curr_tab_fs_h), "CAUTION",
                      font_btn_algo, text_gray, tab_bg)
        draw_raised_panel(display, rect_apply, btn_yellow if pending_changes else panel_shadow,
                          pressed=(not pending_changes))
        t_apply = font_btn_algo.render("APPLY MODIFICATIONS", True, text_dark)
        display.blit(t_apply, t_apply.get_rect(center=rect_apply.center))

        draw_fieldset(display, pygame.Rect(x_random, curr_tab_fs_y, w_random, curr_tab_fs_h), "RANDOMIZE",
                      font_btn_algo, text_gray, tab_bg)
        draw_raised_panel(display, rect_rand, btn_red, pressed=False)

        display.set_clip(None)

    pygame.display.flip()

    # -----------------------------------------------------------------------
    # NÚCLEO DE BUSCAS
    # -----------------------------------------------------------------------
    while next_algo_id is not None:
        algo_id = next_algo_id
        next_algo_id = None
        running_algo_id = algo_id
        maze_display = copy.deepcopy(maze_base)
        s_rows, s_cols = get_grid_dimensions(applied_size)
        algo_dict = next(a for a in ALGORITMOS if a['id'] == algo_id)


        def animar_busca(current_lim=None):
            global next_algo_id, skip_anim
            if skip_anim:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                return

            curr_mouse = pygame.mouse.get_pos()
            curr_click = False

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                speed_slider.handle_event(ev)
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    curr_click = True

            draw_maze()
            draw_footer(curr_mouse, curr_click)
            pygame.display.flip()

            if speed_slider.val > 0: pygame.time.delay(speed_slider.val)


        try:
            result_search = None
            limit_val = int(algo_limits.get(algo_id, 0)) if algo_dict['has_limit'] and algo_limits.get(algo_id) else 0
            if algo_dict.get('has_limit') and limit_val <= 0: raise ValueError("Defina um limite válido maior que 0.")

            if algo_id == 'bfs':
                result_search = np_searcher.breadth_first_search(applied_start, applied_end, s_rows, s_cols,
                                                                 maze_display, animar_busca)
            elif algo_id == 'dfs':
                result_search = np_searcher.depth_first_search(applied_start, applied_end, s_rows, s_cols, maze_display,
                                                               animar_busca)
            elif algo_id == 'dls':
                result_search = np_searcher.depth_limited_search(applied_start, applied_end, s_rows, s_cols,
                                                                 maze_display, limit_val, animar_busca)
            elif algo_id == 'ids':
                result_search = np_searcher.aprof_iterativo_grid(applied_start, applied_end, s_rows, s_cols,
                                                                 maze_display, limit_val, animar_busca)
            elif algo_id == 'bi':
                result_search = np_searcher.bidirecional_grid(applied_start, applied_end, s_rows, s_cols, maze_display,
                                                              animar_busca)
            elif algo_id == 'ucs':
                result_search = p_searcher.uniform_cost(applied_start, applied_end, s_rows, s_cols, maze_display,
                                                               animar_busca)
            elif algo_id == 'grd':
                result_search = p_searcher.greedy(applied_start, applied_end, s_rows, s_cols, maze_display,
                                                  animar_busca)
            elif algo_id == 'ast':
                result_search = p_searcher.a_star(applied_start, applied_end, s_rows, s_cols, maze_display,
                                                  animar_busca)
            elif algo_id == 'ida':
                result_search = p_searcher.ida_star(applied_start, applied_end, s_rows, s_cols, maze_display,
                                                    animar_busca)

            if result_search:
                if isinstance(result_search, tuple) and len(result_search) == 3:
                    path, cost, total_nodes = result_search
                    print("Custo")
                elif isinstance(result_search, tuple) and len(result_search) == 2:
                    path, total_nodes= result_search
                    cost = len(path) - 1
                    print("Interativo")
                else:
                    path = result_search
                    cost = len(path)-1
                    total_nodes = sum(row.count(4) for row in maze_display) + len(path)
                    print("Outros")


                if len(path) > 0: path.pop(0)
                for step in path:
                    if maze_display[step[0]][step[1]] not in [2, 3]: maze_display[step[0]][step[1]] = 5

                results[algo_id]['cost'] = str(cost)
                results[algo_id]['nodes'] = str(total_nodes)
                play_sfx('success')
            else:
                play_sfx('error')
                show_popup("A IA não conseguiu encontrar uma saída!")

        except InterromperBusca:
            maze_display = copy.deepcopy(maze_base)
        except ValueError as e:
            play_sfx('error')
            show_popup(str(e))
        except Exception as e:
            print(f"Erro: {e}")
            play_sfx('error')
            show_popup("Ocorreu um erro interno no algoritmo.")
        finally:
            running_algo_id = None

    clock.tick(60)

pygame.quit()
sys.exit()