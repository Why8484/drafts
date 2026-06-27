from PIL import Image,ImageGrab
import os

retry = True
while retry:
    path = input("Enter path of the image: ")
    saveFolder = input("enter save folder path: ")
    if path == "clipboard":
        img = ImageGrab.grabclipboard()
        if img:
            retry = False
    elif path == "folder":
        pathFolder = input("Enter folder path: ")
        images = []
        for file in os.listdir(pathFolder):
            if file.endswith((".png",".jpg",".jpeg")):
                images.append((Image.open(os.path.join(pathFolder,file)).convert("RGB"),file))
        retry = False
    else:    
        img = Image.open(path).convert("RGB")
        retry = False


def getPixelsFromImg(img):
    pixels = list(img.get_flattened_data())
    pixelsNCoords = []

    for y in range(img.height):    
        pixelsNCoords.append([])
        for x in range(img.width):
            pixelsNCoords[y].append(pixels[y*img.width+x])
    
    return pixelsNCoords

def makeTXTFile(folderName,lst,fileName):
    if not fileName.endswith(".txt"):
        fileName = f"{fileName}.txt"

    filePath = os.path.join(folderName,fileName)
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
