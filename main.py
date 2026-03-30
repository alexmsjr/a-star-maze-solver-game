import pygame
import sys

# FIXING AUDIO DELAY BEFORE INIT (Small buffer)
pygame.mixer.pre_init(44100, -16, 2, 512)
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

transparent = (0,0,0,0)

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

#### MAIN DIV ####
level_div_main_l = (cell_size * lines)  # maze size
level_div_main_h = (cell_size * columns) + 200  # maze size + buttons space

level_div_main_pos_x = (display_l // 2) - (level_div_main_l // 2)  # maze centralize
level_div_main_pos_y = (display_h // 2) - (level_div_main_h // 2)  # maze centralize

# TOP BAR BUTTONS (Local Coordinates inside the Div)
back_button = pygame.Rect(0, 0, 140, 40)
title_bar = pygame.Rect(150, 0, 300, 40)
help_button = pygame.Rect(460, 0, 140, 40)


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

    # Help Button (With interactive hover)
    if help_button.collidepoint(mouse_local_x, mouse_local_y):
        pygame.draw.rect(level_div_main, dark_gray, help_button, border_radius=12)
        help_text = default_font.render("help", True, white)
    else:
        pygame.draw.rect(level_div_main, dark_gray, help_button, border_radius=12)
        help_text = default_font.render("help", True, text_gray)

    level_div_main.blit(help_text, help_text.get_rect(center=help_button.center))

    # BLIT MAIN DIV TO DISPLAY (Must be before the maze, otherwise it covers the maze)
    display.blit(level_div_main, (level_div_main_pos_x, level_div_main_pos_y))

    # --- MAZE ---
    """
    maze_pattern = [
        # Row 0 (Entry at 19)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1],
        # Rows 1-2 (Open hall)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        # Rows 3-5 (Pillars area)
        [1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0,
         0, 0, 1],
        [1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0,
         0, 0, 1],
        [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0,
         0, 0, 1],
        # Rows 6-7 (Wall separating top and middle arenas - with 2 gates)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1],
        # Rows 8-11 (Middle Open Arena 1)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        # Rows 12-14 (Wall blocks breaking the center)
        [1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0,
         0, 0, 1],
        # Rows 15-17 (Middle Open Arena 2)
        [1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        # Rows 18-19 (Horizontal Separator 2 - with 2 gates)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1],
        # Row 20 (Open horizontal hallway bridging arenas and the labyrinth below)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 1],
        # Row 21 (Labyrinth Starts - 3 Entrances at columns 1, 19, and 38)
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
         1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,
         1, 0, 1],
        # Row 37 (Massive horizontal hallway merging labyrinth paths to the center)
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 1],
        # Row 38 (Final bottleneck)
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 0, 1],
        # Row 39 (Exit at 19)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1]
    ]
    """
    maze_pattern = [
        [2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 3]
    ]
    for line in range(lines):
        for column in range(columns):
            cell = maze_pattern[line][column]

            cell_pos_x = (column * cell_size) + level_div_main_pos_x
            # Adding 80 to distance the maze from the top bar
            cell_pos_y = (line * cell_size) + level_div_main_pos_y + 60

            cell_rect = pygame.Rect(cell_pos_x, cell_pos_y, cell_size, cell_size)

            if cell == 1:
                pygame.draw.rect(display, gray, cell_rect)
            elif cell == 0:
                pygame.draw.rect(display, white, cell_rect)
            elif cell == 2: # begin
                pygame.draw.rect(display, green, cell_rect)
            elif cell == 3:
                pygame.draw.rect(display, red, cell_rect)


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

                # Help button check
                if help_button.collidepoint(mouse_local_x, mouse_local_y):
                    #if confirm_sound: confirm_sound.play()
                    print('help button clicked')

    # RENDER CORRECT SCREEN BASED ON 'screen' VARIABLE
    if screen == 0:
        menu_screen()
    elif screen == 1:
        level_one()

    pygame.display.flip()

pygame.quit()
sys.exit()