import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

image = pygame.image.load("assets\\images\\sell1Button.png").convert_alpha()
image2 = pygame.image.load("assets\\images\\bread.png").convert_alpha()


def draw_image_on_color(target_surface, image, target_color, dest_pos=(0, 0)):
    """
    Draws `image` onto `target_surface` at `dest_pos`, 
    rendering ONLY on pixels where target_surface matches `target_color`.
    """
    # 1. Create a mask of the exact color area on target_surface
    color_mask = pygame.mask.from_threshold(
        target_surface, target_color, threshold=(1, 1, 1, 255)
    )
    
    # 2. Convert the mask back into a transparent surface (our stencil)
    stencil = color_mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    
    # 3. Prepare a copy of the image cropped/fitted to the target dimensions
    clipped_image = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    clipped_image.blit(image, (0, 0))
    
    # 4. Multiply stencil with image: keeps image pixels only where stencil is white
    clipped_image.blit(stencil, (-dest_pos[0], -dest_pos[1]), special_flags=pygame.BLEND_RGBA_MULT)
    
    # 5. Draw the masked result onto the main target surface
    target_surface.blit(clipped_image, dest_pos)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    # RENDER YOUR GAME HERE
    draw_image_on_color(image, image2, (26, 35, 126), (40, 40))
    screen.blit(image, (100,100))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()