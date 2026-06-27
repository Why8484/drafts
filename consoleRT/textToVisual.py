# Example file showing a basic pygame "game loop"
import pygame
import ast

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

filePath = input("file path: ")

with open(filePath, "r",encoding="utf-8") as f:
    content = f.read().splitlines()

realLists = []

for line in content:
    realLst = ast.literal_eval(line)
    realLists.append(realLst)

offsetX = offsetY = 100

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    for y,xs in enumerate(realLists):
        for x,tx in enumerate(xs):
            pygame.draw.rect(screen,tx,(x+offsetX,y+offsetY,1,1))
    # RENDER YOUR GAME HERE
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
