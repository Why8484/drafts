# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

image = pygame.transform.scale_by(pygame.image.load("assets\\bread.png").convert_alpha(), 4)

alpha = 100
def reset(rectAlpha = 100):
    global surf

    overlay = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    overlay.fill((0, 0, 0, rectAlpha))  # Black with 120/255 opacity (adjust this darkness)

    overlay.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    surf = pygame.Surface((560, 560), flags=pygame.SRCALPHA)
    surf.blit(image, (0, 0))
    surf.blit(overlay, (0, 0))

reset()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN] and alpha > 0:
        alpha -= 1
        reset(alpha)
    if keys[pygame.K_UP] and alpha < 255:
        alpha += 1
        reset(alpha)
    if keys[pygame.K_p]:
        print(alpha)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE
    screen.blit(surf, (200,100))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()