import os
import time
import keyboard
from keyboard._keyboard_event import KEY_DOWN,KEY_UP
from math import ceil
from layouts import *
from pynput.mouse import *
import pygetwindow
    

symbols:list = []
objects = []
colliders = []
items = []
blocks = []
objectLists = [objects,colliders,items,blocks]

WIDTH = 192
GAME_WIDTH = 96
HEIGHT = 48   
BLOCK_SIZE = 6
GRID_WIDTH = 16
GRID_HEIGHT= 8
MIN_INTENSITY = 0
GRAVITY = 0.3
updateFrame = True
startGravity = True


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def isBetween(val, min,max):
    if min < val < max:
        return True
    return False

def inclusiveIsBetween(val,min,max):
    if min <= val <= max:
        return True
    return False

def getPointsFromLine(x1,y1,x2,y2):
    # for horizontal lines
    def getPointsFromLineH(x1,y1,x2,y2):
        # output list
        pixels = []

        # swap values if endX is greater than startX
        if x1 > x2:
            x1,x2 = x2,x1
            y1,y2 = y2,y1
        
        # compute deltas
        dx = x2-x1
        dy = y2-y1

        # factor for y if line is negative
        yFactor = -1 if dy < 0 else 1
        dy *= yFactor

        # check if dx is not 0 to avoid division by zero
        if dx != 0:

            # create a variable that starts at initial y
            yCurrent = y1

            # current y directly on the line(it's initial version)
            pixelCurrentY = 2*dy - dx

            # iterate delta x to get it's evry part incremented by 1
            for dxPart in range(dx+1):

                # append needed pixel to output
                pixels.append((x1+dxPart,yCurrent))

                # incerement current Y if incremented is nearer to the line
                if pixelCurrentY >= 0:
                    yCurrent += yFactor
                    pixelCurrentY -= 2*dx
                
                # do this anyway(move pixel current linewise)
                pixelCurrentY += 2*dy
        
        # return
        return pixels

    # for vertical lines
    def getPointsFromLineV(x1,y1,x2,y2):
        # for explains look into getPointsFromLineH (it's the same but with swaped x and y)

        pixels = []
        if y1 > y2:
            x1,x2 = x2,x1
            y1,y2 = y2,y1
        
        dx = x2-x1
        dy = y2-y1

        yFactor = -1 if dx < 0 else 1
        dx *= yFactor

        if dy != 0:
            xCurrent = x1
            pixelCurrentX = 2*dx - dy
            for dyPart in range(dy+1):
                pixels.append((xCurrent,y1+dyPart))
                if pixelCurrentX >= 0:
                    xCurrent += yFactor
                    pixelCurrentX -= 2*dy
                pixelCurrentX += 2*dx
        return pixels
    
    # detect whether the line is vertical or horizontal
    x1 = round(x1)
    y1 = round(y1)
    x2 = round(x2)
    y2 = round(y2)
    
    if abs(x1-x2) > abs(y1-y2):
        return getPointsFromLineH(x1,y1,x2,y2)
    return getPointsFromLineV(x1,y1,x2,y2)

class window:
    @classmethod
    def updateSpecs(cls):
        cls.win = pygetwindow.getActiveWindow()
        cls.size = os.get_terminal_size()
        cls.collumns,cls.rows = cls.size
        cls.x = cls.win.left
        cls.y = cls.win.top
        cls.width = cls.win.width
        cls.height = cls.win.height
        cls.fontWidth = cls.width/cls.collumns
        cls.fontHeight = cls.height/cls.rows
    @classmethod
    def pxToChars(cls,xpx,ypx):
        window.updateSpecs()
        if not (isBetween(xpx,cls.x,cls.x+cls.width) and isBetween(ypx,cls.y,cls.y+cls.height)):
            return 0,0
        inWindowX = xpx - cls.x
        inWindowY = ypx - cls.y
        charX = inWindowX // cls.fontWidth
        charY = inWindowY // cls.fontHeight
        return charX,charY


# time.sleep(0.5)
window.updateSpecs()

class COLORS:
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"
    
    RESET   = "\033[0m"
    LIST = [BLACK,RED,GREEN,YELLOW,BLUE,CYAN,MAGENTA,WHITE,BRIGHT_BLACK,BRIGHT_BLUE,BRIGHT_RED,BRIGHT_YELLOW,BRIGHT_GREEN,BRIGHT_MAGENTA,BRIGHT_CYAN,BRIGHT_WHITE]

    def RGBtoANSI(rgb:tuple[int]):
        if rgb == (100500,100500,100500):
            return COLORS.RESET
        r,g,b = rgb
        ansi = f"\033[38;2;{r};{g};{b}m"
        return ansi



