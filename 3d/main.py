# Example file showing a basic pygame "game loop"
import pygame
from object import object3D
from camera import *
from projection import *


class Render:
    def __init__(self):
        # pygame setup
        pygame.init()
        self.RES = self.WIDTH,self.HEIGHT = 1600,900
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2,self.HEIGHT // 2
        self.screen = pygame.display.set_mode(self.RES)
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.createObjects()
    
    def draw(self):
        self.screen.fill(pygame.Color("darkslategray"))
        self.object.draw()

    def createObjects(self):
        self.camera = Camera(self,[0.5,1,-4])
        self.projection = projection(self)
        self.object = object3D(self)
        self.object.translate([0.2,0.4,0.2])
        self.object.rotateY(math.pi / 6)


    def run(self):
        while True:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            self.draw()
            pygame.display.set_caption(str(self.clock.get_fps()))

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.clock.tick(self.FPS)  # limits FPS to 60



if __name__ == "__main__":
    app = Render()
    app.run()

pygame.quit()


