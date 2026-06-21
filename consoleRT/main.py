import os
import time
import keyboard
from keyboard._keyboard_event import KEY_DOWN,KEY_UP
from textures import *

symbols:list = []
objects = []
WIDTH = 64
HEIGHT = 32
MAX_INTENSITY = 68
MIN_INTENSITY = 0


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
        r,g,b = rgb
        ansi = f"\033[38;2;{r};{g};{b};m"
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

for y in range(HEIGHT):
    for x in range(WIDTH):
        newSymb = symbol(COLORS.WHITE, 15, x,y)

def render():
    os.system("cls") #clear screen
    STRINGS = STRINGS_START.copy()
    for symb in symbols:
        if symb.x < WIDTH:
            symbStr = f"{symb.color}{findInChars(symb.intensity)}{COLORS.RESET}"
            STRINGS[symb.y] = STRINGS[symb.y] + symbStr
    for string in STRINGS:
        print(string)

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


CONTROLS = {
    "up": lightenScreen,
    "down": darkenScreen,
    "x": cycleThroughColor,
}
def control():
    for key in pressed.copy():       
        if key in CONTROLS.keys():    
            CONTROLS[key]() 
    
keyboard.hook(lambda e: action(e))

while True:
    control()
    render()
    time.sleep(0.01)