class MOUSE:
    mousex = 0
    mousey = 0
    prevMousex = 0
    prevMousey = 0
    buttonsClicked  = {
        "left": False,
        "right": False,
        "middle": False
    }

    @classmethod
    def onClick(cls,button,pressed):
        if button.name in cls.buttonsClicked:
            cls.buttonsClicked[button.name] =  pressed
    
    @classmethod
    def onMove(cls,x,y): 
        cls.mousex, cls.mousey = x,y
        MOUSE.cursorSnap()
    
    @classmethod
    def cursorSnap(cls):
        hover = window.pxToChars(cls.mousex,cls.mousey)
        if hover is None:
            cursor.x,cursor.y = 0,0
            return
        cursor.x,cursor.y = hover[0],hover[1]
        if cursor.x+cursor.width > WIDTH:
            cursor.x = WIDTH-cursor.width
        elif cursor.x < 0:
            cursor.x = 0
        if cursor.y + cursor.height > HEIGHT:
            cursor.y = HEIGHT-cursor.height
        elif cursor.y < 0:
            cursor.y = 0

    @classmethod
    def onLeftClick(cls):
        global prevHoverBlock

        if cls.buttonsClicked["left"]:
            if not player.isMining:
                hoverBlock:block|None = block.findFromCoords((cursor.x,cursor.y))
                if player.blockMining is not None:    
                    player.blockMining.texture = player.blockMining.standartVersion
                player.blockMining = hoverBlock
                if player.blockMining is None:
                    return

                # if there is a hover block:
                player.isMining = True

                # check if reachable
                player.updateSides()
                player.blockMining.updateSides()
                if measureDistanceBetweenObjects(player,player.blockMining) > player.mineDistance*BLOCK_SIZE:
                    player.isMining = False
                    player.blockMining = None
                    return
                
                if player.whatLookingAt(blocks) != player.blockMining:
                    player.isMining = False
                    player.blockMining = None
                    return
                
                hoverBlock.texture = hoverBlock.brightVersion
                flickUpdateFrame()
                player.timeMining = 0
                return
            player.mine()
        else:
            if player.blockMining is not None:    
                player.blockMining.texture = player.blockMining.standartVersion
                flickUpdateFrame()
            if player.isMining:
                player.isMining = False
                player.blockMining = None
                player.timeMining = 0
    
    @classmethod
    def onRightClick(cls):
        if cls.buttonsClicked["right"]:
            hoverBlock:block|None = block.findFromCoords((cursor.x,cursor.y))
            if hoverBlock is not None:
                return

            if player.selectedBlock == None:
                return

            newBlock:block = player.selectedBlock(0,0)
            newBlock.gridx,newBlock.gridy = newBlock.getGridCoordsFromCoords(cursor.x,cursor.y)
            newBlock.x,newBlock.y = newBlock.getCoordsFromGridCoords()
            if newBlock not in colliders:    
                colliders.append(newBlock)
            if newBlock not in blocks:
                blocks.append(newBlock)
            
            if checkCollision(player,newBlock):
                newBlock.destroy()
                return

            player.updateSides()
            newBlock.updateSides()
            if measureDistanceBetweenObjects(player,newBlock) > player.placeDistance*BLOCK_SIZE:
                newBlock.destroy()
                return
            
            if player.whatLookingAt(blocks) != newBlock:
                newBlock.destroy()
                return
            
            player.selectedFrame.count -= 1
            if player.selectedFrame.count == 0:
                player.selectedBlock = None
                player.selectedFrame.clearItem()
            else:    
                player.selectedFrame.clearCount()
                player.selectedFrame.displayCount() 
            flickUpdateFrame()
    
    @classmethod
    def onScrollDown(cls):
        if player.selectedFrameIndex + 1 > len(inventory.itemFrames)-1:
            return    
        
        player.selectedFrame.deselect()
        player.selectedFrameIndex += 1
        player.updateSelectedBlock()
        flickUpdateFrame()
    
    @classmethod
    def onScrollUp(cls):
        if player.selectedFrameIndex - 1 < 0:
            return
        
        player.selectedFrame.deselect()
        player.selectedFrameIndex -= 1
        player.updateSelectedBlock()
        flickUpdateFrame()

        


# # turn off quick edit mode on windows
def win32_event_filter(msg, data):
    if msg == 516:
        MOUSE.buttonsClicked["right"] = True
        MOUSE.onRightClick()
        Listener.suppress = True
        return False 
    if msg == 0x41:
        Listener.suppress = True
    if msg == 0x44:
        Listener.suppress = True
    elif msg == 517:
        MOUSE.buttonsClicked["right"] = False
        return False
    
    Listener.suppress = False
    
    return True

mouseController = Controller()

def onClick(x,y,button,pressed):
    MOUSE.onClick(button,pressed)

