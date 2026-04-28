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

### DISPLAY SETUP
display_l = 1600
display_h = 1000
display = pygame.display.set_mode((display_l, display_h))
pygame.display.set_caption("Lab de IA - Estacionamento Voador")

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
sky_blue = (135, 206, 235)

color_maze_wall = gray
color_maze_path = white
color_maze_start = (46, 135, 10)
color_maze_end = (255, 0, 0)
color_maze_explored = (50, 100, 200)
color_maze_path_found = yellow
color_maze_dirt = (160, 82, 45)


### -------------------------------------------------------------------------
### ================= SISTEMA INTELIGENTE DE FROTA ==========================
### -------------------------------------------------------------------------
def load_img_auto_crop(path):
    if os.path.exists(path):
        try:
            img_raw = pygame.image.load(path).convert_alpha()
            img_raw.set_colorkey((255, 255, 255))
            bounding_rect = img_raw.get_bounding_rect()
            return img_raw.subsurface(bounding_rect)
        except:
            return None
    return None


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
                    imagens_carregadas = {}
                    for direcao_arquivo in ['up.png', 'down.png', 'left.png', 'right.png']:
                        caminho_img = os.path.join(cor_path, direcao_arquivo)
                        img_recortada = load_img_auto_crop(caminho_img)
                        if img_recortada: imagens_carregadas[direcao_arquivo.replace('.png', '')] = img_recortada
                    if imagens_carregadas: self.catalogo[tamanho].append(
                        {"modelo": modelo, "cor": cor, "imagens": imagens_carregadas})
        self.catalogo = {k: v for k, v in self.catalogo.items() if len(v) > 0}

    # NOVO: Busca cirúrgica do tamanho exato
    def sortear_veiculo_exato(self, tamanho, orientacao):
        if tamanho not in self.catalogo: return None
        compativeis = []
        for v in self.catalogo[tamanho]:
            if orientacao == 'H' and ('left' in v['imagens'] or 'right' in v['imagens']):
                compativeis.append(v)
            elif orientacao == 'V' and ('up' in v['imagens'] or 'down' in v['imagens']):
                compativeis.append(v)

        if compativeis: return random.choice(compativeis)
        return None


gerenciador_frota = GerenciadorFrota("vehicles")
veiculos_estacionados = {}


def find_car_anchor(maze_grid, r, c, s_lines):
    for r_idx in range(s_lines):
        for c_idx in range(s_lines):
            val = maze_grid[r_idx][c_idx]
            if val >= 100 and val in veiculos_estacionados:
                v = veiculos_estacionados[val]
                if r_idx <= r < r_idx + v['h'] and c_idx <= c < c_idx + v['w']:
                    return r_idx, c_idx, val
    return None, None, None


def estacionar_carros(maze_grid, size, reparar=False):
    global veiculos_estacionados
    if not reparar:
        veiculos_estacionados.clear()
        next_id = 100
    else:
        next_id = max(veiculos_estacionados.keys(), default=99) + 1

    # Pega todos os tamanhos que você tem instalados, do maior pro menor (ex: [3, 2, 1])
    tamanhos_disponiveis = sorted(gerenciador_frota.catalogo.keys(), reverse=True)

    for t in tamanhos_disponiveis:
        for r in range(size):
            for c in range(size):
                if maze_grid[r][c] == 1:
                    # Verifica se cabe na Horizontal
                    can_H = True
                    if c + t <= size:
                        for i in range(t):
                            if maze_grid[r][c + i] != 1: can_H = False; break
                    else:
                        can_H = False

                    # Verifica se cabe na Vertical
                    can_V = True
                    if r + t <= size:
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
                        veiculo = gerenciador_frota.sortear_veiculo_exato(t, orientacao)
                        if veiculo:
                            direcoes = [d for d in ['left', 'right'] if
                                        d in veiculo['imagens']] if orientacao == 'H' else [d for d in ['up', 'down'] if
                                                                                            d in veiculo['imagens']]
                            if direcoes:
                                direcao_final = random.choice(direcoes)
                                sprite = veiculo['imagens'][direcao_final]
                                anchor_id = next_id
                                next_id += 1
                                w_cells = t if orientacao == 'H' else 1
                                h_cells = 1 if orientacao == 'H' else t

                                veiculos_estacionados[anchor_id] = {'surface': sprite, 'w': w_cells, 'h': h_cells,
                                                                    'direction': direcao_final}
                                maze_grid[r][c] = anchor_id
                                if orientacao == 'H':
                                    for i in range(1, w_cells): maze_grid[r][c + i] = -1
                                else:
                                    for i in range(1, h_cells): maze_grid[r + i][c] = -1
    return maze_grid


