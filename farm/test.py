import pygame 

top = pygame.image.load("assets\\topMillstone.png")
bottom = pygame.image.load("assets\\bottomMillstone.png")

x,y = 0,0

surf = pygame.Surface((80,80))

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        x += 1
    if keys[pygame.K_LEFT]:
        x -= 1
    if keys[pygame.K_UP]:
        y -= 1
    if keys[pygame.K_DOWN]:
        y += 1
    if keys[pygame.K_s]:
        pygame.image.save(surf, "ssurf.png")

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE
    surf.fill("purple")
    surf.blit(bottom, (x,y))
    surf.blit(top,(0,0))
    screen.blit(surf,(0,0))


    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()