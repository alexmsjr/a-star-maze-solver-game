import pygame
import sys

pygame.init()

### DISPLAY SETUP:
display_h = 900 # screen High
display_l = 700 # screen Length
display = pygame.display.set_mode((display_l, display_h))
pygame.display.set_caption("oLabirinto")

### FONTS:
title_font = pygame.font.Font('fonts\DOS.ttf', 73)
button_font = pygame.font.SysFont("terminal", 36)

### COLORS:
white = (255,255,255)
black = (0,0,0)
gray = (200,200,200)
green = (46,135,10)

############################################## SCREENS #################################################

# Every menu screen have an id, a number to use on main loop.
# For example, menu screen is 0.

############################################## MENU(0) #################################################
menu_background = pygame.image.load('img\main.webp')
menu_background = pygame.transform.scale(menu_background, (display_l, display_h))
menu_background.set_alpha(5)
title_text = title_font.render("oLabirinto", True, white)

# BOTTOM DIV
div_length = display_l * 0.6
div_height = (70 * 3)# (buttons size+10 of margin) * number of buttons + 10 for margins
div_pos_x = (display_l // 2) - (div_length // 2)
div_pos_y = (display_h // 2) - (div_height // 2)

# BUTTONS (posX, posY, length, height)
start_button = pygame.Rect(5, 5, (div_length-10), 60)
option_button = pygame.Rect(5,75, (div_length-10), 60)
quit_button = pygame.Rect(5,145, (div_length-10), 60)

def menu_screen():
    # id 0
    display.blit(menu_background, (0, 0)) # place background

    # BUTTONS DIV
    buttons_div = pygame.Surface((div_length,div_height), pygame.SRCALPHA)
    buttons_div.fill((0,255,0,0))

    # TITLE
    display.blit(title_text, (150,150))

    # START BUTTON
    pygame.draw.rect(buttons_div, white, start_button, border_radius=8)
    text_start_button = button_font.render("Jogar", True, black)
    rect_start_button = text_start_button.get_rect(center=start_button.center)
    buttons_div.blit(text_start_button, rect_start_button)

    # OPTION BUTTON
    pygame.draw.rect(buttons_div, white, option_button, border_radius=8)
    text_option_button = button_font.render("Opções", True, black)
    rect_option_button = text_option_button.get_rect(center=option_button.center)
    buttons_div.blit(text_option_button, rect_option_button)

    # QUIT BUTTON
    pygame.draw.rect(buttons_div, white, quit_button, border_radius=8)
    text_quit_button = button_font.render("Sair", True, black)
    rect_quit_button = text_quit_button.get_rect(center=quit_button.center)
    buttons_div.blit(text_quit_button, rect_quit_button)

    display.blit(buttons_div, (div_pos_x, div_pos_y))



############################################## LEVEL(1) #################################################

# MAZE CONFIG
lines = 10
columns = lines
cell_size = (600/lines)  # pixels

# MAIN DIV ###
# maze size
level_div_main_l = (cell_size * lines)
# maze size + buttons space
level_div_main_h = (cell_size * columns) + 200
level_div_main_pos_x = (display_l // 2) - (level_div_main_l // 2)
level_div_main_pos_y = (display_h // 2) - (level_div_main_h // 2)

def level_one():
    # id 1
    display.fill(0)

    # BOTTOM DIV
    level_div_main = pygame.Surface((level_div_main_l, level_div_main_h), pygame.SRCALPHA)
    level_div_main.fill((255,0,0,50))
    display.blit(level_div_main, (level_div_main_pos_x, level_div_main_pos_y))

    # Maze pattern
    matriz_labirinto = [
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    ]

    # Drawing the maze
    for line in range(lines):
        for column in range(columns):
            # Descobre se é caminho (0) ou parede (1)
            cell = matriz_labirinto[line][column]

            # Calcula o X e Y na tela, somando o offset para ficar centralizado
            cell_pos_x = (column * cell_size) + level_div_main_pos_x
            cell_pos_y = (line * cell_size) + level_div_main_pos_y

            # Cria a forma matemática do quadradinho
            rect_celula = pygame.Rect(cell_pos_x, cell_pos_y, cell_size, cell_size)

            # Pinta de acordo com o valor lógico
            if cell == 1:
                pygame.draw.rect(display, gray, rect_celula)  # gray wall
            else:
               pygame.draw.rect(display, white, rect_celula)  # white path


#============================================ MAIN LOOP ==================================================
screen = 0
running = True
while running:
    for event in pygame.event.get():
        # CLOSE BUTTON(X)
        if event.type == pygame.QUIT:
            running = False

        ### MENU BUTTONS
        if screen == 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos_x, pos_y = event.pos
                mouse_local_pos = (pos_x-div_pos_x,pos_y-div_pos_y)

                if event.button == 1:
                    if start_button.collidepoint(mouse_local_pos):
                        screen = 1

    # MENU(0) SCREEN
    if screen == 0:
        menu_screen()

    # LEVEL ONE
    if screen == 1:
        level_one()

    pygame.display.flip()