### -------------------------------------------------------------------------
### ================= UI E RENDERIZAÇÃO PADRÃO ==============================
### -------------------------------------------------------------------------
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

# Carrega as imagens do início (carro direcional) e do fim na pasta 'maze'
ASSETS = {
    2: {
        'up': load_img_auto_crop(os.path.join('maze', 'up.png')),
        'down': load_img_auto_crop(os.path.join('maze', 'down.png')),
        'left': load_img_auto_crop(os.path.join('maze', 'left.png')),
        'right': load_img_auto_crop(os.path.join('maze', 'right.png'))
    },
    3: {
        'h': load_img_auto_crop(os.path.join('maze', 'h_end.png')),
        'v': load_img_auto_crop(os.path.join('maze', 'v_end.png'))
    },
    6: load_img_auto_crop(os.path.join('maze', 'ground.png'))
}

def draw_3d_button(screen, rect, color, dark_color, text, pressed, text_color=white, font=button_font):
    if pressed:
        pygame.draw.rect(screen, dark_color, rect, border_radius=10)
        if text:
            text_surf = font.render(text, True, text_color)
            screen.blit(text_surf, text_surf.get_rect(center=(rect.centerx, rect.centery + 2)))
    else:
        pygame.draw.rect(screen, dark_color, pygame.Rect(rect.x, rect.y, rect.w, rect.h), border_radius=10)
        top_rect = pygame.Rect(rect.x, rect.y - 4, rect.w, rect.h)
        pygame.draw.rect(screen, color, top_rect, border_radius=10)
        if text:
            text_surf = font.render(text, True, text_color)
            screen.blit(text_surf, text_surf.get_rect(center=top_rect.center))


class CaixaTexto:
    def __init__(self, x, y, w, h, text, bg_color=green_box, text_color=text_dark):
        self.rect = pygame.Rect(x, y, w, h)
        self.bg_color, self.bg_color_dark = bg_color, (max(0, bg_color[0] - 40), max(0, bg_color[1] - 40),
                                                       max(0, bg_color[2] - 40))
        self.text_color, self.text = text_color, text
        self.txt_surface = button_font.render(text, True, text_color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self.active = self.rect.collidepoint(event.pos)
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
        screen.blit(self.txt_surface, self.txt_surface.get_rect(midright=(self.rect.right - 8, self.rect.centery)))


class Slider:
    def __init__(self, x, y, w, min_val, max_val, current_val):
        self.rect, self.min_val, self.max_val, self.val = pygame.Rect(x, y, w, 16), min_val, max_val, current_val
        self.handle_rect = pygame.Rect(x + int(w * (current_val / max_val)), y - 4, 24, 28)
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.handle_rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.left, min(event.pos[0], self.rect.right - self.handle_rect.w))
            self.handle_rect.x, self.val = pos_x, int(self.min_val + (
                    (pos_x - self.rect.left) / (self.rect.width - self.handle_rect.w) * (
                    self.max_val - self.min_val)))

    def draw(self, screen):
        pygame.draw.rect(screen, bg_main, self.rect, border_radius=8)
        pygame.draw.rect(screen, dark_gray, self.rect, 1, border_radius=8)
        draw_3d_button(screen, self.handle_rect, white, gray, "", pressed=self.dragging)
        val_box = pygame.Rect(self.handle_rect.centerx - 25, self.handle_rect.bottom + 6, 50, 22)
        pygame.draw.rect(screen, white, val_box, border_radius=4)
        val_surf = small_font.render(f"{self.val} ms", True, text_dark)
        screen.blit(val_surf, val_surf.get_rect(center=val_box.center))


class InterromperBusca(Exception): pass


running_algo_id, next_algo_id = None, None
sidebar_w, margin, top_margin = 550, 20, 100

SIZE_OPTIONS = [20, 30, 40, 50, 60]
ui_selected_size, applied_size = 20, 20
inputs = {
    'st_x': CaixaTexto(margin + 175, top_margin + 70, 50, 35, '0'),
    'st_y': CaixaTexto(margin + 235, top_margin + 70, 50, 35, '0'),
    'en_x': CaixaTexto(margin + 175, top_margin + 120, 50, 35, '20'),
    'en_y': CaixaTexto(margin + 235, top_margin + 120, 50, 35, '20')
}
applied_start, applied_end = (0, 0), (20, 20)
last_generated_start, last_generated_end = (0, 0), (20, 20)