def onMove(x,y):
    MOUSE.onMove(x,y)

def onScroll(x, y, dx, dy):
    if dy < 0:
        MOUSE.onScrollDown()
        return
    MOUSE.onScrollUp()
    
    
mouseListener = Listener(on_move=onMove,on_click=onClick,on_scroll=onScroll,win32_event_filter=win32_event_filter)
mouseListener.start()



CHARS = {
0: " ",
1: ".",
2: ",",
3: "^",
4: '"',
5: "!",
6: "*",
7: "?",
8: "/",
9: "|",
10: "[",
11: "}",
12: "K",
13: "M",
14: "&",
15: "%",
16: "@",
17: "#",
18: "$",
}
MAX_INTENSITY = len(CHARS)-1

def createTextr (width, height,colRGB):
    output = []
    for y in range(height):
        output.append([])
        for x in range(width):
            output[y].append(colRGB)
    return texture(output)

def flickUpdateFrame ():
    global updateFrame
    updateFrame = True

def findInChars(intensity):
    if type(intensity) == str:
        return intensity
    return CHARS  [intensity]

def findSymbByCoords (fx,fy):
    symbols[fy*WIDTH+fx]
    return symbols[fy*WIDTH+fx]
    

def measureDistance(x1,y1,x2,y2):
    xDistance = abs(x1-x2)
    yDistance = abs(y1-y2)
    distance = (xDistance**2+yDistance**2)**(1/2)
    return distance

def measureDistanceBetweenObjects(obj1,obj2,center=False):
    if center:
        obj1.updateSides()
        obj2.updateSides()
        return measureDistance(obj1.center[0],obj1.center[1],obj1.center[0],obj2.center[1])
    return measureDistance(obj1.x,obj1.y,obj2.x,obj2.y)

def indexDict (dict,obj):
    index = 0
    for val in dict.values():
        index += 1
        if val == obj:
            return index 
        


def loadLayout(layout):
    global namesNClasses

    lx = 0
    ly = 0
    for name in layout:
        lx += 1
        if lx == 16:
            ly += 1
            lx = 0
        if name is None:
            continue
        if not ly == 8:      
            cls = namesNClasses[name]
            cls(lx,ly)



STRINGS = []
for i in range(HEIGHT):
    STRINGS.append("")
STRINGS_START = STRINGS.copy()

BG_COLOR = COLORS.WHITE

class symbol:
    def __init__(self,color,intensity,x,y,menuSymb = False):
        self.x = x
        self.y = y
        self.color = color
        self.intensity = intensity
        self.distanceFromLight = 0
        self.menuSymb = menuSymb
        if menuSymb:
            self.intensity = MAX_INTENSITY
        symbols.append(self)

# SPAWN ALL SYMBOLS
for y in range(HEIGHT):
    for x in range(WIDTH):
        if x > GAME_WIDTH:
            newSymb = symbol(COLORS.WHITE, 0, x,y,True)
            continue
        newSymb = symbol(COLORS.WHITE, 0, x,y,False)


class texture:
    def __init__(self,texture:list):
        self.width = len(texture[0])
        self.height = len(texture)
        self.texture = texture
    def findInTexture(self,x,y):
        if self.texture[y][x] == (-12,-12,-12):
            return BG_COLOR
        return COLORS.RGBtoANSI(self.texture[y][x])
    def getWidth(self):
        return len(self.texture[0])
    def getHeight(self):
        return len(self.texture)

class shape:
    def __init__(self,x,y,width,height,texture):
        self.x = x
        self.y = y
        self.width = width
        self.texture = texture
        self.lists = [objects]
        self.height = height
        self.bottom = self.y + self.height
        self.right = self.x + self.width
        self.left = self.x
        self.top = self.y
        self.center = self.x+self.width//2,self.y+self.height//2
        self.corners = [(self.left,self.top),(self.left,self.bottom),(self.right,self.top),(self.right,self.bottom)]
        objects.append(self)
    def destroy(self):
        for lst in self.lists:
            if self in lst:    
                lst.remove(self)
        del self
    def updateSides(self):
        self.bottom = self.y + self.height
        self.right = self.x + self.width
        self.left = self.x
        self.top = self.y
        self.center = self.x+self.width//2,self.y+self.height//2
        self.corners = [(self.left,self.top),(self.left,self.bottom),(self.right,self.top),(self.right,self.bottom)]
    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                symb = findSymbByCoords(self.x+x,self.y+y)
                symb.color = self.texture.findInTexture(x,y)

    @classmethod
    def fromTexture(cls,x,y,textr:texture):
        return cls(x,y,textr.getWidth(),textr.getHeight(),textr)

