import pygame
import sys

pygame.init()

### Display Setup ###
displayH = 900 # screen High
displayL = 700 # screen Length
display = pygame.display.set_mode((displayL, displayH))
pygame.display.set_caption("oLabirinto")

### Fonts Setup ###
titleFont = pygame.font.Font('fonts\DOS.ttf',70)
buttonFont = pygame.font.SysFont("terminal", 36)

## Colors
white = (255,255,255)
black = (0,0,0)
gray = (200,200,200)


###### Menu ######
# background setup
background = pygame.image.load('img\main.webp')
background = pygame.transform.scale(background, (displayL, displayH))
background.set_alpha(10)

# text setup
textImg = titleFont.render("oLabirinto",True, white)

## button setup
# dimensions
buttonL = 200
buttonH = 60
# position
pos_x = (displayL // 2) - (buttonL // 2)
pos_y = (displayH // 2) - (buttonH // 2)
startButton = pygame.Rect(pos_x, pos_y, buttonL, buttonH)


screen = 'menu'

###### MAIN LOOP ######
running = True
while running:
    for event in pygame.event.get():
        # close button
        if event.type == pygame.QUIT:
            running = False

        ### MENU BUTTONS
        if screen == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                if startButton.collidepoint(event.pos):
                    screen = 'level1'

        ### LEVEL1 BUTTONS
        elif screen == 'level1':
            print('level1')

    ### MENU SCREEN
    if screen == 'menu':
        display.blit(background, (0, 0))  # draw the background
        display.blit(textImg, (150, 220))  # draw the text

        mousePos = pygame.mouse.get_pos()  # get mouse position

        ## houver effect
        if startButton.collidepoint(mousePos):
            pygame.draw.rect(display, gray, startButton, border_radius=12)
        else:
            pygame.draw.rect(display, white, startButton, border_radius=12)

        ## draw the button
        textButton = buttonFont.render("START", True, black)
        textRect = textButton.get_rect(center=startButton.center)
        display.blit(textButton, textRect)

        pygame.display.flip()  # update the screen

    ### LEVEL1 SCREEN
    if screen == 'level1':
        textImg = titleFont.render('Boa!', True, white)

        display.fill((46,135,10))
        display.blit(textImg, ((displayL //2 ), (displayH // 2)))
        pygame.display.flip()

pygame.quit()