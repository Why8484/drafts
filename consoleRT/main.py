import os
import time
import keyboard
from keyboard._keyboard_event import KEY_DOWN,KEY_UP
from textures import *
from math import ceil,floor

symbols:list = []
objects = []
colliders = []
WIDTH = 64
HEIGHT = 32
MAX_INTENSITY = 68
MIN_INTENSITY = 0
GRAVITY = 0.3
updateFrame = True
startGravity = False

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

CHARS = {
0: " ",
1: ".",
2: "'",
3: "`",
4: "^",
5: '"',
6: ",",
7: ":",
8: ";",
9: "I",
10: "l",
11: "!",
12: "i",
13: ">",
14: "<",
15: "~",
16: "+",
17: "_",
18: "-",
19: "?",
20: "]",
21: "[",
22: "}",
23: "{",
24: "1",
25: ")",
26: "(",
27: "|",
28: "/",
29: "t",
30: "f",
31: "j",
32: "r",
33: "x",
34: "n",
35: "u",
36: "v",
37: "c",
38: "z",
39: "X",
40: "Y",
41: "U",
42: "J",
43: "C",
44: "L",
45: "Q",
46: "0",
47: "O",
48: "Z",
49: "m",
50: "w",
51: "q",
52: "p",
53: "d",
54: "b",
55: "k",
56: "h",
57: "a",
58: "o",
59: "*",
60: "#",
61: "M",
62: "W",
63: "&",
64: "8",
65: "%",
66: "B",
67: "@",
68: "$",
}

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
    return CHARS[intensity]

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
    overlapsHorizontally = overlapsHorizontallyLeft or overlapsHorizontallyRight

    # general vertical
    overlapsVertically = overlapsVerticallyTop or overlapsVerticallyBottom

    # general
    overlaps = overlapsVertically and overlapsHorizontally

    return overlaps

def checkListCollision(col1,lst):
    lstCopy = lst.copy()
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
    def move(self,amt):
        if 0 <= self.x + amt <= WIDTH-self.width:
            self.x += amt
        flickUpdateFrame()
    def applyGravity(self):
        self.checkGrounded()
        if not self.grounded:    
            self.fall += GRAVITY
        else:
            self.fall = 0
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
        self.y -= self.jumpVelocity
        self.jumpVelocity -= 0.3
        if self.jumpVelocity <= 0: #on way down
            collisionObject = checkListCollision(self,colliders)
            if collisionObject is not None:
                self.y = collisionObject.y-self.height
                self.grounded = True
                self.groundedObject = collisionObject
                self.isJumping = False
                startGravity = True
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

class lightSource():
    def __init__(self,x,y,lightRange,strength):
        self.x = x
        self.y = y
        self.range = lightRange

        self.strength = strength
        self.appliers = []
        self.appliersByStrength = {}
        self.descendenceInterval = ceil(self.range/self.strength)
        self.strengthDescendence = ceil(self.strength/self.range)
        for index in range(self.range+1):
            self.appliersByStrength[index*self.strengthDescendence] = []
        self.apply()
    def updateAppliers(self):
        self.appliers = self.findAppliers()
    def findAppliers(self):
        potentialAppliers = []
        appliers = []

        for applierList in self.appliersByStrength.values():
            applierList.clear()

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
            distance = measureDistanceBetweenObjects(applier,self)
            if distance <= self.range:
                interval = divmod(distance,self.descendenceInterval)[0]
                self.appliersByStrength[int(((self.range+1)-interval-1)*self.strengthDescendence)].append(applier)                
                appliers.append(applier)
        return appliers
    def apply(self):
        for applier in self.appliers:
            applier:symbol
            applier.intensity = 0
        self.updateAppliers()
        for strength,applierList in self.appliersByStrength.items():
            for appl in applierList:
                appl: symbol
                appl.intensity = strength
        flickUpdateFrame()

    def snapToPlayer(self):
        player.updateSides()
        self.x,self.y = player.center
        self.apply()
    



mainLight = lightSource(15,15,19,15)
ground = rectangle(0,22,64,10,texture(groundTextr))
player = character(0,0,2,2,createTextr(2,2,(255,0,0)),1)
test23 = rectangle(3,10,14,1,createTextr(14,1,(255,255,0)))


def render():
    os.system("cls")
    print("\033[?25l",end="")
    clearScreen()
    STRINGS = STRINGS_START.copy()
    drawObjects()
    mainLight.snapToPlayer()
    for symb in symbols:
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

previousColor = COLORS.WHITE

# pressed keys. USEd for controls+
pressed =  set()
on_press = lambda k: pressed.add(k.name)
on_release = lambda k: pressed.discard(k.name)

def action(event):
    if event.event_type == KEY_DOWN:
        on_press(event)
    elif event.event_type == KEY_UP:
        on_release(event)

def cycleThroughColor():
    global previousColor

    nextIndex = COLORS.LIST.index(previousColor)+1
    if nextIndex > len(COLORS.LIST)-1:
        nextIndex = 0
    color = COLORS.LIST[nextIndex]
    for s in symbols:
        s.color = color
        previousColor = s.color

def clearScreen():
    for s in symbols:
        s.color = BG_COLOR

def flickGravity():
    global startGravity
    startGravity = True



CONTROLS = {
    "x": lambda: (cycleThroughColor(), pressed.discard("x"), flickUpdateFrame()),
    "a": lambda: player.move(-player.speed),
    "d": lambda: player.move(player.speed),
    "g": flickGravity,
    "h": flickUpdateFrame,
    "space": player.startJump,
}
def control():
    for key in pressed.copy():
        if key in CONTROLS.keys():        
            CONTROLS[key]() 

keyboard.hook(lambda e: action(e))

while True:
    control()
    player.applyJump()
    if startGravity:    
        player.applyGravity()
    if updateFrame:    
        render()
        updateFrame = False

    time.sleep(0.017)