def loadTextures():
    global grassTexture,darkDirtTexture,darkGrassTexture,characterTexture,brightDirtTexture,interfaceBGTexture
    global cursorTexture,darkWoodTexture,brightLeavesTexture,brightGrassTexture,itemFrameTexture,leavesTexture,woodTexture,darkLeavesTexture,brightWoodTexture
    global dirtTexture,HitemFrameTexture,brightIronTexture,brightQuartzTexture,ironTexture,quartzTexture
    global stoneTexture,coalTexture,brightStoneTexture,brightCoalTexture
    import textures


    HitemFrameTexture = texture(textures.HitemframeT)
    brightLeavesTexture = texture(textures.brightLeavesT)
    darkWoodTexture = texture(textures.darkWoodT)
    brightDirtTexture = texture(textures.brightDirtT)
    interfaceBGTexture = texture(textures.interfaceBGT)
    leavesTexture = texture(textures.leavesT)
    cursorTexture = texture(textures.cursorT)
    darkLeavesTexture = texture(textures.darkLeavesT)
    characterTexture = texture(textures.characterT)
    brightGrassTexture = texture(textures.brightGrassT)
    dirtTexture = texture(textures.dirtT)
    woodTexture = texture(textures.woodT)
    darkDirtTexture = texture(textures.darkDirtT)
    itemFrameTexture = texture(textures.itemFrameT)
    grassTexture = texture(textures.grassT)
    brightWoodTexture = texture(textures.brightWoodT)
    darkGrassTexture = texture(textures.darkGrassT)
    stoneTexture = texture(textures.stoneT)
    coalTexture = texture(textures.coalT)
    brightStoneTexture = texture(textures.brightStoneT)
    brightCoalTexture = texture(textures.brightCoalT)
    brightIronTexture = texture(textures.brightIronT)
    brightQuartzTexture = texture(textures.brightQuartzT)
    ironTexture = texture(textures.ironT)
    quartzTexture = texture(textures.quartzT)






loadTextures()


def checkCollision(collider1:shape,collider2:shape):
    collider1.updateSides()
    collider2.updateSides()

    # bools for detecting overlaps
    overlaps = False
    overlapsHorizontallyRight = False
    overlapsHorizontallyLeft = False
    overlapsHorizontally = False
    overlapsVerticallyTop = False
    overlapsVerticallyBottom = False
    overlapsVertically = False

    # detect horizontal overlapping
    overlapsHorizontallyLeft = isBetween(collider2.left,collider1.left,collider1.right) or isBetween(collider1.left,collider2.left,collider2.right)
    overlapsHorizontallyRight = isBetween(collider2.right,collider1.left,collider1.right) or isBetween(collider1.right,collider2.left,collider2.right)

    # detect vertical overlapping
    overlapsVerticallyBottom = isBetween(collider2.bottom,collider1.top,collider1.bottom) or isBetween(collider1.bottom,collider2.top,collider2.bottom)
    overlapsVerticallyTop = isBetween(collider2.top,collider1.top,collider1.bottom) or isBetween(collider1.top, collider2.top,collider2.bottom)

    # general horizontal
    overlapsHorizontally = overlapsHorizontallyLeft or overlapsHorizontallyRight or (collider1.left == collider2.left and collider2.right == collider1.right)

    # general vertical
    overlapsVertically = overlapsVerticallyTop or overlapsVerticallyBottom or (collider1.top == collider2.top and collider1.bottom == collider2.bottom)

    # general
    overlaps = overlapsVertically and overlapsHorizontally

    return overlaps

def checkPointCollision(collider:shape,pos:tuple):
    cx,cy = pos
    
    overlaps = False
    overlapsVertically = False
    overlapsHorizontally = False

    overlapsHorizontally = isBetween(cx,collider.left,collider.right) or cx == collider.left or cx == collider.right
    overlapsVertically = isBetween(cy, collider.top,collider.bottom) or cy == collider.top or cy == collider.bottom

    if overlapsHorizontally and overlapsVertically:
        overlaps = True
    
    return overlaps

def checkPointListCollision(pos:tuple,lst:list):
    for element in lst:
        if checkPointCollision(element,pos):
            return element
    return None

def checkListCollision(col1,lst):
    lstCopy = lst.copy()
    if col1 in lstCopy:
        lstCopy.remove(col1)
    for element in lstCopy:  
        if checkCollision(col1,element):
            return element
    return None

