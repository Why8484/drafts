import os
import time
import keyboard
from keyboard._keyboard_event import KEY_DOWN,KEY_UP
from textures import *
from math import ceil
from startLayout import mainLayout
from pynput.mouse import Controller,Listener
import pygetwindow
import sys

def hideCursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def showCursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


symbols:list = []
objects = []
colliders = []
items = []
blocks = []
WIDTH = 96
HEIGHT = 48   
BLOCK_SIZE = 6
GRID_WIDTH = 16
GRID_HEIGHT= 8
MIN_INTENSITY = 0
GRAVITY = 0.3
updateFrame = True
startGravity = True

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
        


time.sleep(0.5)
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
    cursorImage = None
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
        if cls.buttonsClicked["left"]:
            if not player.isMining:
                hoverBlock = block.findFromCoords((cursor.x,cursor.y))
                player.isMining = True
                player.blockMining = hoverBlock
                if player.blockMining is  None:
                    player.isMining = False
                if player.blockMining is not None:
                    pass
                player.timeMining = 0
                return
            player.mine()
        else:
            if player.isMining:
                player.isMining = False
                player.blockMining = None
                player.timeMining = 0


# PYNPUT SPECIAL MOUSE:

# # turn off quick edit mode on windows
def win32_event_filter(msg, data):
    if msg == 516:
        MOUSE.buttonsClicked["right"] = True
        return False 
    elif msg == 517:
        MOUSE.buttonsClicked["right"] = False
        return False
    
    return True

mouseController = Controller()

def onClick(x,y,button,pressed):
    MOUSE.onClick(button,pressed)

def onMove(x,y):
    MOUSE.onMove(x,y)
mouseListener = Listener(on_move=onMove,on_click=onClick,win32_event_filter=win32_event_filter)
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
    return CHARS  [intensity]

def findSymbByCoords (fx,fy):
    return symbols[fy*WIDTH+fx]

def measureDistance(x1,y1,x2,y2):
    xDistance = abs(x1-x2)
    yDistance = abs(y1-y2)
    distance = (xDistance**2+yDistance**2)**(1/2)
    return distance

def measureDistanceBetweenObjects(obj1,obj2):
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
    def __init__(self,color,intensity,x,y):
        self.x = x
        self.y = y
        self.color = color
        self.intensity = intensity
        self.distanceFromLight = 0
        symbols.append(self)

for y in range(HEIGHT):
    for x in range(WIDTH):
        newSymb = symbol(COLORS.WHITE, 0, x,y)

class texture:
    def __init__(self,texture:list):
        self.width = len(texture[0])
        self.height = len(texture)
        self.texture = texture
    def findInTexture(self,x,y):
        if self.texture[y][x] == (-12,-12,-12):
            return BG_COLOR
        return COLORS.RGBtoANSI(self.texture[y][x])

class shape:
    def __init__(self,x,y,width,height,texture):
        self.x = x
        self.y = y
        self.width = width
        self.texture = texture
        self.height = height
        self.bottom = self.y + self.height
        self.right = self.x + self.width
        self.left = self.x
        self.top = self.y
        self.center = self.x+self.width//2,self.y+self.height//2
        objects.append(self)
    def updateSides(self):
        self.bottom = self.y + self.height
        self.right = self.x + self.width
        self.left = self.x
        self.top = self.y
        self.center = self.x+self.width//2,self.y+self.height//2
    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                symb = findSymbByCoords(self.x+x,self.y+y)
                symb.color = self.texture.findInTexture(x,y)


def isBetween(val, min,max):
    if min < val < max:
        return True
    return False

def inclusiveIsBetween(val,min,max):
    if min <= val <= max:
        return True
    return False

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


def checkListCollision(col1,lst):
    lstCopy = lst.copy()
    if col1 in lstCopy:
        lstCopy.remove(col1)
    for element in lstCopy:  
        if checkCollision(col1,element):
            return element
    return None

class rectangle(shape):
    def __init__(self,x,y,width,height,texture):
        super().__init__(x,y,width,height,texture)
        colliders.append(self)