def get_safe_size(s): return s + 1 if s % 2 == 0 else s


# ================= GERAÇÃO INICIAL (Solução do Topeira) =================
s_lines_init = get_safe_size(applied_size)
maze_base = AuxFunctions.profundidade_grid_topeira((0, 0), (s_lines_init - 1, s_lines_init - 1), s_lines_init,
                                                   s_lines_init)

for r in range(s_lines_init):
    for c in range(s_lines_init):
        if maze_base[r][c] in [2, 3]: maze_base[r][c] = 0

maze_base[applied_start[0]][applied_start[1]] = 2
maze_base[applied_end[0]][applied_end[1]] = 3

maze_base = estacionar_carros(maze_base, s_lines_init)
maze_display = copy.deepcopy(maze_base)

skip_anim = False
speed_slider = Slider(margin + 15, display_h - 85, sidebar_w - (margin * 2) - 30, 0, 100, 50)
right_edge = sidebar_w - margin - 15
btn_aplicar = pygame.Rect(right_edge - 200, top_margin + 70, 200, 85)

ALGORITMOS = [{'id': 'bfs', 'name': 'BUSCA EM AMPLITUDE'},
              {'id': 'dfs', 'name': 'BUSCA EM PROFUNDIDADE'},
              {'id': 'dls', 'name': 'PROF. LIMITADA', 'has_limit': True},
              {'id': 'ids', 'name': 'PROF. ITERATIVA', 'has_limit': True},
              {'id': 'bi', 'name': 'BUSCA BIDIRECIONAL'},
              {'id': 'ucs', 'name': 'CUSTO UNIFORME'},
              {'id': 'greedy', 'name': 'BUSCA GULOSA'},
              {'id': 'astar', 'name': 'A-STAR (A*)'},
              {'id': 'ida', 'name': 'IDA*'}]
results = {}
box_w, gap = 75, 10
box3_x = right_edge - box_w;
box2_x = box3_x - gap - box_w;
box1_x = box2_x - gap - box_w
algo_w = box1_x - gap - (margin + 15)
start_y_algos, btn_height, btn_spacing = top_margin + 245, 32, 10

for index, algo in enumerate(ALGORITMOS):
    y_pos = start_y_algos + (index * (btn_height + btn_spacing))
    algo['rect'] = pygame.Rect(margin + 15, y_pos, algo_w, btn_height)
    if algo.get('has_limit'): algo['limit_box'] = CaixaTexto(box1_x, y_pos, box_w, btn_height, '20')
    results[algo['id']] = {'cost': '--', 'nodes': '--'}


def draw_text(s, t, f, c, pos, align='left'):
    surf = f.render(t, True, c)
    s.blit(surf, surf.get_rect(topleft=pos) if align == 'left' else surf.get_rect(center=pos))


