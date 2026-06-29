from PIL import Image,ImageGrab
from pathlib import Path
import os

SCRIPT_DIR = Path(__file__).parent

def getPixelsFromImg(img):
    pixels = list(img.get_flattened_data())
    pixelsNCoords = []

    for y in range(img.height):    
        pixelsNCoords.append([])
        for x in range(img.width):
            pixelsNCoords[y].append(pixels[y*img.width+x])
    
    return pixelsNCoords


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
    

def previewImage(path):
    path = SCRIPT_DIR / path
    img = Image.open(path).convert("RGB")

    pnc = getPixelsFromImg(img)

    colors = []

    LENGTh = len(pnc[0])

    for string in pnc:
        for color in string:
            colors.append(COLORS.RGBtoANSI(color))

    i = 0
    strring = ""
    for c in colors:
        strring = strring+f"{c}${COLORS.RESET}"
        i += 1
        if i == LENGTh:
            print(strring)
            strring = ""
            i = 0


while True:
    path = input("image path: ")
    if path == "folder":
        folderPath = input("enter folder path: ")
        try:
            os.listdir(SCRIPT_DIR / folderPath)
            for filename in os.listdir(SCRIPT_DIR / folderPath):
                previewImage(os.path.join(folderPath,filename))
        except:
            pass
    else:
        try:    
            previewImage(path)
        except:
            pass

    if input("exit ...") != "":
        break