class character(rectangle):
    def __init__(self, x, y, width, height, texture,speed):
        super().__init__(x, y, width, height, texture)
        self.speed = speed
        self.fall = 0
        self.isJumping = False
        self.jumpForce = 2
        self.jumpVelocity = 0
        self.grounded = False
        self.groundedObject = None
        self.light = bestLight
        self.isMining = False
        self.blockMining = None
        self.timeMining = 0
    def move(self,amt):
        self.checkForItems()
        if 0 <= self.x + amt <= WIDTH-self.width:
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
        if 0 <= self.y + self.fall <= HEIGHT-self.height and collisionObject is None and not self.grounded:  
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
        if collisionObject is not None:
            if self.jumpVelocity <= 0:
                self.y = collisionObject.y-self.height
                self.grounded = True
                self.groundedObject = collisionObject
                self.isJumping = False
                startGravity = True
            else:
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
        if self.blockMining.mineTime < self.timeMining:
            self.blockMining.mined()

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
                if not 0 <= x < WIDTH:
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
        items.append(self)
    def onCollection(self):
        objects.remove(self)
        items.remove(self)

class lightItem(item):
    def __init__(self, x, y, width, height, texture,light):
        super().__init__(x, y, width, height, texture)
        self.light = light
    def onCollection(self):
        player.aquireLight(self.light)
        super().onCollection()

class block(shape):
    def __init__(self, gridX, gridY, texture,name:str,mineTime):
        self.name:str = name
        self.gridx = gridX
        self.gridy = gridY
        self.mineTime = mineTime
        self.wasMined = False
        x,y = self.getCoordsFromGridCoords()
        colliders.append(self)
        blocks.append(self)
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, texture)
    def getCoordsFromGridCoords(self):
        return self.gridx * BLOCK_SIZE, self.gridy * BLOCK_SIZE
    @classmethod
    def findFromCoords(cls,pos):
        for bl in blocks:
            if checkPointCollision(bl,pos):
                return bl
        
    def mined(self):
        if self.wasMined:
            return
        try:
            objects.remove(self)
            blocks.remove(self)
            colliders.remove(self)
            print(f"yoo greetings from{self.name}")
            self.wasMined = True
            flickUpdateFrame()
        except Exception as e:
            print(e)

class dirt(block):
    def __init__(self, gridx, gridy):
        super().__init__(gridx, gridy, dirtTexture, "dirt",0.4)

class grass(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, grassTexure, "grass", 1)

class wood(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, woodTexture,"wood",2)

class leaves(block):
    def __init__(self, gridX, gridY):
        super().__init__(gridX, gridY, leavesTexture, "leaves", 0.1)
    

# load textures
def loadTextures():
    global dirtTexture,grassTexure,woodTexture,leavesTexture,characterTexture,cursorTexture

    dirtTexture = texture(dirtT)
    grassTexure = texture(grassT)
    woodTexture = texture(woodT)
    leavesTexture = texture(leavesT)
    characterTexture = texture(characterT)
    cursorTexture = texture(cursorT)

loadTextures()
namesNClasses = {
    "dirt": dirt,
    "grass": grass,
    "wood": wood,
    "leaves": leaves
}
loadLayout(mainLayout)


# OBJECTS:

# light objects
flashLight = lightSource(0,0,18,3,9)
startLight = lightSource(0,0,5,1,14, True)
bestLight = lightSource(0,0,48,1,MAX_INTENSITY)

# player object
player = character(0,0,6,10,characterTexture,1)

# block types:
cursor = shape(0,0,4,4,cursorTexture)
objects.remove(cursor)
# ground = rectangle(0,HEIGHT-10,WIDTH,10,createTextr(WIDTH,10,(100,10,80)))

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
        if symb.x < WIDTH:
            symbStr = f"{symb.color}{findInChars(symb.intensity)}{COLORS.RESET}"
            STRINGS[symb.y] = STRINGS[symb.y] + symbStr
    for string in STRINGS:
        print(string)

def drawObjects():
    for o in objects:
        try:
            o.x = round(o.x)
            o.y = round(o.y)
        except Exception as e:
            print(o,e)
            input()
            continue
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
    "left": MOUSE.onLeftClick
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
    hideCursor()
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
