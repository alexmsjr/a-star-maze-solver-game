import pygame
import sys
import AuxFunctions
from NPsearch import NPsearch

np_searcher = NPsearch()

pygame.init()

### DISPLAY SETUP:
display_h = 900  # screen High
display_l = 700  # screen Length
display = pygame.display.set_mode((display_l, display_h))
pygame.display.set_caption("oLabirinto")

### FONTS:
# Make sure font paths are correct in your PC!
title_font = pygame.font.Font(r'fonts\DOS.ttf', 73)
button_font = pygame.font.SysFont("terminal", 36)
default_font = pygame.font.SysFont("terminal", 25)

### COLORS:
back_gray = (50, 52, 55)
dark_gray = (40,42,45)
gray = (90, 90, 90)
text_gray = (120,120,120)

yellow = (226,183,20)
white = (255,255,255)
black = (0,0,0)
green = (46,135,10)
maze_gray = (200,200,200)
red = (255,0,0)
blue = (0,0,255)

transparent = (0,0,0,0)

############################################## MESSAGE POP-UP #################################################
def show_popup(message):
    # 1. Cria a camada de escurecimento (Dim Overlay)
    # Surface do tamanho da tela com suporte a canal Alpha (Transparência)
    overlay = pygame.Surface((display_l, display_h), pygame.SRCALPHA)
    # Preenche com preto (0,0,0) e alpha de 180 (vai de 0 a 255)
    overlay.fill((0, 0, 0, 180))
    display.blit(overlay, (0, 0))  # Desenha por cima de todo o labirinto

    # 2. Configurações de tamanho e posição da caixa
    popup_w = 400
    popup_h = 200
    popup_x = (display_l // 2) - (popup_w // 2)
    popup_y = (display_h // 2) - (popup_h // 2)
    popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)

    # 3. Desenha a caixa do popup
    pygame.draw.rect(display, dark_gray, popup_rect, border_radius=15)

    # 4. Desenha a mensagem principal (Mudado para button_font - tamanho menor)
    text_surf = default_font.render(message, True, yellow)
    text_rect = text_surf.get_rect(center=(popup_rect.centerx, popup_rect.centery - 20))
    display.blit(text_surf, text_rect)

    # 5. Desenha o aviso de como fechar
    sub_text = default_font.render("Click anywhere to close", True, text_gray)
    sub_rect = sub_text.get_rect(center=(popup_rect.centerx, popup_rect.bottom - 30))
    display.blit(sub_text, sub_rect)

    # 6. Atualiza a tela UMA VEZ com o popup montado
    pygame.display.flip()

    # 7. Loop de pausa esperando o usuário clicar
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Fecha o popup com clique ou tecla
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

    # Quando o loop acabar, o jogo volta a rodar normalmente no while principal.
    # O labirinto será redesenhado por cima no próximo frame, apagando o popup.

############################################## MENU(0) #################################################
# TITLE
main_title_text = title_font.render("oLabirinto", True, white)

# MENU BUTTONS CONFIG (Global Screen Coordinates)
button_w = (display_l * 0.6) - 10
button_h = 60
button_x = (display_l // 2) - (button_w // 2)

total_buttons_h = (70 * 3)
start_y = (display_h // 2) - (total_buttons_h // 2)

# BUTTONS (posX, posY, length, height)
start_button = pygame.Rect(button_x, start_y + 5, button_w, button_h)
option_button = pygame.Rect(button_x, start_y + 75, button_w, button_h)
quit_button = pygame.Rect(button_x, start_y + 145, button_w, button_h)

def menu_screen():
    # id 0
    display.fill(black)

    # TITLE
    display.blit(main_title_text, (150, 150))

    # GET GLOBAL MOUSE POS
    mouse_global_pos = pygame.mouse.get_pos()

    # START BUTTON
    if start_button.collidepoint(mouse_global_pos):
        pygame.draw.rect(display, gray, start_button, border_radius=8)
        start_text = button_font.render("start", True, white)
    else:
        pygame.draw.rect(display, white, start_button, border_radius=8)
        start_text = button_font.render("start", True, black)
    display.blit(start_text, start_text.get_rect(center=start_button.center))

    # OPTION BUTTON
    if option_button.collidepoint(mouse_global_pos):
        pygame.draw.rect(display, gray, option_button, border_radius=8)
        option_text = button_font.render("options", True, white)
    else:
        pygame.draw.rect(display, white, option_button, border_radius=8)
        option_text = button_font.render("options", True, black)
    display.blit(option_text, option_text.get_rect(center=option_button.center))

    # QUIT BUTTON
    if quit_button.collidepoint(mouse_global_pos):
        pygame.draw.rect(display, gray, quit_button, border_radius=8)
        quit_text = button_font.render("quit", True, white)
    else:
        pygame.draw.rect(display, white, quit_button, border_radius=8)
        quit_text = button_font.render("quit", True, black)
    display.blit(quit_text, quit_text.get_rect(center=quit_button.center))


############################################## LEVEL(1) #################################################

# MAZE CONFIG
lines = 20
columns = lines
cell_size = (600 / lines)  # pixels

# FIRST MAZE PATTERN
maze_pattern, maze_start, maze_end = AuxFunctions.gen_randon_maze(lines,lines,100)

#### MAIN DIV ####
level_div_main_l = (cell_size * lines)  # maze size
level_div_main_h = (cell_size * columns) + 200  # maze size + buttons space

level_div_main_pos_x = (display_l // 2) - (level_div_main_l // 2)  # maze centralize
level_div_main_pos_y = (display_h // 2) - (level_div_main_h // 2)  # maze centralize

# TOP BAR BUTTONS (Local Coordinates inside the Div)
back_button = pygame.Rect(0, 0, 140, 40)
title_bar = pygame.Rect(150, 0, 300, 40)
gen_random_maze = pygame.Rect(460, 0, 140, 40)
breadth_first = pygame.Rect(0, 680, 140, 40)
depth_first = pygame.Rect(150, 680, 140, 40)


def level_one():
    # id 1
    display.fill(back_gray)

    # MAIN DIV LAYER
    level_div_main = pygame.Surface((level_div_main_l, level_div_main_h), pygame.SRCALPHA)
    level_div_main.fill((0, 0, 0, 0))

    # MOUSE TRANSLATION FOR DIV HOVER
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_local_x = mouse_x - level_div_main_pos_x
    mouse_local_y = mouse_y - level_div_main_pos_y

    # --- TOP BAR ---
    # Back Button
    if back_button.collidepoint(mouse_local_x, mouse_local_y):
        pygame.draw.rect(level_div_main, dark_gray, back_button, border_radius=12)
        back_text = default_font.render("back", True, white)
        level_div_main.blit(back_text, back_text.get_rect(center=back_button.center))
    else:
        pygame.draw.rect(level_div_main, dark_gray, back_button, border_radius=12)
        back_text = default_font.render("back", True, text_gray)
        level_div_main.blit(back_text, back_text.get_rect(center=back_button.center))

    # Title Bar
    pygame.draw.rect(level_div_main, dark_gray, title_bar, border_radius=12)
    level_title_text = default_font.render("level 1", True, yellow)
    level_div_main.blit(level_title_text, level_title_text.get_rect(center=title_bar.center))

    # gen_random_maze button
    if(gen_random_maze.collidepoint(mouse_local_x, mouse_local_y)):
        pygame.draw.rect(level_div_main, dark_gray, gen_random_maze, border_radius=12)
        gen_random_maze_font = default_font.render("random maze", True, white)
    else:
        pygame.draw.rect(level_div_main, dark_gray, gen_random_maze, border_radius=12)
        gen_random_maze_font = default_font.render("random maze", True, text_gray)
    level_div_main.blit(gen_random_maze_font, gen_random_maze_font.get_rect(center=gen_random_maze.center))

    # amplitude button
    if(breadth_first.collidepoint(mouse_local_x, mouse_local_y)):
        pygame.draw.rect(level_div_main, dark_gray, breadth_first, border_radius=12)
        breadth_first_text = default_font.render("breadth first", True, white)
    else:
        pygame.draw.rect(level_div_main, dark_gray, breadth_first, border_radius=12)
        breadth_first_text = default_font.render("breadth first", True, text_gray)
    level_div_main.blit(breadth_first_text, breadth_first_text.get_rect(center=breadth_first.center))

    # profundidade button
    if(depth_first.collidepoint(mouse_local_x, mouse_local_y)):
        pygame.draw.rect(level_div_main, dark_gray, depth_first, border_radius=12)
        depth_first_text = default_font.render("depth first", True, white)
    else:
        pygame.draw.rect(level_div_main, dark_gray, depth_first, border_radius=12)
        depth_first_text = default_font.render("depth first", True, text_gray)
    level_div_main.blit(depth_first_text, depth_first_text.get_rect(center=depth_first.center))

    # BLIT MAIN DIV TO DISPLAY (Must be before the maze, otherwise it covers the maze)
    display.blit(level_div_main, (level_div_main_pos_x, level_div_main_pos_y))

    for line in range(lines):
        for column in range(columns):
            cell = maze_pattern[line][column]

            cell_pos_x = (column * cell_size) + level_div_main_pos_x

            cell_pos_y = (line * cell_size) + level_div_main_pos_y + 60

            cell_rect = pygame.Rect(cell_pos_x, cell_pos_y, cell_size, cell_size)

            if cell == 1: # wall
                pygame.draw.rect(display, gray, cell_rect)
            elif cell == 0: # free path
                pygame.draw.rect(display, white, cell_rect)
            elif cell == 2: # start
                pygame.draw.rect(display, green, cell_rect)
            elif cell == 3: # end
                pygame.draw.rect(display, red, cell_rect)
            elif cell == 4: # explored path
                pygame.draw.rect(display, (200,200,200), cell_rect)
            elif cell == 5: # explored path
                pygame.draw.rect(display, (150,200,150), cell_rect)



# ============================================ MAIN LOOP ==================================================

# Load sound safely
try:
    confirm_sound = pygame.mixer.Sound(r'.\sounds\confirm_sfx.ogg')
except FileNotFoundError:
    confirm_sound = None

screen = 0
running = True
while running:

    for event in pygame.event.get():

        ### CLOSE BUTTON(X)
        if event.type == pygame.QUIT:
            running = False

        ### MOUSE CLICKS
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # MENU CLICKS (screen 0)
            if screen == 0:
                if start_button.collidepoint(event.pos):
                    if confirm_sound: confirm_sound.play()
                    screen = 1  # Go to game

                elif option_button.collidepoint(event.pos):
                    #if confirm_sound: confirm_sound.play()
                    print('option button clicked')

                elif quit_button.collidepoint(event.pos):
                    running = False  # Quit game

            # LEVEL 1 CLICKS (screen 1)
            elif screen == 1:
                # Translate mouse position to Div coordinates
                mouse_x, mouse_y = event.pos
                mouse_local_x = mouse_x - level_div_main_pos_x
                mouse_local_y = mouse_y - level_div_main_pos_y

                # Back button check
                if back_button.collidepoint(mouse_local_x, mouse_local_y):
                    if confirm_sound: confirm_sound.play()
                    screen = 0  # Back to menu!

                # Generate a new random maze button check
                if gen_random_maze.collidepoint(mouse_local_x, mouse_local_y):
                    maze_pattern, maze_start, maze_end = AuxFunctions.gen_randon_maze(lines,lines,100)

                # breadth_first_search check
                if breadth_first.collidepoint(mouse_local_x, mouse_local_y):
                    # 1. Cria a função que desenha, atualiza e pausa
                    def animar_busca():
                        level_one()  # Redesenha o mapa com os novos '4's
                        pygame.display.flip()  # Atualiza a tela do monitor
                        pygame.time.delay(10//(lines*columns))  # Pausa por 20 milissegundos (ajuste a velocidade aqui!)
                        pygame.event.pump()  # Impede o Windows de achar que o jogo travou


                    # 2. Passa essa função como último parâmetro!
                    path = np_searcher.breadth_first_search(maze_start, maze_end,lines, lines, maze_pattern, animar_busca)
                    path.pop(0)
                    if path != None:
                        for step in range(len(path)-1):
                            cell = path[step]
                            maze_pattern[cell[0]][cell[1]] = 5

                    else:
                        show_popup('Nenhum caminho foi encontrado!')

                # breadth_first_search check
                if depth_first.collidepoint(mouse_local_x, mouse_local_y):
                    # 1. Cria a função que desenha, atualiza e pausa
                    def animar_busca():
                        level_one()  # Redesenha o mapa com os novos '4's
                        pygame.display.flip()  # Atualiza a tela do monitor
                        pygame.time.delay(10)  # Pausa por 20 milissegundos (ajuste a velocidade aqui!)
                        pygame.event.pump()  # Impede o Windows de achar que o jogo travou


                    # 2. Passa essa função como último parâmetro!
                    path = np_searcher.depth_first_search(maze_start, maze_end, lines, lines, maze_pattern, animar_busca)
                    path.pop(0)
                    if path != None:
                        for step in range(len(path)-1):
                            cell = path[step]
                            maze_pattern[cell[0]][cell[1]] = 5


                    else:
                        show_popup('Nenhum caminho foi encontrado!')

    # RENDER CORRECT SCREEN BASED ON 'screen' VARIABLE
    if screen == 0:
        menu_screen()
    elif screen == 1:
        level_one()

    pygame.display.flip()

pygame.quit()
sys.exit()