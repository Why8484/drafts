import ast
from pathlib import Path

SCRIPT_FOLDER = Path(__file__).parent

def loadTexture(path):
    fullPath = SCRIPT_FOLDER / path

    with open(fullPath,"r") as f:
        rows = f.read().splitlines()
    
    output = []
    for row in rows:
        row = ast.literal_eval(row)
        output.append(row)
    
    return output


characterT = loadTexture(r"txtrs/character.txt")
cursorT = loadTexture(r"txtrs/cursor.txt")
interfaceBGT = loadTexture(r"txtrs/interfaceBG.txt")
itemFrameT = loadTexture(r"txtrs/itemFrame.txt")
HitemframeT = loadTexture(r"txtrs/HitemFrame.txt")

# dirt
brightDirtT = loadTexture(r"txtrs/dirt/brightDirt.txt")
darkDirtT = loadTexture(r"txtrs/dirt/darkDirt.txt")
dirtT = loadTexture(r"txtrs/dirt/dirt.txt")
# grass
brightGrassT = loadTexture(r"txtrs/grass/brightGrass.txt")
darkGrassT = loadTexture(r"txtrs/grass/darkGrass.txt")
grassT = loadTexture(r"txtrs/grass/grass.txt")
# leaves
brightLeavesT = loadTexture(r"txtrs/leaves/brightLeaves.txt")
darkLeavesT = loadTexture(r"txtrs/leaves/darkLeaves.txt")
leavesT = loadTexture(r"txtrs/leaves/leaves.txt")
# wood
brightWoodT = loadTexture(r"txtrs/wood/brightWood.txt")
darkWoodT = loadTexture(r"txtrs/wood/darkWood.txt")
woodT = loadTexture(r"txtrs/wood/wood.txt")


# stones
blackStoneT = loadTexture(r"txtrs/stone/blackStone.txt")
blueStoneT = loadTexture(r"txtrs/stone/blueStone.txt")
brightBlackStoneT = loadTexture(r"txtrs/stone/brightBlackStone.txt")
brightBlueStoneT = loadTexture(r"txtrs/stone/brightBlueStone.txt")
brightOrangeStoneT = loadTexture(r"txtrs/stone/brightOrangeStone.txt")
brightWhiteStoneT = loadTexture(r"txtrs/stone/brightWhiteStone.txt")
orangeStoneT = loadTexture(r"txtrs/stone/orangeStone.txt")
whiteStoneT = loadTexture(r"txtrs/stone/whiteStone.txt")
