import os
import time
import keyboard
from keyboard._keyboard_event import KEY_DOWN,KEY_UP
from textures import *

symbols:list = []
objects = []
colliders = []
WIDTH = 64
HEIGHT = 32
MAX_INTENSITY = 68
MIN_INTENSITY = 0
GRAVITY = 1
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


def findInChars(intensity):
    return CHARS[intensity]

def findSymbByCoords (fx,fy):
    return symbols[fy*WIDTH+fx]


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
        self.jumpForce = 5
        self.jumpVelocity = 0
        self.grounded = False
        self.groundedObject = None
    def move(self,amt):
        if 0 <= self.x + amt <= WIDTH-self.width:
            self.x += amt
        flickUpdateFrame()
    def applyGravity(self):
        if not self.grounded:    
            self.fall += GRAVITY
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
        self.jumpVelocity -= 1
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
        if self.grounded == False:
            self.groundedObject = None
            return
        
        # if grounded == true:
        self.y += 1
        if checkCollision(self,self.groundedObject):
            return
        # if grounded == false:(no collision if lower one point)
        self.grounded = False
        self.groundedObject = None
        self.y -= 1




ground = rectangle(0,22,64,10,texture(groundTextr))
player = character(0,0,3,4,createTextr(3,4,(0,255,0)),1)
test23 = rectangle(3,10,14,1,createTextr(14,1,(255,0,0)))


for y in range(HEIGHT):
    for x in range(WIDTH):
        newSymb = symbol(COLORS.WHITE, 19, x,y)

def render():
    os.system("cls")
    print("\033[?25l",end="")
    clearScreen()
    STRINGS = STRINGS_START.copy()
    drawObjects()
    for symb in symbols:
        if symb.x < WIDTH:
            symbStr = f"{symb.color}{findInChars(symb.intensity)}{COLORS.RESET}"
            STRINGS[symb.y] = STRINGS[symb.y] + symbStr
    for string in STRINGS:
        print(string)

def drawObjects():
    for o in objects:
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

def lightenScreen():
    for s in symbols:
        if s.intensity < MAX_INTENSITY:    
            s.intensity += 1

def darkenScreen():
    for s in symbols:
        if s.intensity > MIN_INTENSITY:    
            s.intensity -= 1

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

def flickUpdateFrame ():
    global updateFrame
    updateFrame = True

CONTROLS = {
    "up": lambda: (lightenScreen(), pressed.discard("up"),flickUpdateFrame()),
    "down": lambda: (darkenScreen(), pressed.discard("down"), flickUpdateFrame()),
    "x": lambda: (cycleThroughColor(), pressed.discard("x"), flickUpdateFrame),
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