def getMinDistance(obj1:shape,obj2:shape):
    # update sides
    obj1.updateSides()
    obj2.updateSides()

    # get all distances between every corner
    cornerDistances = []
    for x1,y1 in obj1.corners:
        for x2,y2 in obj2.corners:
            cornerDistances.append((measureDistance(x1,y1,x2,y2),(x1,y1,x2,y2)))
    diagonalDistance,closestCornerPair = min(cornerDistances, key=lambda x: x[0])

    # check if objects are lined up
    cx1,cy1,cx2,cy2 = closestCornerPair
    dx = abs(cx1-cx2)
    dy = abs(cy1-cy2)
    if dx == 0:
        return dy
    if dy == 0:
        return dx
    # one side inside between another two by X
    if isBetween(obj2.left,obj1.left,obj1.right) or isBetween(obj1.left,obj2.left,obj2.right) or isBetween(obj2.right,obj1.left,obj1.right) or isBetween(obj1.right,obj2.left,obj2.right):
        return(min(diagonalDistance,dy))
    
    # one side is inside onther two by Y 
    if isBetween(obj2.bottom,obj1.top,obj1.bottom) or isBetween(obj1.bottom,obj2.top,obj2.bottom) or isBetween(obj2.top,obj1.top,obj1.bottom) or isBetween(obj1.top, obj2.top,obj2.bottom):
        return min((diagonalDistance,dx))
    
    return diagonalDistance

class inventory:
    itemFrames = []
    interfaceBG = shape.fromTexture(96,0,interfaceBGTexture)
    FRAME_ROWS = 5
    FRAME_COLLUMNS = 4
    FRAME_INDENT_X = 1
    FRAME_INDENT_Y = 1
    FRAME_WIDTH = 17
    FRAME_HEIGHT = 10

    @classmethod
    def createFrames(cls):
        for y in range(cls.FRAME_COLLUMNS):
            for x in range(cls.FRAME_ROWS):
                itemF = itemFrame.fromTexture(100+(cls.FRAME_WIDTH+cls.FRAME_INDENT_X)*x,3+(cls.FRAME_HEIGHT+cls.FRAME_INDENT_Y)*y,itemFrameTexture)
                cls.itemFrames.append(itemF)
    
    @classmethod
    def getNextEmptyFrame(cls):
        for iFrame in cls.itemFrames:
            if iFrame.item is None:
                return iFrame
    
    @classmethod
    def getFrameByItem(cls,item):
        for iFrame in cls.itemFrames:
            if iFrame.item == item:
                return iFrame
    
    @classmethod
    def add(cls,item,count):
        for frame in cls.itemFrames:
            if frame.item is not None and frame.item.name == item.name and frame.count + count <= itemFrame.ITEM_LIMIT:
                nextEmptyFrame = frame
        try:
            nextEmptyFrame
        except:    
            nextEmptyFrame:itemFrame = cls.getNextEmptyFrame()
        
        if nextEmptyFrame.count == 0:
            nextEmptyFrame.item = item
            item.x = nextEmptyFrame.itemX
            item.y = nextEmptyFrame.itemY
        else:
            item.destroy()
        nextEmptyFrame.count += count
        nextEmptyFrame.displayCount()
    
    @classmethod
    def remove(cls,frame):
        frame.item = None
        frame.count = 0

class itemFrame(shape):
    ITEM_LIMIT = 20
    def __init__(self, x, y, width, height, texture):
        super().__init__(x, y, width, height, texture)
        self.item = None
        self.count = 0
        self.gridx = (x-100)/(inventory.FRAME_WIDTH+inventory.FRAME_INDENT_X)
        self.gridy = (y-3)/(inventory.FRAME_HEIGHT-inventory.FRAME_INDENT_Y)
        self.itemX = self.x+2
        self.itemY = self.y+2
        self.countX = self.itemX+BLOCK_SIZE+1
        self.countY = self.itemY
        self.countXEnd = self.countX+BLOCK_SIZE
        self.countYEnd = self.countY+BLOCK_SIZE
        self.selectedTexture = HitemFrameTexture
        self.standartTexture = itemFrameTexture
        self.countSymbs = []
        for y in range(self.countY,self.countYEnd):
            for x in range(self.countX,self.countXEnd):
                findSymbByCoords(x,y).intensity = " "
    
    def writeInCount(self,text:str,fx:int,fy:int) -> None:
        textSplit = list(text)
        if len(textSplit) > 6:
            genOfLsts = chunks(textSplit,6)
            for lst in genOfLsts:
                for index,letter in enumerate(lst):
                    findSymbByCoords(self.countX+fx+index,self.countY+fy).intensity = letter
                fy += 1
            return
        for index,letter in enumerate(textSplit):
            findSymbByCoords(self.countX+fx+index,self.countY+fy).intensity = letter

    def displayCount(self):
        stringHowMuch = f"x {self.count}"
        stringWhat = f"{self.item.name}"
        self.writeInCount(stringHowMuch,1,1)
        self.writeInCount(stringWhat,0,3)

    def clearCount(self):
        for y in range(0,BLOCK_SIZE):
            for x in range(0,BLOCK_SIZE):
                findSymbByCoords(self.countX+x,self.countY+y).intensity = findInChars(0)

    def clearItem(self):
        self.item.destroy()
        self.item = None
        self.count = 0
        self.clearCount()

    def select(self,player):
        self.texture = self.selectedTexture
        player.selectedBlock = namesNClasses[self.item.name] if self.item is not None else None
    
    def deselect(self):
        self.texture = self.standartTexture

