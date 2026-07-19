import pygame
from matrices import *

class object3D:
    def __init__(self,render):
        self.render = render
        self.vertexes = np.array([(0,0,0,1), (0,1,0,1), (1,1,0,1), (1,0,0,1),
                                  (0,0,1,1), (0,1,1,1), (1,1,1,1), (1,0,1,1)])

        self.faces = np.array([(0,1,2,3), (0,1,5,4), (0,4,7,3), (5,6,7,4),(1,5,6,2),(2,6,7,3)])
    
    def draw(self):
        self.screenProjection()
    
    def screenProjection(self):
        vertexes = self.vertexes @ self.render.camera.cameraMatrix()
        vertexes = vertexes @ self.render.projection.projectionMatrix
        vertexes /= vertexes[:, -1].reshape(-1,1)
        vertexes[(vertexes > 1) | (vertexes < -1)] = 0
        vertexes @= self.render.projection.toScreenMatrix
        vertexes = vertexes[:,:2]

        for face in self.faces:
            polygon = vertexes[face]
            if not np.any((polygon == self.render.H_WIDTH) | (polygon == self.render.H_HEIGHT)):
                pygame.draw.polygon(self.render.screen, pygame.Color("orange"), polygon, 3)
        
        for vertex in vertexes:
            if not np.any((vertex == self.render.H_WIDTH) | (vertex == self.render.H_HEIGHT)):
                pygame.draw.circle(self.render.screen, pygame.Color("black"), vertex, 6)

    def translate(self, pos):
        self.vertexes = self.vertexes @ translate(pos)
    
    def scale(self,scaleBy):
        self.vertexes = self.vertexes @ scale(scaleBy)
    
    def rotateX(self, angle):
        self.vertexes = self.vertexes @ rotateX(angle)
    
    def rotateY(self,angle):
        self.vertexes = self.vertexes @ rotateY(angle)
    
    def rotateZ(self,angle):
        self.vertexes = self.vertexes @ rotateZ(angle)