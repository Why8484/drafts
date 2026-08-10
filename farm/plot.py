# Example file showing a basic pygame "game loop"
import pygame
import math

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

data = []

amplitude = 100
timeSpeed = 1

def degToRad(deg):
    return deg*math.pi/180

for i in range(0,360):
    data.append(round(math.tan(degToRad(i)), 3))

def render():
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE
    for x,y in enumerate(data):
        pygame.draw.circle(screen, (0,0,0),(x*timeSpeed,360+y*amplitude),1)

render()
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT]:
        timeSpeed += 0.1
        render()    
    if keys[pygame.K_LEFT]:
        timeSpeed -= 0.1
        render()
    if keys[pygame.K_UP]:
        amplitude += 3
        render()
    if keys[pygame.K_DOWN]:
        amplitude -= 3
        render()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60


print(data)
pygame.quit()