inventory.createFrames()

class rectangle(shape):
    def __init__(self,x,y,width,height,texture):
        super().__init__(x,y,width,height,texture)
        self.lists.append(colliders)
        colliders.append(self)



class character(rectangle):
    def __init__(self, x, y, width, height, texture,speed,mineStrength):
        super().__init__(x, y, width, height, texture)
        self.speed = speed
        self.mineStrength = mineStrength
        self.fall = 0
        self.mineDistance = 2
        self.placeDistance = 4
        self.isJumping = False
        self.jumpForce = 2
        self.jumpVelocity = 0
        self.selectedBlock:block = None
        self.selectedFrameIndex = 0
        self.selectedFrame:itemFrame = inventory.itemFrames[self.selectedFrameIndex]
        self.selectedFrame.select(self)
        self.grounded = False
        self.eyesX = self.x+4
        self.eyesY = self.y+2
        self.groundedObject = None
        self.light = bestLight
        self.isMining = False
        self.blockMining = None
        self.timeMining = 0
    def updateSides(self):
        super().updateSides()
        self.eyesX = self.center[0]
        self.eyesY = self.center[1]

    def whatLookingAt(self,lst):
        self.updateSides()

        lookLinePoints = getPointsFromLine(self.eyesX,self.eyesY,cursor.x,cursor.y)
        for point in lookLinePoints:
            for t in lst:
                if checkPointCollision(t,point):
                    return t
        return None



    def move(self,amt):
        self.checkForItems()
        if 0 <= self.x + amt <= GAME_WIDTH-self.width:
            self.x += amt
        if checkListCollision(self,colliders) is not None:
            self.x -= amt
        flickUpdateFrame()
    def applyGravity(self):
        self.checkGrounded()
        if not self.grounded:    
            self.fall += GRAVITY
        else:
            self.fall = 0
            return
        self.checkForItems()
        changeFrame = False
        collisionObject = checkListCollision(self,colliders)
        finalY = self.y + self.fall
        if collisionObject is None and not self.grounded:  
            while self.y < finalY:
                self.y += 1
                collisionObject = checkListCollision(self,colliders)
                if collisionObject is not None:
                    self.y = collisionObject.y - self.height
                    self.grounded = True
                    self.groundedObject = collisionObject
                    changeFrame = True
                    break
            changeFrame = True
        if changeFrame:    
            flickUpdateFrame()
    def startJump(self):
        global startGravity

        if self.isJumping or not self.grounded:
            return
        self.isJumping = True
        self.fall = 0
        startGravity = False
        self.jumpVelocity = self.jumpForce
    def applyJump(self):
        global startGravity,colliders

        if not self.isJumping:
            return
        self.checkForItems()
        self.y -= self.jumpVelocity
        self.jumpVelocity -= 0.3
        collisionObject = checkListCollision(self,colliders)
        self.updateSides()
        
        if collisionObject is not None:
            collisionObject.updateSides()
            if self.jumpVelocity <= 0 and abs(self.bottom - collisionObject.top) < 4:
                self.y = collisionObject.y-self.height
                self.grounded = True
                self.groundedObject = collisionObject
                self.isJumping = False
                startGravity = True
            elif abs(self.top - collisionObject.bottom) < 2:
                self.y = collisionObject.y+collisionObject.height
                self.jumpVelocity = 0
        if self.jumpVelocity == -self.jumpForce-1:
            self.isJumping = False
            startGravity = True
        flickUpdateFrame()
    def checkGrounded(self):
        # if grounded == true:
        self.y += 1
        collisionObject = checkListCollision(self, colliders)
        if collisionObject is None:
            self.grounded = False
            self.groundedObject = None
            self.y -= 1
            return
        # if grounded == true:(tyhere is collision if lower one point)
        self.grounded = True
        self.groundedObject = collisionObject
        self.y -= 1 
    def checkForItems(self):
        collisionObject = checkListCollision(self,items)
        if collisionObject is None:
            return
        collisionObject:item
        collisionObject.onCollection()
    def aquireLight(self,light):
        self.light = light
    def mine(self):
        self.timeMining += deltaTime
        self.blockMining:block
        if self.blockMining.mineTime*(1/self.mineStrength) < self.timeMining:
            self.blockMining.mined()
    def updateSelectedBlock(self):
        self.selectedFrame:itemFrame = inventory.itemFrames[self.selectedFrameIndex]
        self.selectedFrame.select(self)        


