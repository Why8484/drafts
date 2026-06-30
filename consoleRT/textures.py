import ast
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).parent

def loadtexture(path):
    fullPath = SCRIPT_FOLDER / path

    with open(fullPath,"r") as f:
        rows = f.read().splitlines()
    
    output = []
    for row in rows:
        row = ast.literal_eval(row)
        output.append(row)
    
    return output
    
dirtT = loadtexture(r"txtrs/dirt.txt")
grassT = loadtexture(r"txtrs/grass.txt")
woodT = loadtexture(r"txtrs/wood.txt")
leavesT = loadtexture(r"txtrs/leaves.txt")
characterT = loadtexture(r"txtrs/character.txt")
cursorT = loadtexture(r"txtrs/cursor.txt")
interfaceBGT = loadtexture(r"txtrs/interfaceBG.txt")
itemFrameT = loadtexture(r"txtrs/itemFrame.txt")
