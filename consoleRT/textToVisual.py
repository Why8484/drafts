# Example file showing a basic pygame "game loop"
import pygame
import ast
import os

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

offsetX = offsetY = 100
distanceBetweenImgs = 100
scale = 10

folderMdde = input("use foder mode?(y/n) ") == ("y" or "Y")
if folderMdde:
    folderPath = input("Enter folder path: ")
    realListsLists = []
filePath = input("file path: ")

def openImage (path):
    with open(path, "r",encoding="utf-8") as f:
        content = f.read().splitlines()

    realLists = []

    for line in content:
        realLst = ast.literal_eval(line)
        realLists.append(realLst)
    

    
    return realLists

if folderMdde is False:    
    realLists = openImage(filePath)
else: 
    i = 1
    for fileName in os.listdir(folderPath):
        fileName = os.path.join(folderPath,fileName)
        if fileName.endswith(".txt"):
            realListsLists.append(((openImage(fileName)),offsetX+i*distanceBetweenImgs))
        i += 1




def drawImage(offsetx,offsety,realLsts):
    global offsetX,offsetY,distanceBetweenImgs

    for y,xs in enumerate(realLsts):
        for x,tx in enumerate(xs):
            pygame.draw.rect(screen,tx,(x*scale+offsetx,y*scale+offsety,1*scale,1*scale))
    

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    if not folderMdde:    
        drawImage(offsetX,offsetY,realLists)
    else:
        for realLst,offsets in realListsLists:
            drawImage(offsets,offsetY,realLst)
    # RENDER YOUR GAME HERE
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
