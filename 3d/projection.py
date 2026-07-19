import numpy as np
import math

class projection:
    def __init__(self,render):
        NEAR = render.camera.nearPlane
        FAR = render.camera.farPlane
        RIGHT = math.tan(render.camera.horizontalFOV / 2)
        LEFT = -RIGHT
        TOP = math.tan(render.camera.verticalFOV / 2)
        BOTTOM = -TOP

        # use the projection matrix formulas
        m00 = 2 / (RIGHT - LEFT)
        m11 = 2 / (TOP - BOTTOM)
        m22 = (FAR + NEAR) / (FAR - NEAR)
        m32 = -2 * NEAR * FAR / (FAR - NEAR)
        self.projectionMatrix = np.array([
            [m00,0,0,0],
            [0,m11,0,0],
            [0,0,m22,1],
            [0,0,m32,0]
        ])

        HW,HH = render.H_WIDTH, render.H_HEIGHT
        self.toScreenMatrix = np.array([
            [HW,0,0,0],
            [0,-HH,0,0],
            [0,0,1,0],
            [HW,HH,0,1] 
        ])