class lightSource():
    def __init__(self,x,y,lightRange,descends,maxLuminosity,showOnStart = False):
        self.x = x
        self.y = y
        self.range = lightRange

        self.descends = descends # how many descends  
        self.maxLuminosity = maxLuminosity
        self.appliers = []
        ringWidth = self.range/self.descends
        lumen = maxLuminosity/descends
        self.rings = {}
        previousPoint = self.range
        for desc in range(1,descends+1):
            self.rings[(previousPoint-ringWidth,previousPoint)] = desc*lumen
            previousPoint -= ringWidth
        if showOnStart:    
            self.apply()
    def updateAppliers(self):
        self.appliers = self.findAppliers()
    def findAppliers(self):
        potentialAppliers = []
        appliers = [] # appliers are symbols to whuch lightning is applied

        # get all symbols in square with a side of range*2+someSafetyShit around the source
        for y in range(self.y-self.range-1,self.y+self.range+2):    
            for x in range(self.x-self.range-1,self.x+self.range+2):  
                if not 0 <= x < GAME_WIDTH:
                    continue
                if not 0 <= y < HEIGHT:
                    break
                potentialAppliers.append(findSymbByCoords(x,y))
        
        # from the potential get all that are real appliers
        for applier in potentialAppliers:
            applier:symbol
            distance = measureDistanceBetweenObjects(applier,self)
            if distance <= self.range: 
                applier.distanceFromLight = distance    
                appliers.append(applier)
        for appl in appliers:
            appl: symbol
            for ringRange,intensity in self.rings.items():
                if inclusiveIsBetween(appl.distanceFromLight,ringRange[0],ringRange[1]):
                    appl.intensity = intensity


        return appliers
    def apply(self):
        for applier in self.appliers:
            applier:symbol
            applier.intensity = 0
        self.updateAppliers() 
        flickUpdateFrame()

    def snapToPlayer(self):
        player.updateSides()
        self.x,self.y = player.center
        self.apply()
    def updateRings(self):
        ringWidth = ceil(self.range/self.descends)
        lumen = ceil(self.maxLuminosity/self.descends)
        self.rings = {}
        previousPoint = 0
        descList = list(reversed(range(1,self.descends+1)))
        for desc in descList:
            ringLumen = desc*lumen
            if ringLumen > MAX_INTENSITY:
                ringLumen = MAX_INTENSITY
            if ringLumen < 0:
                ringLumen = 0
            self.rings[(previousPoint,previousPoint+ringWidth)] = ringLumen
            previousPoint += ringWidth    

class item(shape):
    def __init__(self, x, y, width, height, texture):
        super().__init__(x, y, width, height, texture)
        self.lists.append(items)
        items.append(self)
    def onCollection(self):
        self.destroy()

class lightItem(item):
    def __init__(self, x, y, width, height, texture,light):
        super().__init__(x, y, width, height, texture)
        self.light = light
    def onCollection(self):
        player.aquireLight(self.light)
        super().onCollection()

