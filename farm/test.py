# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

surf = pygame.Surface((100,40),flags=pygame.SRCALPHA)
surf.fill((0,0,0,0))
pygame.draw.ellipse(surf, (0,0,0,140), (0,0,100,40))
pygame.draw.ellipse(surf, (0,0,0,180), (5,5,90,30))
pygame.draw.ellipse(surf, (0,0,0,200), (10,10,80,20))
pygame.draw.ellipse(surf, (0,0,0,225), (15,15,70,10))
# pygame.draw.ellipse(surf, (0,0,0,240), (20,20,80,20))
# pygame.draw.ellipse(surf, (0,0,0,255), (25,25,70,10))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE
    screen.blit(surf,(100,100))
    pygame.image.save(surf, "assets\\shadow.png")

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()