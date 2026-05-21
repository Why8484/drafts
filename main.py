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
        self.baseSize = radius
        self.color = color
        if surface is None:
            surface = self.createSurface()
        self.surface = surface
    def createSurface (self):
        surface = pygame.Surface((self.radius*2,self.radius*2),pygame.SRCALPHA)
        pygame.draw.circle(surface,self.color, (self.radius,self.radius),self.radius)
        return surface
    def draw (self):
        screen.blit(self.surface, (self.x,self.y))
    def move(self):
        if pygame.mouse.get_pressed()[0]:    
            pos = pygame.mouse.get_pos()
            self.x = pos[0] - self.radius
            self.y = pos[1] - self.radius
        elif pygame.mouse.get_pressed()[2]:
            self.radius += 5
            self.surface = self.createSurface()
        elif pygame.mouse.get_pressed()[1]:
            self.color = "blue"
            self.surface = self.createSurface()
        else:
            self.color = "red"
            if self.radius > self.baseSize:    
                self.radius -= 5
            self.surface = self.createSurface()
        

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