from PIL import Image,ImageGrab
import os
import sys
from pathlib import Path
import shutil

BACKUP_FOLDER = r"C:\Users\dan\Desktop\backupConsoleRT"

def getParent(path:str):
    return os.path.split(path)[0]

def getChild(path:str):
    return os.path.split(path)[1]

def move_folders_and_cleanup(
    folders_to_move, source_dir, dest_dir, delete_source=True
):
    # AI SLOP
    # AI SLOP
    # AI SLOP
    # AI SLOP
    # AI SLOP
    # AI SLOP
    # AI SLOP

    """Moves a list of folders from a source directory to a destination directory,

    and optionally deletes the source directory if it's empty.
    """
    # Ensure paths are absolute/normalized
    source_dir = os.path.abspath(source_dir)
    dest_dir = os.path.abspath(dest_dir)

    # 2. Clean up the source directory if requested
    if delete_source:
        try:
            # os.rmdir only works if the directory is empty (safe approach)
            os.rmdir(source_dir)
            print(f"Successfully deleted empty source directory: {source_dir}")
        except OSError:
            print(
                f"Note: {source_dir} was not deleted because it is not empty."
            )

SCRIPT_DIR = Path(__file__).parent

retry = True
def addToImagesFromFolder(pathFolder):
    global retry

    imagesReturn = []
    for file in os.listdir(pathFolder):
        if file.endswith((".png",".jpg")):
            imagesReturn.append((Image.open(os.path.join(pathFolder,file)).convert("RGB"),file))
    retry = False

    return imagesReturn

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
        images = addToImagesFromFolder(pathFolder)
    elif path == "subfolder":
        images = []
        folderPath = input("Enter folder path: ")
        folders = []
        for folder in os.listdir(folderPath):
            if folder.endswith((".png",".jpg")):
                images.append((Image.open(os.path.join(folderPath,folder)).convert("RGB"),folder))
            else:    
                joinedSubfolderPath = os.path.join(folderPath,folder)
                folderImgs = addToImagesFromFolder(joinedSubfolderPath)
                folders.append((joinedSubfolderPath,folderImgs))
                images.extend(folderImgs)
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
    if not os.path.exists(folderName):
        os.makedirs(folderName)

    with open(filePath,"w") as file:
        for string in lst:
            file.write(str(string) + "\n")
    
    print(f"file {fileName} saved to {filePath}")

try:
    for fold,imgs in folders:
        save = os.path.join(saveFolder,fold)
        save = os.path.join(getParent(getParent(save)),getChild(save))
        for imag,name in imgs:
            makeTXTFile(save,getPixelsFromImg(imag),name)
            images.remove((imag,name))
        move_folders_and_cleanup([getChild(fold)],save,saveFolder)
except NameError:
    pass


try:
    for imag,name in images:
        makeTXTFile(saveFolder,getPixelsFromImg(imag),name)
except NameError:
    makeTXTFile(saveFolder,getPixelsFromImg(img),path)