def draw_sidebar(mouse_pos, pending_changes, running_algo_id=None):
    pygame.draw.rect(display, bg_main, (0, 0, sidebar_w, display_h))
    logo_rect = pygame.Rect(margin, margin, LOGO_MAX_SIZE[0], LOGO_MAX_SIZE[1])
    if logo_img:
        display.blit(logo_img, logo_rect.topleft)
    else:
        pygame.draw.rect(display, bg_panel, logo_rect, border_radius=6)
        pygame.draw.rect(display, dark_gray, logo_rect, 2, border_radius=6)
        draw_text(display, "LOGO AQUI", default_font, text_gray, logo_rect.center, align='center')

    panel1_rect = pygame.Rect(margin, top_margin, sidebar_w - (margin * 2), 175)
    pygame.draw.rect(display, bg_panel, panel1_rect, border_radius=10)
    draw_3d_button(display, pygame.Rect(margin + 15, top_margin + 15, 200, 35), white, dark_gray,
                   "TAMANHO DO LABIRINTO", False, text_dark, button_font)
    draw_3d_button(display, pygame.Rect(margin + 15, top_margin + 70, 150, 35), white, dark_gray, "ENTRADA (X,Y)",
                   False, text_dark, button_font)
    draw_3d_button(display, pygame.Rect(margin + 15, top_margin + 120, 150, 35), white, dark_gray, "SAÍDA (X,Y)", False,
                   text_dark, button_font)

    btn_w, gap_w, start_x = 46, 10, 245
    for i, size in enumerate(SIZE_OPTIONS):
        btn_rect = pygame.Rect(start_x + (i * (btn_w + gap_w)), top_margin + 15, btn_w, 35)
        is_hover = btn_rect.collidepoint(mouse_pos)
        draw_3d_button(display, btn_rect, white_dark if (is_hover and size != ui_selected_size) else white, gray,
                       str(size), size == ui_selected_size, text_dark)

    for i in inputs.values(): i.draw(display)
    draw_3d_button(display, btn_aplicar, red_btn, red_btn_dark, "APLICAR MODIFICAÇÕES", not pending_changes,
                   font=button_font)

    panel2_rect = pygame.Rect(margin, top_margin + 190, sidebar_w - (margin * 2), 440)
    pygame.draw.rect(display, bg_panel, panel2_rect, border_radius=10)
    draw_text(display, "Algoritmo", default_font, white, (margin + 15, top_margin + 205))
    draw_text(display, "Lim", default_font, white, (box1_x + (box_w // 2), top_margin + 210), align='center')
    draw_text(display, "Custo", default_font, white, (box2_x + (box_w // 2), top_margin + 210), align='center')
    draw_text(display, "Nós", default_font, white, (box3_x + (box_w // 2), top_margin + 210), align='center')
    pygame.draw.line(display, gray, (margin + 15, top_margin + 225), (right_edge, top_margin + 225), 2)

    for algo in ALGORITMOS:
        btn, res = algo['rect'], results[algo['id']]
        is_running = (algo['id'] == running_algo_id)
        btn_color = yellow if is_running else (white_dark if btn.collidepoint(mouse_pos) else white)
        draw_3d_button(display, btn, btn_color, gray, algo['name'], is_running, text_dark, button_font)
        if algo.get('has_limit'): algo['limit_box'].draw(display)
        CaixaTexto(box2_x, btn.y, box_w, btn.h, str(res['cost'])).draw(display)
        CaixaTexto(box3_x, btn.y, box_w, btn.h, str(res['nodes'])).draw(display)

    panel3_rect = pygame.Rect(margin, display_h - 160, sidebar_w - (margin * 2), 135)
    pygame.draw.rect(display, bg_panel, panel3_rect, border_radius=10)
    draw_3d_button(display, pygame.Rect(margin + 15, display_h - 140, panel3_rect.w - 30, 40), red_btn, red_btn_dark,
                   "PULAR ANIMAÇÃO: ATIVADO" if skip_anim else "PULAR ANIMAÇÃO: DESATIVADO", skip_anim)
    speed_slider.draw(display)


def draw_maze():
    pygame.draw.rect(display, sky_blue, (sidebar_w, 0, display_l - sidebar_w, display_h))
    offset_x, offset_y = sidebar_w + 60, 60
    area_w, area_h = (display_l - sidebar_w) - 120, display_h - 120

    # --- AJUSTE VISUAL: PLATAFORMA MAIOR (PADDING DE SEGURANÇA) ---
    pad = 25  # Expande a base visualmente sem mexer no grid
    pygame.draw.rect(display, (50, 90, 130),
                     (offset_x - pad + 20, offset_y - pad + 25, area_w + pad * 2, area_h + pad * 2), border_radius=15)
    pygame.draw.rect(display, (45, 45, 50), (offset_x - pad, offset_y - pad, area_w + pad * 2, area_h + pad * 2),
                     border_radius=10)

    s_lines = get_safe_size(applied_size)
    cell_w, cell_h = area_w / s_lines, area_h / s_lines

    def get_center(r, c):
        return int(offset_x + c * cell_w + cell_w / 2), int(offset_y + r * cell_h + cell_h / 2)

    def get_rect(r, c):
        return int(offset_x + c * cell_w), int(offset_y + r * cell_h), int(offset_x + (c + 1) * cell_w), int(
            offset_y + (r + 1) * cell_h)

    # --- AJUSTE VISUAL: FIM DOS CAROCINHOS ---
    thickness = max(4, int(cell_w * 0.35))
    # Força a espessura a ser sempre um número PAR para o diâmetro do círculo casar perfeitamente com a linha!
    if thickness % 2 != 0:
        thickness -= 1

    # ==============================================================
    # PASSAGEM 1: BASE (Terrenos Pesados - 6)
    # ==============================================================
    for r in range(s_lines):
        for c in range(s_lines):
            # Lê da base para nunca esquecer que aqui tem textura, mesmo após a busca passar!
            if maze_base[r][c] == 6:
                x1, y1, x2, y2 = get_rect(r, c)
                w_px, h_px = x2 - x1, y2 - y1

                img_terra = ASSETS.get(6)
                if img_terra:
                    # Redimensiona a textura para cobrir a célula exata
                    img_scaled = pygame.transform.scale(img_terra, (w_px, h_px))
                    display.blit(img_scaled, (x1, y1))
                else:
                    # Fallback (Plano B) caso a imagem 'terra.png' não exista na pasta
                    pygame.draw.rect(display, color_maze_dirt, (x1, y1, w_px, h_px), border_radius=4)

    # ==============================================================
    # PASSAGEM 2: ÁREA EXPLORADA (A Teia Azul Contínua - 4)
    # ==============================================================
    for r in range(s_lines):
        for c in range(s_lines):
            if maze_display[r][c] == 4:
                cx, cy = get_center(r, c)
                pygame.draw.circle(display, (50, 100, 200), (cx, cy), thickness // 2)

                # Desenhando com RETÂNGULOS (Flawless, sem quinas vazando)
                # Direita
                if c < s_lines - 1 and maze_display[r][c + 1] in [2, 3, 4, 5]:
                    nx, ny = get_center(r, c + 1)
                    pygame.draw.rect(display, (50, 100, 200), (cx, cy - thickness // 2, nx - cx, thickness))
                # Esquerda
                if c > 0 and maze_display[r][c - 1] in [2, 3, 4, 5]:
                    nx, ny = get_center(r, c - 1)
                    pygame.draw.rect(display, (50, 100, 200), (nx, cy - thickness // 2, cx - nx, thickness))
                # Baixo
                if r < s_lines - 1 and maze_display[r + 1][c] in [2, 3, 4, 5]:
                    nx, ny = get_center(r + 1, c)
                    pygame.draw.rect(display, (50, 100, 200), (cx - thickness // 2, cy, thickness, ny - cy))
                # Cima
                if r > 0 and maze_display[r - 1][c] in [2, 3, 4, 5]:
                    nx, ny = get_center(r - 1, c)
                    pygame.draw.rect(display, (50, 100, 200), (cx - thickness // 2, ny, thickness, cy - ny))

        # ==============================================================
        # PASSAGEM 3: CAMINHO FINAL (A Linha Amarela Superior - 5)
        # ==============================================================
        for r in range(s_lines):
            for c in range(s_lines):
                if maze_display[r][c] == 5:
                    cx, cy = get_center(r, c)
                    pygame.draw.circle(display, yellow, (cx, cy), thickness // 2)

                    # Direita
                    if c < s_lines - 1 and maze_display[r][c + 1] in [2, 3, 5]:
                        nx, ny = get_center(r, c + 1)
                        pygame.draw.rect(display, yellow, (cx, cy - thickness // 2, nx - cx, thickness))
                    # Esquerda
                    if c > 0 and maze_display[r][c - 1] in [2, 3, 5]:
                        nx, ny = get_center(r, c - 1)
                        pygame.draw.rect(display, yellow, (nx, cy - thickness // 2, cx - nx, thickness))
                    # Baixo
                    if r < s_lines - 1 and maze_display[r + 1][c] in [2, 3, 5]:
                        nx, ny = get_center(r + 1, c)
                        pygame.draw.rect(display, yellow, (cx - thickness // 2, cy, thickness, ny - cy))
                    # Cima
                    if r > 0 and maze_display[r - 1][c] in [2, 3, 5]:
                        nx, ny = get_center(r - 1, c)
                        pygame.draw.rect(display, yellow, (cx - thickness // 2, ny, thickness, cy - ny))

    # ==============================================================
    # PASSAGEM 4: CARROS, SOMBRAS E ÍCONES
    # ==============================================================
    for r in range(s_lines):
        for c in range(s_lines):
            x1, y1, x2, y2 = get_rect(r, c)
            cell = maze_display[r][c]

            if cell >= 100 and cell in veiculos_estacionados:
                v_data = veiculos_estacionados[cell]
                w_px = (x2 - x1) * v_data['w']
                h_px = (y2 - y1) * v_data['h']
                surface = v_data['surface']
                direction = v_data['direction']

                orig_w, orig_h = surface.get_size()
                multiplier = 2.3 if direction in ['up', 'down'] else 2.2
                scale = min(w_px / orig_w, h_px / orig_h) * multiplier

                new_w, new_h = int(orig_w * scale), int(orig_h * scale)
                img_scaled = pygame.transform.scale(surface, (new_w, new_h))

                draw_x = x1 + (w_px - new_w) // 2
                draw_y = y1 + (h_px - new_h) // 2

                shadow_surf = img_scaled.copy()
                shadow_surf.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)
                display.blit(shadow_surf, (draw_x + 3, draw_y + 4))

                display.blit(img_scaled, (draw_x, draw_y))

            elif cell in [2, 3]:

                if cell == 2:
                    # Lógica de Visão do Carro (Início)
                    direcao = 'right'

                    if c < s_lines - 1 and maze_display[r][c + 1] in [0, 4, 5, 3]:
                        direcao = 'right'

                    elif c > 0 and maze_display[r][c - 1] in [0, 4, 5, 3]:
                        direcao = 'left'

                    elif r < s_lines - 1 and maze_display[r + 1][c] in [0, 4, 5, 3]:
                        direcao = 'down'

                    elif r > 0 and maze_display[r - 1][c] in [0, 4, 5, 3]:
                        direcao = 'up'

                    surface = ASSETS[cell].get(direcao)

                    if not surface: surface = next((img for img in ASSETS[cell].values() if img is not None), None)

                elif cell == 3:
                    # Lógica da Faixa no Chão (Fim)
                    orientacao = 'h'  # Padrão

                    # Se a rua vem de Cima/Baixo, a faixa cruza na Horizontal (h)
                    if (r > 0 and maze_display[r - 1][c] in [0, 4, 5, 2]) or (
                            r < s_lines - 1 and maze_display[r + 1][c] in [0, 4, 5, 2]):

                        orientacao = 'h'

                    # Se a rua vem da Esquerda/Direita, a faixa cruza na Vertical (v)
                    elif (c > 0 and maze_display[r][c - 1] in [0, 4, 5, 2]) or (
                            c < s_lines - 1 and maze_display[r][c + 1] in [0, 4, 5, 2]):

                        orientacao = 'v'

                    surface = ASSETS[cell].get(orientacao)

                    if not surface: surface = next((img for img in ASSETS[cell].values() if img is not None), None)

                # Fallback de segurança se a imagem não carregar
                if not surface:
                    cor = (46, 135, 10) if cell == 2 else (255, 0, 0)

                    pygame.draw.rect(display, cor, (x1, y1, x2 - x1, y2 - y1))

                    continue

                orig_w, orig_h = surface.get_size()
                w_px, h_px = (x2 - x1), (y2 - y1)

                # Multiplicador: 1.60 para o Carro ficar grandão, 1.15 para a faixa cobrir a rua sem vazar pras paredes
                multiplier = 2.5 if cell == 2 else 1

                scale = min(w_px / orig_w, h_px / orig_h) * multiplier
                new_w, new_h = int(orig_w * scale), int(orig_h * scale)
                img_scaled = pygame.transform.scale(surface, (new_w, new_h))
                draw_x = x1 + (w_px - new_w) // 2
                draw_y = y1 + (h_px - new_h) // 2

                # Detalhe: Apenas o Carro (2) tem sombra. A faixa (3) é pintada chapada no asfalto!
                if cell == 2:
                    shadow_surf = img_scaled.copy()

                    shadow_surf.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)

                    display.blit(shadow_surf, (draw_x + 3, draw_y + 4))

                display.blit(img_scaled, (draw_x, draw_y))


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
        pending_changes = (ui_selected_size != applied_size) or (current_st != last_generated_start) or (
                current_en != last_generated_end)
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
                btn_w, gap_w, start_x = 46, 10, 245
                for i, size in enumerate(SIZE_OPTIONS):
                    if pygame.Rect(start_x + (i * (btn_w + gap_w)), top_margin + 15, btn_w, 35).collidepoint(mouse_pos):
                        ui_selected_size = size
                        s_lines = get_safe_size(size)
                        inputs['st_x'].text, inputs['st_y'].text = '0', '0'
                        inputs['en_x'].text, inputs['en_y'].text = str(s_lines - 1), str(s_lines - 1)
                        for k in inputs: inputs[k].txt_surface = button_font.render(inputs[k].text, True, text_dark)
                        play_sfx('click')

                if pygame.Rect(margin + 15, display_h - 140, sidebar_w - (margin * 2) - 30, 40).collidepoint(mouse_pos):
                    skip_anim = not skip_anim
                    play_sfx('click')

            # CLIQUES NO GRID
            if mouse_pos[0] > sidebar_w:
                offset_x, offset_y = sidebar_w + 60, 60
                area_w, area_h = (display_l - sidebar_w) - 120, display_h - 120
                s_lines = get_safe_size(applied_size)

                if offset_x <= mouse_pos[0] <= offset_x + area_w and offset_y <= mouse_pos[1] <= offset_y + area_h:
                    col, row = ((mouse_pos[0] - offset_x) * s_lines) // area_w, (
                            (mouse_pos[1] - offset_y) * s_lines) // area_h
                    if 0 <= row < s_lines and 0 <= col < s_lines:

                        if event.button == 1:
                            maze_base[applied_start[0]][applied_start[1]] = 0

                            ar, ac, aid = find_car_anchor(maze_base, row, col, s_lines)
                            if aid:
                                v = veiculos_estacionados.pop(aid)
                                for i in range(v['h']):
                                    for j in range(v['w']):
                                        maze_base[ar + i][ac + j] = 1

                            applied_start = (row, col)
                            maze_base[row][col] = 2
                            estacionar_carros(maze_base, s_lines, reparar=True)
                            inputs['st_x'].text, inputs['st_y'].text = str(row), str(col)

                        elif event.button == 2:  # MEIO: Pinta/Apaga Terra (Pesada)
                            if maze_base[row][col] == 6:
                                maze_base[row][col] = 0
                            elif maze_base[row][col] == 0:
                                maze_base[row][col] = 6

                        elif event.button == 3:
                            maze_base[applied_end[0]][applied_end[1]] = 0

                            ar, ac, aid = find_car_anchor(maze_base, row, col, s_lines)
                            if aid:
                                v = veiculos_estacionados.pop(aid)
                                for i in range(v['h']):
                                    for j in range(v['w']):
                                        maze_base[ar + i][ac + j] = 1

                            applied_end = (row, col)
                            maze_base[row][col] = 3
                            estacionar_carros(maze_base, s_lines, reparar=True)
                            inputs['en_x'].text, inputs['en_y'].text = str(row), str(col)
                        if event.button in [1, 2, 3]:
                            for k in inputs: inputs[k].txt_surface = button_font.render(inputs[k].text, True, text_dark)
                            maze_display = copy.deepcopy(maze_base)
                            play_sfx('click')

            # BOTÃO APLICAR MODIFICAÇÕES
            if event.button == 1 and btn_aplicar.collidepoint(mouse_pos) and pending_changes:
                try:
                    new_st = (int(inputs['st_x'].text), int(inputs['st_y'].text))
                    new_en = (int(inputs['en_x'].text), int(inputs['en_y'].text))
                    s_lines = get_safe_size(ui_selected_size)

                    if max(new_st[0], new_st[1], new_en[0], new_en[1]) >= s_lines:
                        inputs['st_x'].text, inputs['st_y'].text = '0', '0'
                        inputs['en_x'].text, inputs['en_y'].text = str(s_lines - 1), str(s_lines - 1)
                        for k in inputs: inputs[k].txt_surface = button_font.render(inputs[k].text, True, text_dark)
                        raise ValueError(f"Fora dos limites. Corrigido automaticamente.")

                    en_x, en_y = new_en
                    if new_st[0] % 2 != en_x % 2: en_x = en_x - 1 if en_x > 0 else en_x + 1
                    if new_st[1] % 2 != en_y % 2: en_y = en_y - 1 if en_y > 0 else en_y + 1
                    new_en = (en_x, en_y)

                    inputs['en_x'].text, inputs['en_y'].text = str(en_x), str(en_y)
                    for k in ['en_x', 'en_y']: inputs[k].txt_surface = button_font.render(inputs[k].text, True,
                                                                                          text_dark)

                    applied_size, applied_start, applied_end = ui_selected_size, new_st, new_en
                    last_generated_start, last_generated_end = new_st, new_en

                    maze_base = AuxFunctions.profundidade_grid_topeira((0, 0), (s_lines - 1, s_lines - 1), s_lines,
                                                                       s_lines)
                    for r in range(s_lines):
                        for c in range(s_lines):
                            if maze_base[r][c] in [2, 3]: maze_base[r][c] = 0

                    maze_base[applied_start[0]][applied_start[1]] = 2
                    maze_base[applied_end[0]][applied_end[1]] = 3

                    maze_base = estacionar_carros(maze_base, s_lines)
                    maze_display = copy.deepcopy(maze_base)
                    for k in results: results[k] = {'cost': '--', 'nodes': '--'}
                    play_sfx('click')

                except ValueError as e:
                    play_sfx('error');
                    show_popup(f"Aviso: {e}")

            if event.button == 1 and mouse_pos[0] <= sidebar_w:
                for algo in ALGORITMOS:
                    if 'rect' in algo and algo['rect'].collidepoint(mouse_pos):
                        play_sfx('click');
                        next_algo_id = algo['id']

    while next_algo_id is not None:
        algo_id = next_algo_id
        next_algo_id = None
        running_algo_id = algo_id
        maze_display = copy.deepcopy(maze_base)
        s_lines = get_safe_size(applied_size)
        algo_dict = next(a for a in ALGORITMOS if a['id'] == algo_id)


        def animar_busca(current_lim=None):
            global skip_anim, next_algo_id
            if skip_anim: return
            current_mouse_pos = pygame.mouse.get_pos()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                speed_slider.handle_event(ev)
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if pygame.Rect(margin + 15, display_h - 140, sidebar_w - (margin * 2) - 30, 40).collidepoint(
                            ev.pos):
                        skip_anim = True;
                        play_sfx('click')
                    elif ev.pos[0] <= sidebar_w:
                        for a in ALGORITMOS:
                            if 'rect' in a and a['rect'].collidepoint(ev.pos):
                                play_sfx('click');
                                next_algo_id = a['id']
                                raise InterromperBusca()

            if current_lim is not None and algo_id == 'ids':
                algo_dict['limit_box'].text = str(current_lim)
                algo_dict['limit_box'].txt_surface = button_font.render(str(current_lim), True, text_dark)

            draw_sidebar(current_mouse_pos, pending_changes, running_algo_id)
            draw_maze()
            pygame.display.flip()
            if speed_slider.val > 0: pygame.time.delay(speed_slider.val)


        try:
            result_search = None
            if algo_dict.get('has_limit') and not algo_dict['limit_box'].text: raise ValueError("Defina um limite")
            if algo_id == 'bfs':
                result_search = np_searcher.breadth_first_search(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                        animar_busca)
            elif algo_id == 'dfs':
                result_search = np_searcher.depth_first_search(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                      animar_busca)
            elif algo_id == 'dls':
                result_search = np_searcher.depth_limited_search(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                        int(algo_dict['limit_box'].text), animar_busca)
            elif algo_id == 'ids':
                result_search = np_searcher.aprof_iterativo_grid(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                        int(algo_dict['limit_box'].text), animar_busca)
            elif algo_id == 'bi':
                result_search = np_searcher.bidirecional_grid(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                      animar_busca)
            elif algo_id == 'ucs':
                result_search = p_searcher.uniform_cost(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                        animar_busca)
            elif algo_id == 'greedy':
                result_search = p_searcher.greedy(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                  animar_busca)
            elif algo_id == 'astar':
                result_search = p_searcher.a_star(applied_start, applied_end, s_lines, s_lines, maze_display,
                                                  animar_busca)

            # TRATAMENTO DE RETORNO ATUALIZADO
            if result_search:
                if isinstance(result_search, tuple):  # Algoritmos com peso retornam tupla
                    path, cost = result_search
                else:
                    path = result_search  # Algoritmos antigos retornam só o path
                    cost = len(path)

                if len(path) > 0:
                    path.pop(0)

                for step in path:
                    if maze_display[step[0]][step[1]] not in [2, 3]: maze_display[step[0]][step[1]] = 5

                results[algo_id]['cost'] = str(cost)
                results[algo_id]['nodes'] = str(sum(row.count(4) for row in maze_display) + len(path))

                play_sfx('success')
                if skip_anim: draw_maze(); pygame.display.flip()

            else:
                # Se caiu aqui, ou o algoritmo não achou caminho, ou ainda não foi implementado!
                play_sfx('error')
                show_popup('Nenhum caminho encontrado ou algoritmo não implementado')

        except InterromperBusca:
            maze_display = copy.deepcopy(maze_base)
            results[algo_id] = {'cost': '--', 'nodes': '--'}
            if next_algo_id == algo_id: next_algo_id = None

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            details = traceback.extract_tb(exc_traceback)[-1]
            error_msg = f"Erro: {e}\nArquivo: {details.filename}\nLinha: {details.lineno}"
            print(error_msg)
            show_popup(f"Erro: {e}")

        finally:
            running_algo_id = None

    draw_sidebar(mouse_pos, pending_changes, running_algo_id)
    draw_maze()
    pygame.display.flip()

pygame.quit()
sys.exit()