import os

def appendFromFolder(folder,title,writeInTextures=True):

    filenameBases = []

    with open("textures.py","a") as textures:   
        textures.write(f"# {title}" + "\n")
        for filename in os.listdir(folder):
            filenameBase,_ = os.path.splitext(filename)
            if writeInTextures:
                path_ = os.path.join(folder,filename)
                path_ = path_.replace("\\","/")
                textures.write(f'{filenameBase}T = loadTexture(r"{path_}")' + "\n")
            filenameBases.append(filenameBase)
    
    print("Done.")

    return filenameBases
    
def writeInAppender(filenameBases):
    with open("loadTexturesForAppender.py","a") as loader:
        for fnb in filenameBases:
            loader.write(f"{fnb}Texture = texture(textures.{fnb}T)" + "\n")

        loader.write("\n"+"global ")
        for fnb2 in filenameBases:
            loader.write(f"{fnb2}Texture,")


subF = input("subfolder?(y/n) ")
wit = input("writeIntexture? (y/n) ") == "y"
if subF == "y":
    sbf = input("what is subfolder's path? ")
    fbs = []

    for fold in os.listdir(sbf):
        folderPath = os.path.join(sbf,fold).replace("\\","/")
        if fold.endswith((".png",".jpg",".txt")):
            fbs.extend(appendFromFolder(sbf,fold,wit))
        else:
            fbs.extend(appendFromFolder(folderPath,fold,wit))
    fbs = set(fbs)
    fbs = list(fbs)
    writeInAppender(fbs)
else:
    while True:
        folder = input("Enter folder path: ")
        title = input("what is the title? ")
        writeInAppender(appendFromFolder(folder,title,wit))

        if input("exit? ") != "":
            break

                
