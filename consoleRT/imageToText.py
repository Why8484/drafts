from PIL import Image,ImageGrab
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

retry = True
while retry:
    path = input("Enter path of the image (!USE THIS SLASH: '/'!)(use folder for folder input): ")
    saveFolder = input("enter save folder path: ")
    if saveFolder == "":
        saveFolder = "txtrs"
    if path == "clipboard":
        img = ImageGrab.grabclipboard()
        if img:
            retry = False
    elif path == "folder":
        pathFolder = input("Enter folder path: ")
        images = []
        for file in os.listdir(pathFolder):
            if file.endswith((".png",".jpg")):
                images.append((Image.open(os.path.join(pathFolder,file)).convert("RGB"),file))
        retry = False
    else:    
        img = Image.open(path).convert("RGB")
        path = path.split("/")[-1]
        retry = False


def getPixelsFromImg(img):
    pixels = list(img.get_flattened_data())
    pixelsNCoords = []

    for y in range(img.height):    
        pixelsNCoords.append([])
        for x in range(img.width):
            color = pixels[y*img.width+x]
            if color == (0,0,0):
                color = (-12,-12,-12)
            pixelsNCoords[y].append(color)
    
    return pixelsNCoords

def makeTXTFile(folderName,lst,fileName):
    if not fileName.endswith(".txt"):
        fileName = fileName[:-4]
        fileName = f"{fileName}.txt"

    filePath = os.path.join(folderName,fileName)
    if os.path.exists(filePath):
        with open(filePath, "w") as f:
            f.write("")
    if not os.path.exists(folderName):
        os.makedirs(folderName)

    with open(filePath,"a") as file:
        for string in lst:
            file.write(str(string) + "\n")
    
    print(f"file {fileName} saved to {filePath}")


try:
    for imag,name in images:
        makeTXTFile(saveFolder,getPixelsFromImg(imag),name)
except NameError:
    makeTXTFile(saveFolder,getPixelsFromImg(img),path)
