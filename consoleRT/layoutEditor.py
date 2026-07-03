# Example file showing a basic pygame "game loop"
import pygame
import ast

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

scale = 10
cellSize = 6*scale
pos = pygame.mouse.get_pos()
following = None
buttons = []
entities = []
blocks = []
lines = []
isErasing = False
rectStart = None
rectEnd = None
lastButton = None
drawingRect =False
canPrint = True
font = pygame.font.SysFont("comicsansms",22)



def loadImage(path):
    return pygame.transform.scale_by(pygame.image.load(path).convert(),scale)

def getBlockFromPos(gx,gy):
    for bl in blocks:
        if bl.x == gx and bl.y == gy:
            if bl.name is None:
                bl.name = "air"
            return bl.name

dirtImage = loadImage(r"sprites\dirt\dirt.png")
grassImage = loadImage(r"sprites\grass\grass.png")
woodImage = loadImage(r"sprites\wood\wood.png")
leavesImage = loadImage(r"sprites\leaves\leaves.png")
eraseImage = loadImage(r"sprites\erase.png")
blackStone = loadImage(r"sprites\stone\blackStone.png")
blueStone = loadImage(r"sprites\stone\blueStone.png")
orangeStone = loadImage(r"sprites\stone\orangeStone.png")
whiteStone = loadImage(r"sprites\stone\whiteStone.png")


printList = []

dct = {
    dirtImage: "dirt",
    grassImage: "grass",
    woodImage: "wood",
    leavesImage: "leaves",
    blueStone: "blue stone",
    orangeStone: "orange stone",
    whiteStone: "white stone",
    blackStone: "black stone",
}

reverseDct = {v:k for k,v in dct.items()}

class block:
    def __init__(self,x,y,width,height,img):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = img
        for image,name in dct.items():
            if image == self.img:
                self.name = name
        entities.append(self)
        blocks.append(self)
    def snapToGrid(self):
        self.x = self.x//cellSize*cellSize
        self.y = self.y//cellSize*cellSize
    def getRect(self):
        return pygame.rect.Rect(self.x,self.y,self.width,self.height)

class button(block):
    def __init__(self, x, y, width, height, img):
        super().__init__(x, y, width, height, img)
        buttons.append(self)
        blocks.remove(self)
    def onPress(self):
        global following,isErasing


        isErasing = False
        following = block(pos[0],pos[1],cellSize,cellSize,self.img)

i = 0
for img,name in dct.items():
    button(1280-60,i,cellSize,cellSize,img)
    i += 100
# dirtButton = button(1280-60,0,cellSize,cellSize,dirtImage)
# grassButton = button(1280-60,100,cellSize,cellSize,grassImage)
# woodButton = button(1280-60,200,cellSize,cellSize,woodImage)
# leavesButton = button(1280-60,300,cellSize,cellSize,leavesImage)

def write(text,x,y):
    surf = font.render(text,True,"black")
    newBlock = block(x,y,cellSize,cellSize,surf)
    blocks.remove(newBlock)

for h in range(1,9):
    write(str(h),0,(60*(h-1))+12)
    lines.append((0,60*h,1280,60*h))

for w in range(1,17):
    write(str(w),60*w+12,60*8)
    lines.append((60*w,0,60*w,720))

lines.append((60*17,0,60*17,720))
    

def erase_(NoErasers = []):
    global pos

    for bl in blocks:
        if bl.getRect().collidepoint(pos[0],pos[1]) and bl not in NoErasers:
            blocks.remove(bl)
            entities.remove(bl)
            del bl

def eraseOnPress():
    global isErasing

    isErasing = True


eraseButton = button(1280-60,720-60,cellSize,cellSize,eraseImage)
eraseButton.onPress = eraseOnPress

canScrollAgain = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pos = pygame.mouse.get_pos()
    mouse = pygame.mouse.get_pressed(5)
    keys = pygame.key.get_pressed()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    if mouse[0]:
        if isErasing:
            erase_()
        if following is not None:
            erase_([following])
            following = None

        for b in buttons:
            b:button
            if b.getRect().collidepoint(pos[0],pos[1]):
                lastButton = b
                b.onPress()
    if mouse[1]:
        if isErasing:
            erase_()
        if following is not None:
            erase_([following])
            following = block(following.x,following.y,following.width,following.height,following.img)
    if mouse[2]:
        x,y = pos
        x = x//cellSize*cellSize
        y = y//cellSize*cellSize
        if not drawingRect:    
            rectStart = [x,y]
        drawingRect = True
    elif not mouse[2] and drawingRect:
        xe,ye = pos
        xe = xe //cellSize*cellSize
        ye = ye //cellSize*cellSize
        rectEnd = [xe,ye]
        following = None
        drawingRect = False
        if rectEnd[1] == rectStart[1]:
            rectEnd[1] += cellSize
        if rectStart[0] == rectStart[0]:
            rectEnd[0] += cellSize
        for sy in range(rectStart[1],rectEnd[1],cellSize):
            for sx in range(rectStart[0],rectEnd[0],cellSize):
                block(sx,sy,cellSize,cellSize,lastButton.img)
    
    if mouse[4] and canScrollAgain:
        for bl in blocks[:]:
            if not 0 < bl.x < 16*cellSize and not 0 < bl.y < 8*cellSize:
                blocks.remove(bl)
        for b in buttons:
            b.y -= 500
            canScrollAgain = False
            eraseButton.y = 720-60
    
    if mouse[3] and canScrollAgain:
        for bl in blocks[:]:
            if not 0 < bl.x < 16*cellSize and not 0 < bl.y < 8*cellSize:
                blocks.remove(bl)
        for b in buttons:
            b.y += 500
            canScrollAgain = False
            eraseButton.y = 720-60
    
    if not any(mouse):
        canScrollAgain = True

    
    if keys[pygame.K_c]:
        if following is not None:
            blocks.remove(following)
            entities.remove(following)
            following = None
    if keys[pygame.K_e]:
        isErasing = True
    if keys[pygame.K_p] and canPrint:
        printList = []
        for y in range(8):    
            for x in range(1,17):
                printList.append(getBlockFromPos(x*cellSize,y*cellSize))
        printList.pop(0)
        print(printList,len(printList))
        with open("layout","w") as l:
            l.write(str(printList))
        canPrint = False
    if keys[pygame.K_l]:
        layout = ast.literal_eval(input("paste layout: "))
        print(layout)
        for i,bl in enumerate(layout):
            if bl is not None:
                block(divmod(i,16)[1]+cellSize,divmod(i,16)[0],cellSize,cellSize,reverseDct[bl])

    
    if not any(keys):
        canPrint = True


    if following is not None:    
        following.x,following.y = pos
    for bl in blocks:
        bl:block
        bl.snapToGrid()

    # RENDER YOUR GAME HERE
    for ent in entities:
        screen.blit(ent.img,(ent.x,ent.y))
    for l in lines:
        x1,y1,x2,y2 = l
        pygame.draw.aaline(screen,"black",(x1,y1),(x2,y2))
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()