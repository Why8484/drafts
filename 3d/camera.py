from matrices import *
import pygame

class Camera:
    def __init__(self, render, position):
        self.render = render
        self.position = np.array([*position,1.0])
        self.forward = np.array([0,0,1,1])
        self.up = np.array([0,1,0,1])
        self.right = np.array([1,0,0,1])
        self.horizontalFOV = math.pi / 3
        self.verticalFOV = self.horizontalFOV * (render.HEIGHT/render.WIDTH) # calculate vertiocal fov from screen's height tpo width ratio
        self.nearPlane = 0.1
        self.farPlane = 100
    
    def translateMatrix(self):
        x,y,z,w = self.position
        return np.array([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [-x,-y,-z,1]
        ])

    def rotateMatrix(self):
        rightX,rightY,rightZ,w = self.right
        forwardX,forwardY,forwardZ,w = self.forward
        upX,upY,upZ,w = self.up

        return np.array([
            [rightX,forwardX,upX,0],
            [rightY,forwardY,upY,0],
            [rightZ,forwardZ,upZ,0],
            [0,0,0,1]
        ])

    def cameraMatrix(self):
        return self.translateMatrix() @ self.rotateMatrix()