class block(rectangle):
    def __init__(self, gridX, gridY, texture,name:str,mineTime,brightVersion):
        self.name:str = name
        self.gridx = gridX
        self.gridy = gridY
        self.mineTime = mineTime         
        self.brightVersion = brightVersion
        self.wasMined = False
        self.neighbours = []
        x,y = self.getCoordsFromGridCoords()
        blocks.append(self)
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, texture)
        self.lists.append(blocks)
        self.standartVersion = self.texture
        self.updateNeighbours()
    def getCoordsFromGridCoords(self):
        return self.gridx * BLOCK_SIZE, self.gridy * BLOCK_SIZE
    def getGridCoordsFromCoords(self,x,y):
        return x // BLOCK_SIZE,y // BLOCK_SIZE
    @classmethod
    def findFromCoords(cls,pos):
        if not 0 <= pos[0] < GAME_WIDTH or not 0 <= pos[1] < HEIGHT:
            return None
        
        gx = int(pos[0]//BLOCK_SIZE)
        gy = int(pos[1]//BLOCK_SIZE)

        for bl in blocks:
            if bl.gridx == gx and bl.gridy == gy:
                return bl
        return None
    
    def updateNeighbours(self):
        self.updateSides()
        self.neighbours = [
        self.findFromCoords((self.x,self.y-3)),
        self.findFromCoords((self.x,self.bottom+3)),
        self.findFromCoords((self.x-3,self.y)),
        self.findFromCoords((self.right+3,self.y)),
        ]
        for neigh in self.neighbours[:]:
            if neigh is None:
                self.neighbours.remove(neigh)
    def mined(self):
        if self.wasMined:
            return
        

        
        self.texture = self.standartVersion
        
        for neigh in self.neighbours:
            neigh:block
            neigh.updateNeighbours()

        colliders.remove(self)
        blocks.remove(self)
        self.wasMined = True
        inventory.add(self,1)
        player.updateSelectedBlock()
        flickUpdateFrame()
    
    def copy(self):
        newBlock:block = namesNClasses[self.name](self.gridx,self.gridy)
        newBlock.wasMined = False
        return newBlock
    

# block types
class dirt(block):
    def __init__(self, gridx, gridy):
        super().__init__(gridx, gridy, dirtTexture, "dirt",0.4,brightDirtTexture)

class grass(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, grassTexture, "grass", 1,brightGrassTexture)

class wood(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, woodTexture,"wood",2,brightWoodTexture)

class leaves(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, leavesTexture, "leaves", 0.1,brightLeavesTexture)

class stone(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, stoneTexture, "stone", 5, brightStoneTexture)

class quartz(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, quartzTexture, "quartz", 4, brightQuartzTexture)

class coal(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, coalTexture, "coal", 7, brightCoalTexture)

class iron(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, ironTexture, "iron", 6, brightIronTexture)


    

# load textures

namesNClasses = {
    "dirt": dirt,
    "grass": grass,
    "wood": wood,
    "leaves": leaves,
    "stone": stone,
    "coal": coal,
    "iron": iron,
    "quartz": quartz,
}
loadLayout(sandbox)

prevHoverBlock = blocks[0]

# STARTER PACK
inventory.add(dirt(0,0),20)
inventory.add(leaves(0,0),20)
inventory.add(wood(0,0),20)
inventory.add(stone(0,0),20)
inventory.add(coal(0,0),20)
inventory.add(iron(0,0),20)
inventory.add(quartz(0,0),20)
inventory.add(grass(0,0),20)



# OBJECTS:

# light objects
flashLight = lightSource(0,0,18,3,9)
startLight = lightSource(0,0,5,1,14, True)
bestLight = lightSource(0,0,48,1,MAX_INTENSITY)

# player object
player = character(0,0,6,10,characterTexture,1,1)





# walls
def passDraw():
    pass
topWall = rectangle(0,-10,WIDTH,10,createTextr(WIDTH,10,(0,0,0)))
bottomWall = rectangle(0,HEIGHT,WIDTH,1,createTextr(WIDTH,1,(0,0,0)))
topWall.draw = bottomWall.draw = passDraw

# block types:
cursor = shape.fromTexture(0,0,cursorTexture)
objects.remove(cursor)
# ground = rectangle(0,HEIGHT-10,WIDTH,10,createTextr(WIDTH,10,(100,10,80)))
# item frame width: 17, height: 10

def render():
    os.system("cls")
    print("\033[?25l",end="")
    clearScreen()
    STRINGS = STRINGS_START.copy()
    drawObjects()
    player.light.snapToPlayer()
    player.draw() # draw it last
    # cursor.draw()
    for symb in symbols:
        symb:symbol
        if symb.x < WIDTH:
            symbStr = f"{symb.color}{findInChars(symb.intensity)}{COLORS.RESET}"
            STRINGS[symb.y] = STRINGS[symb.y] + symbStr
    for string in STRINGS:
        print(string)

def drawObjects():
    for o in objects:
        o.x = round(o.x)
        o.y = round(o.y)
        o.draw()

# pressed keys. USEd for controls+
pressed =  set()
on_press = lambda k: pressed.add(k.name)
on_release = lambda k: pressed.discard(k.name)

def action(event):
    if event.event_type == KEY_DOWN:
        on_press(event)
    elif event.event_type == KEY_UP:
        on_release(event)

def clearScreen():
    for s in symbols:
        s.color = BG_COLOR

def flickGravity():
    global startGravity
    startGravity = True


CONTROLS = {
    "a": lambda: player.move(-player.speed),
    "d": lambda: player.move(player.speed),
    "h": flickUpdateFrame,
    "space": player.startJump,
}

MOUSE_CONTROLS = {
    "left": MOUSE.onLeftClick,
    "right": MOUSE.onRightClick
}
def control():
    for key in pressed.copy():
        if key in CONTROLS.keys():        
            CONTROLS[key]() 
    
    for button,pressedM in MOUSE.buttonsClicked.items():
        if button in MOUSE_CONTROLS.keys():    
            MOUSE_CONTROLS[button]()

keyboard.hook(lambda e: action(e))


deltaTime = 0.017
while True:
    try:
        startTime = time.time()
        control()
        player.applyJump()
        if startGravity:    
            player.applyGravity()
        if updateFrame:    
            render()
            updateFrame = False

        time.sleep(0.017)
        endTime = time.time()
        deltaTime = endTime - startTime
    except Exception as e:
        print(e)
        input()
