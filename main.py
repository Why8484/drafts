# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

class circle:
    def __init__(self,x,y,radius,color,surface = None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        if surface is None:
            surface = pygame.Surface((radius*2,radius*2))
            pygame.draw.circle(surface,color, (radius,radius),radius)
        self.surface = surface
    def draw (self):
        screen.blit(self.surface, (self.x,self.y))
    def move(self):
        self.x,self.y = pygame.mouse.get_pos() if pygame.mouse.get_pressed()[0] else None

player = circle(100,100,50,"red")

def main():
    global running,screen,clock,player

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")

        # RENDER YOUR GAME HERE
        player.move()
        player.draw()

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
    pygame.quit()

main()