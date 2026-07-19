import math
import numpy as np

def translate(pos):
    tx,ty,tz = pos
    return np.array([
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [tx,ty,tz,1]
    ])

def rotateX(angle):
    return np.array([
        [1,0,0,0],
        [0,math.cos(angle),math.sin(angle),0],
        [0,-math.sin(angle), math.cos(angle), 0],
        [0,0,0,1]
    ])

def rotateY(angle):
    return np.array([
        [math.cos(angle),0,-math.sin(angle),0],
        [0,1,0,0],
        [math.sin(angle),0,math.cos(angle),0],
        [0,0,0,1]
    ])

def rotateZ(angle):
    return np.array([
        [math.cos(angle),math.sin(angle),0,0],
        [-math.sin(angle),math.cos(angle),0,0],
        [0,0,1,0],
        [0,0,0,1]
    ])

def scale(factor):
    return np.array([
        [factor,0,0,0],
        [0,factor,0,0],
        [0,0,factor,0],
        [0,0,0,1]
    ])