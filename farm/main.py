from  time import time
import random
import os
import math
import json
from copy import copy
import ast
import pygame
import sys

pygame.init()
HEIGHT = 720
WIDTH = 1280
screen = pygame.display.set_mode((WIDTH,HEIGHT))
invPanel = pygame.Surface((WIDTH, 160)) # 1280 X 160
sellPanel = pygame.Surface((WIDTH,560)) # 1280 X 560
transitionScreen = pygame.Surface((WIDTH,HEIGHT), flags=pygame.SRCALPHA) # 1280 X 720 overlay for transitions
sellPanelOpened = False
clock = pygame.time.Clock()
pygame.display.set_caption("farm")
INVENTORY_BG = (245,241,127)
MAX_FPS = 120
BLOCK_SIZE = 80
GRID_WIDTH = int(WIDTH/BLOCK_SIZE) #16
GRID_HEIGHT = int(HEIGHT/BLOCK_SIZE)  #9
FONT_HEIGHT = 30
BIG_FONT_HEIGHT = 66
SLOTS_PER_PAGE = 5
BUTTON_DIM_ALPHA = 162
TIME_PER_FRAME = 1/MAX_FPS
font = pygame.font.Font(r"assets\font.ttf",FONT_HEIGHT)
bigFont = pygame.font.Font(r"assets\font.ttf",BIG_FONT_HEIGHT)
mediumFont = pygame.font.Font(r"assets\font.ttf", 44)
running = True
updateFrame = True
newFarmlandCreated = False
canPressAgain = True
inputValue = ""
typingPosition = 780,100
actionOnInputEnd = None
lastMusicTime = 0
lastMusicEndTime = time()
intervalBetweenMusic = [60,300]
currentMusicInterval = random.randint(intervalBetweenMusic[0], intervalBetweenMusic[1])
canTypeAgain = True
soundPlaying = None
selectedInvSlot = None
GAME_RESET_HAPPENED = False
DESCRIPTION_LINE_SYMBOLS = 50
dt = 0
justExited = False
sineWave = [0.0, 0.087, 0.174, 0.259, 0.342, 0.423, 0.5, 0.574, 0.643, 
            0.707, 0.766, 0.819, 0.866, 0.906, 0.94, 0.966,
            0.985, 0.996, 1.0, 0.996, 0.985, 0.966, 0.94, 0.906, 0.866, 
            0.819, 0.766, 0.707, 0.643, 0.574, 0.5, 0.423, 0.342,
            0.259, 0.174, 0.087, 0.0]


def isJSONable(obj) -> bool:
    """Checks if the item is JSON serializable."""
    try:
        json.dumps(obj)
        return True
    except:
        return False

def eliminateNotJSONables(objects: list|dict|tuple) -> list|dict|tuple:
    """Eliminates every not JSONable object from iterable param objects."""
    valDictCopy = copy(objects.__dict__)
    for attribute, val in objects.__dict__.items():
        if not isJSONable(val):
            valDictCopy.pop(attribute)
    return valDictCopy

def inputValueToInt():
    """Returns the decoded(int) version of inputVlaue variable."""

    if inputValue in ("","-"):
        return 0

    return int(inputValue)

def measureBlockDistance(x1,y1,x2,y2):
    """Measures distance in blocks between two points."""

    x1 = x1//BLOCK_SIZE
    x2 = x2//BLOCK_SIZE
    y1 = y1//BLOCK_SIZE
    y2 = y2//BLOCK_SIZE
    
    return (abs(x1-x2)**2+abs(y1-y2)**2)*(1/2)

def measureDistance(x1,y1,x2,y2):
    return (abs(x1-x2)**2+abs(y1-y2)**2)*(1/2)

def renderText(text:str,color):
    """Returns a surface of rendered text."""

    surf = font.render(text,False,color)
    return surf


def renderBigText(text:str,color,size=BIG_FONT_HEIGHT):
    """Returns a surface of rendered text in font of custom size."""

    if size == BIG_FONT_HEIGHT:
        surf = bigFont.render(text,False,color).convert_alpha()
    elif size == 44:
        surf = mediumFont.render(text,False,color).convert_alpha()
    else:
        # custom sized font
        surf = pygame.font.Font(r"assets\font.ttf", size).render(text,False,color).convert_alpha()

    bgSurf = pygame.Surface(surf.get_size(), flags=pygame.SRCALPHA)

    bgSurf.blit(surf, (0,0))
    
    return bgSurf

def displayLetterAmount(amt):
    """Displays the number as 9.0K, 56M etc."""

    numbers = {
        10**3: "K",
        10**6: "M",
        10**9: "T"
    }

    if amt < list(numbers.keys())[0]:
        return amt

    for n,letter in numbers.items():
        if math.floor(amt/n) < 1000:
            nDigits = 3 - len(list(str(round(amt/n))))
            returnValue = str(round(amt/n,ndigits=nDigits))
            if nDigits == 0:
                returnValue = str(round(amt/n))
            return returnValue + letter

def addPopUpMessage(text):
    """Adds the wanted text to the screen."""

    popUp(text, 80, (222, 77, 64, 255), (WIDTH//2, 440))

def nearestSpace(string: str, index: int) -> int:
    """Finds the index of the nearest space to index given in string `string`.

    Returns -1 if no space is found in the string.
    """
    spaces = [i for i, char in enumerate(string) if char == " "]
    for s in spaces[:]:
        if s < index:
            spaces.remove(s)

    if not spaces:
        return -1

    return min(spaces, key=lambda i: abs(i - index))

def displayCoinsAmount():
    """Returns coin amount as 1M or 1K."""

    coinsAmt = inventory.coins

    return displayLetterAmount(coinsAmt)

def loadImage(path,join=True):
    """Loads an image using the path given and applies convert alpha to it.
    Params:
        path: path of the wanted image.
        join: whethter to join the path with assets folder.
    Returns:
        pygame.Surface image loaded using the path given."""

    
    joinedPath = os.path.join("assets",path) if join else path

    return pygame.image.load(joinedPath).convert_alpha()

def loadFromFolder(folderPath):
    """Loads all images from folder skipping the files
    that are not images. And sor6ts them by name if name is 0.png, 9.png etc.
    Params:
        foldersPath: path of the folder.
    Returns:
        list with pygame.Surface objects."""

    imageSequence = []
    joindeFolderPath = os.path.join("assets",folderPath)
    for fileName in os.listdir(joindeFolderPath):
        joinedPath = os.path.join(joindeFolderPath,fileName)
        if joinedPath.endswith((".png",".jpg","jpeg")):
            imageSequence.append(((loadImage(joinedPath,False)),int(fileName.removesuffix(".png"))))

    imageSequence.sort(key=lambda x: x[1])
    returnSequence = []
    for surf,_ in imageSequence:
        returnSequence.append(surf)

    return returnSequence

mountain = loadImage("mountain.jpg")
playerImage = loadImage("player.png")
soilImage = loadImage("soil.png")
wheatGrowth = loadFromFolder("wheat")
wheatBundleImage = loadImage("wheat bundle.png")
wheatSeedsImage = loadImage("wheat seeds.png")
farmerImage = loadImage("jack.png")
sell1ButtonImage = loadImage("sell1Button.png")
sellCustomButtonImage = loadImage("sellCustom.png")
sellAllButtonImage = loadImage("sellAllButton.png")
highlightFrameImage = loadImage("highlightFrame.png")
coinImage = loadImage("coin.png")
backButtonImage = loadImage("backButton.png")
sellableIndicatorImage = loadImage("sellIndicator.png")
buyableIndicatorImage = loadImage("buyIndicator.png")
buy1Image = loadImage("buy1.png")
buyCustomImage = loadImage("buyCustom.png")
buyMaxImage = loadImage("buyMax.png")
woodAshImage = loadImage("woodAsh.png")
progressBarSequence = loadFromFolder("progressBar")
flourImage = loadImage("flour.png")
waterBucketImage = loadImage("waterBucket.png")
bowlImage = loadImage("bowl.png")
doughImage = loadImage("dough.png")
breadImage = loadImage("bread.png")
charcoalImage = loadImage("charcoal.png")
woodImage = loadImage("wood.png")
fertilizedSoilImage = loadImage("fertilizedSoil.png")
wetSoilImage = loadImage("wetSoil.png")
fertilizedWetSoilImage = loadImage("fertilizedWetSoil.png")
rightButton = loadImage("rightButton.png")
leftButton = loadImage("leftButton.png")
millstoneImage = loadImage("millstoneFull.png")
topMillstoneSequence = loadFromFolder("topMillstoneSpin")
topMillstoneImage = loadImage("topMillstone.png")
bottomMillstoneImage = loadImage("bottomMillstone.png")
brickOvenImage = loadImage("brickOven.png")
brickOvenBars = loadImage("brickOvenBars.png")
brickOvenCookingSequence = loadFromFolder("brickOvenCooking")
brickOvenCookedSequence = loadFromFolder("brickOvenCooked")
bowlBack = loadImage("bowlBack.png")
bowlFront = loadImage("bowlFront.png")
bowlStickSequence = loadFromFolder("bowlStick")
sellPanelBG = pygame.transform.scale_by(loadImage("sellPanelBG.png"),2)
tileVariants = loadFromFolder("tileVariants")
shadowImage = loadImage("shadow.png")

def loadItemAtrribute(objDict, attrName):
    """Loads object's atrribute if it should be equal to item class object. 
    Rteurns none if it's equal to none."""

    if objDict[attrName] is None:
        return None
    return existingItems[objDict[attrName]["name"]]

def isIterable(obj):
    """Checks if the given object is iterable."""

    try:
        iter(obj)
        return True
    except TypeError:
        return False

def loadGame():
    """Loads the progress as you log in."""

    with open("saveFile.txt", "r") as sf:
        savedContext = sf.read()

    objectDicts = []
    saves = savedContext.split(";")

    # inventory loading
    invSave = saves[0]
    if not invSave == "":            
        invSave = ast.literal_eval(invSave)
        for itemName, count, slotIndex in invSave:
            inventory.add(existingItems[itemName], count, putSlot = slotIndex)

    # coins loading
    coinsSave = saves[1] if len(saves) > 1 else ""
    if coinsSave != "":
        coinsSave = int(coinsSave.removesuffix(";"))
        inventory.coins = coinsSave

    # fields and machines loading
    objectStrings = saves[2:]
    for objectStr in objectStrings:
        objectStr = objectStr.replace("\n", "")
        if objectStr == "":
            continue

        objectDicts.append(json.loads(objectStr))

    for objectDict in objectDicts:
        loadClassesDict[objectDict["class"]].loadObject(objectDict)

    loadGameInfo()


def loadGameInfo():
    """Loads general info about the game."""

    with open("gameInfo.txt", "r") as gi:
        savedGameInfo = gi.read()

    gameInfoSaves = savedGameInfo.split(";")
    firstLaunch = json.loads(gameInfoSaves[0].replace("first launch: ", ""))
    if firstLaunch:
        field(1,1)
        firstLaunch = False
        with open("gameInfo.txt", "w") as gi:
            gi.write("first launch: " + json.dumps(firstLaunch) + ";")
    

def resetSavedGameContext():
    """Resets all the saved info about the game."""

    with open("gameInfo.txt", "w") as gi:
        gi.write("first launch: true;")

    with open("saveFile.txt", "w") as sf:
        sf.write("")        

    print("ALL OF THE GAME PROGRESS HAS BEEN RESET.")
    sys.exit()


def createDefaultImage(w,h,col1,col2):
    """Creates a default image: 2x2 grid of squares of two colors.
    Params:
        w: width of the image
        h: height of the image
        col1: first color of the image.
        col2: second color of the image.
    Returns:
        pygame.Surface image object
    """

    surf = pygame.Surface((w,h))
    pygame.draw.rect(surf, col1,(0,0,w//2,h//2))
    pygame.draw.rect(surf, col2, (w//2,0,w//2,h//2))
    pygame.draw.rect(surf, col2, (0,h//2,w//2,h//2))
    pygame.draw.rect(surf, col1, (w//2,h//2,w//2,h//2))

    return surf

def findAreaByGridCoords(gridx,gridy):
    """Finds an area object that overlaps coords given.
    Params:
        gridx and gridy: coords.
    Returns:
        area object that overlaps given coords."""

    return areas[gridy*GRID_WIDTH+gridx]

def findAreaByCoords(coords):
    """Finds an area object that overlaps coords given.
    Params:
        coords: coords.
    Returns:
        area object that overlaps given coords."""

    gridx = coords[0]//BLOCK_SIZE
    gridy = coords[1]//BLOCK_SIZE

    return areas[gridy*GRID_WIDTH+gridx]

    
def findFieldByCoords(coords):
    """Finds an field object that overlaps coords given.
    Params:
        coords: coords.
    Returns:
        field object that overlaps given coords.
        None:if none of the fields overlap these coords."""

    areaX = coords[0] // BLOCK_SIZE
    areaY = coords[1] // BLOCK_SIZE

    areaOnCoords = findAreaByGridCoords(areaX,areaY)
    return areaOnCoords.object

def findFieldByGridCoords(gridx,gridy):
    """Finds an field object that has grid coordinates given.
    Params:
        gridx and gridy: grid coords of the wanted field object.
    Returns:
        field object with given grid coords.
        None: if there's no field with grid coords given."""

    return findAreaByGridCoords(gridx,gridy).object

def checkCollisions(obj,lst:list):
    """Checks object's collision with every object in a given list.
    Params:
        obj: object, who's collisions need to be checked.
        lst: list of colliders with which object's collisions will be checked.
    Returns:
        None: if no collisions have been detected.
        Object from list lst: object with which tghe collision has been detected."""

    objRect:pygame.Rect = obj.getRect()
    for col in lst:
        if objRect.colliderect(col.getRect()):
            return col
    return None

def rollFromChance(chances:dict):
    """
    Rolls a random chance and checks what item was rolled.
    Params:
        chances: a dictionary of items and their chances in syntax item:chance
    Returns:
        None: in case the chances don't add up to 100 percent if nothing rolls.
        item that was rolled."""

    roll = random.random() * 100
    cumulativeChance = 0

    for occurence,chance in chances.items():
        cumulativeChance += chance
        if roll <= cumulativeChance:
            return occurence

    return None

def enableButtonType(enable = True, buttonType = "buy"):
    """Enables or disables(based on the `enable` param) all the buttons with buttonType `buttonType`. 
    When `buttonType` is set to 'all' enables or disables all the buttons."""

    if buttonType not in ("all", "buy", "sell"):
        return

    def controlBasedOnFlag(SPButton):
        if enable:
            SPButton.enable()
        else:
            SPButton.disable()

    if buttonType == "all":
        for spb in sellPanelButtons:
            if spb.buttonType in ("buy", "sell"):
                controlBasedOnFlag(spb)


    for spb in sellPanelButtons:
        if spb.buttonType == buttonType:
            controlBasedOnFlag(spb)

def writeSPBMessages(buttonType, msg):
    """Assigns `disabledText` to each button of `buttonType`.
    When `buttonType` is set to 'all' enables or disables all the buttons."""

    if buttonType not in ("all", "buy", "sell"):
        return

    if buttonType == "all":
        for spb in sellPanelButtons:
            spb.disabledText = msg
    else:
        for spb in sellPanelButtons:
            if spb.buttonType == buttonType:
                spb.disabledText = msg

def controlSPBDimming():
    enableButtonType(False, "all")
    if selectedSellableItem.buyable and inventory.coins >= BUY_PANEL_PRICE_LIST[selectedSellableItem.name]:
        enableButtonType(True, "buy") # enable if enough money to buy at least one and they're buyable
    elif not selectedSellableItem.buyable:
        writeSPBMessages("buy", "You know, money can't buy everything.")
    elif inventory.coins < BUY_PANEL_PRICE_LIST[selectedSellableItem.name]:
        writeSPBMessages("buy", "Womp womp.")

    if selectedSellableItem.sellable and selectedSellableItem.item in inventory.items:
        enableButtonType(True, "sell") # enable sell buttons if you have it and sellable
    elif not selectedSellableItem.sellable:
        writeSPBMessages("sell", "Nah, I don't want that.")
    elif selectedSellableItem.item not in inventory.items:
        writeSPBMessages("sell", "Hey, i won't invest in something, that doesn't exist.")

def getSoundPath(filename):
    """Joins the filename with assets\\audio."""
    return os.path.join("assets\\audio", filename)

musicThemes = []

class sound:
    """Class for sounds."""
    def __init__(self, name, audioPath, type="sound"):
        self.name = name
        self.audioPath = audioPath
        self.sound = pygame.mixer.Sound(audioPath)
        self.length = self.sound.get_length()
        if type == "music":
            musicThemes.append(self)

    def play(self):
        global soundPlaying, lastMusicTime

        self.sound.play()
        soundPlaying = self
        lastMusicTime = time()

sound("Listen to the rain", getSoundPath("listen to the rain.mp3"), type="music")
sound("Gate of heaven", getSoundPath("gate of heaven.mp3"), type="music")
sound("Path to the sun", getSoundPath("path to the sun.mp3"), type="music")
sound("Jumping on rocks", getSoundPath("jumping on rocks.mp3"), type="music")

class entity:
    """Every object on a screen. List: entities"""
    def __init__(self,x,y,layer = 0, width = 0,height = 0,image = None):
        self.x = x
        self.y = y
        self.layer = layer
        self.width = width
        self.height = height
        self.image = image

        if self.image is None:
            if self.width is None or self.height is None:
                return
            self.image = createDefaultImage(self.width,self.height,
                                            (random.randint(0,255),
                                             random.randint(0,255),
                                             random.randint(0,255)),
                                            (random.randint(0,255),
                                             random.randint(0,255),
                                             random.randint(0,255),))
        else:
            self.image:pygame.Surface
            self.width = self.image.get_width()
            self.height = self.image.get_height()

        # sides
        self.updateSides()

        entities.append(self)

    def draw(self,surf=screen):
        surf.blit(self.image,(self.x,self.y))

    def updateSides(self):
        self.center = self.x+self.width//2,self.y+self.height//2
        self.centerx,self.centery = self.center
        self.left = self.x
        self.right = self.x+self.width
        self.top = self.y
        self.bottom = self.y+self.height

    def getRect(self):
        return pygame.Rect(self.x,self.y,self.width,self.height)

    def getInvRect(self):
        return pygame.Rect(self.x,self.y+560, self.width,self.height)

    def toJSON(self):
        """Converts the instance of this class to a JSON string"""
        jsonDict = self.__dict__
        jsonDictCopy = copy(jsonDict)
        for attr, value in jsonDictCopy.items():
            if not isJSONable(value) and not hasattr(value, "__dict__") and not isinstance(value, list):
                jsonDict.pop(attr) 
            elif hasattr(value, "__dict__"):
                jsonDict[attr] = eliminateNotJSONables(value)
            elif isIterable(value) and not isinstance(value, tuple):
                newValue = copy(value)
                newValue.clear()
                for obj in value:
                    if hasattr(obj, "__dict__"):
                        newValue.append(eliminateNotJSONables(obj))

                jsonDict[attr] = newValue
                    

        jsonDict["class"] = str(self.__class__.__name__)
        return json.dumps(jsonDict)

    @classmethod
    def loadObject(cls, objectDict):
        pass

    def drawOnOverlay(self,surf=transitionScreen):
        surf.blit(self.image, (self.x,self.y))

class obstacle(entity):
    """Object that is a collider and is in colliders list. List: colliders."""
    def __init__(self, x, y, layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        colliders.append(self)

class area(entity):
    """Invisible object that covers area of one block. List: areas."""
    def __init__(self, gridx, gridy):

        x = gridx * BLOCK_SIZE
        y = gridy * BLOCK_SIZE

        self.gridx = gridx
        self.gridy = gridy
        self.object = None

        super().__init__(x, y, -5,BLOCK_SIZE,BLOCK_SIZE,random.choice(tileVariants))
        areas.append(self)

class field(entity):
    """Field object on which you can plant plants on. List: fields."""
    def __init__(self, gridx,gridy):


        x = gridx*BLOCK_SIZE
        y = gridy*BLOCK_SIZE

        self.plant = None

        self.gridx = gridx
        self.gridy = gridy
        self.multiplier = 1
        self.fertilized = False
        self.wet = False
        findAreaByGridCoords(gridx,gridy).object = self

        super().__init__(x, y, 0, image=soilImage)
        fields.append(self)

    def fertilize(self):
        """multiply multiplier by 2."""
        self.multiplier *= 2
        self.image = fertilizedSoilImage if not self.wet else fertilizedWetSoilImage
        self.fertilized = True

    def makeWet(self):
        """multipliy multiplier by 1.4."""
        self.multiplier *= 1.4
        self.image = wetSoilImage if not self.fertilized else fertilizedWetSoilImage
        self.wet = True

    @classmethod
    def loadObject(cls, objectDict):
        newField = field(objectDict["gridx"], objectDict["gridy"])
        if objectDict["wet"]:
            newField.makeWet()
        if objectDict["fertilized"]:
            newField.fertilize()
        if objectDict["plant"] is not None:
            wheatDict = objectDict["plant"]
            newWheat = wheat(newField)
            newWheat.growthTime = wheatDict["growthTime"]
            newWheat.phase  = wheatDict["phase"]
            newWheat.timePlanted = wheatDict["timePlanted"]
            newWheat.image = newWheat.growthSequence[newWheat.phase]

class wheat(entity):
    """Wheat object that grows on certain field. List: plants."""
    def __init__(self, field:field):
        self.field = field
        field.plant = self
        self.growthSequence = wheatGrowth
        self.timePlanted = 0
        x,y = field.x,field.y-40
        self.phase = 0
        self.growthTime = [random.randint(16,24),
                           random.randint(22,38),
                           random.randint(14,38),
                           random.randint(38,50)]
        super().__init__(x,y, 1, BLOCK_SIZE, BLOCK_SIZE, self.growthSequence[self.phase])
        plants.append(self)
    def increaseTimePlanted(self):
        """Adds dt to time planted."""
        self.timePlanted += dt*self.field.multiplier
        if self.phase < len(self.growthSequence)-1 and self.timePlanted > self.growthTime[self.phase]:
            self.timePlanted = 0
            self.phase += 1
            self.image = self.growthSequence[self.phase]
            flickUpdateFrame()

    def destroy(self):
        """Removes object from all of it's lists."""
        entities.remove(self)
        plants.remove(self)
        del self

    def breakMyself(self):
        """This is executed when player breaks the plant."""
        self.field.plant = None
        self.destroy()
        match self.phase:
            case 0:
                inventory.add(wheatSeeds,rollFromChance({0: 80, 1: 20}), (self.field.gridx,self.field.gridy))
            case 1:
                inventory.add(wheatSeeds,rollFromChance({0: 20, 1: 60, 2: 20}), (self.field.gridx,self.field.gridy))
            case 2:
                inventory.add(wheatSeeds, rollFromChance({1: 50, 2: 40, 3: 10}), (self.field.gridx,self.field.gridy))
            case 3:
                inventory.add(wheatSeeds, rollFromChance({2: 100}), (self.field.gridx,self.field.gridy))
            case 4:
                inventory.add(wheatSeeds, rollFromChance({2: 70, 3: 30}), (self.field.gridx,self.field.gridy))
                inventory.add(wheatBundle, rollFromChance({1: 95, 2: 5}), (self.field.gridx,self.field.gridy))


class inventory:
    items = {}
    coins = 1000
    page = 1
    previousPage = 1
    LAST_PAGE = 6

    @classmethod
    def add(cls,itemAdding,count,gridCoords = None, putSlot="nextEmpty"):
        """
        Adds some amount of some item to the items dict.
        Params:
            itemAdding: item you wanna add.
            count: how many of these items you wanna add.
            slot: the index of wanted slot in slots list. Will be next em0pty if left empty.
            gridCoords: from wheer you got the item(needed to perform the transition).
        Returns:
            none.
        """
        if count == 0:
            return

        if itemAdding in cls.items:
            cls.items[itemAdding] += count
        else:
            cls.items[itemAdding] = count
            if putSlot == "nextEmpty":
                emptySlot = slot.findNextEmpty()
            else:
                emptySlot = slots[putSlot]
            emptySlot.item = itemAdding
            itemAdding.slot = emptySlot
        flickUpdateFrame()

        if gridCoords is not None:
            for _ in range((min((20, count)))):
                transition(gridCoords[0], gridCoords[1], (itemAdding.slot.x+BLOCK_SIZE*1.2)//BLOCK_SIZE, (sellPanel.get_height() + BLOCK_SIZE)//BLOCK_SIZE, itemAdding.image)

    @classmethod
    def draw(cls):
        """Draws every item in self.items."""
        invPanel.blit(highlightFrameImage,(selectedInvSlot.x-5,selectedInvSlot.y-5))
        for i,count in cls.items.items():
            i.draw(i.slot.x,i.slot.y)
            countText = renderText("x"+str(count),"black")
            invPanel.blit(countText,(i.slot.x+BLOCK_SIZE/2-countText.get_width()//2,
                                     i.slot.y+BLOCK_SIZE+i.title.get_height()+10))

        invPanel.blit(coinImage,(1080,invPanel.get_height()-90))
        leftButtonEnt.draw(invPanel)
        rightButtonEnt.draw(invPanel)
        invPanel.blit(renderBigText(str(displayCoinsAmount()),"black",44),
                      (1165,invPanel.get_height()-60))
        invPanel.blit(renderBigText("currently on page: " + str(inventory.page), "black",33),
                      (1060, 10))


    @classmethod
    def remove(cls,itemRemoving):
        """Removes the one piece given iem from inventory.
        Returns true if there was that item in inventory and false if there wasn't."""
        if itemRemoving not in cls.items.keys():
            return False

        cls.items[itemRemoving] -= 1
        cls.popFromItems(itemRemoving)
        return True
    
    @classmethod
    def popFromItems(cls,item):
        """Pops the item so it doesnt show up in inv panel. 
        Usage: when there is 0 of this item left."""
        if cls.items[item] == 0:
            item.slot.item = None
            item.slot = None
            cls.items.pop(item)

    @classmethod
    def changePage(cls, pageNum="right"):
        """Changes the page of the inventory to param pageNum.
        PageNum could also be equal to 'right'(changes the page to one directly to the 
        right of the current one)
        or 'left'(changes the page to one directly to the left of the current one)."""
        global selectedInvSlot

        if pageNum == "right":
            cls.previousPage = cls.page
            cls.page += 1
            if cls.page > cls.LAST_PAGE:
                cls.page = 1
            cls.applyPage()

        elif pageNum == "left":
            cls.previousPage = cls.page
            cls.page -= 1
            if cls.page == 0:
                cls.page = cls.LAST_PAGE
            cls.applyPage()

        else:
            if not 1 <= pageNum <= cls.LAST_PAGE:
                return
            cls.previousPage = cls.page
            cls.page = pageNum
            cls.applyPage()

        selectedInvSlot = slots[(inventory.page-1) * SLOTS_PER_PAGE]

    @classmethod
    def applyPage(cls):
        index = cls.previousPage - cls.page

        for s in slots:
            s.x += index*1280

class item:
    """Class for items that show up in the inventory space. List: existingItems."""
    def __init__(self, image, name,layer=0,description="",machineClass=None):
        self.image = image
        self.machineClass = machineClass
        self.layer = layer
        self.name = name
        self.slot = None
        self.title = renderText(self.name,"black")
        self.description = description
        self.divideDescription()
        existingItems[self.name] = self

    def draw(self,x,y):
        invPanel.blit(self.image,(x,y))
        invPanel.blit(self.title,(x+BLOCK_SIZE//2-self.title.get_width()//2,y+BLOCK_SIZE+10))

    def divideDescription(self):
        self.description = self.description.replace("\n", " ")
        lines = []
        previous = 0
        lastChar = list(self.description)[-1]
        for symbol in range(0,len(list(self.description)), DESCRIPTION_LINE_SYMBOLS):
            lineEndIndex = nearestSpace(self.description, symbol+DESCRIPTION_LINE_SYMBOLS)
            lines.append(self.description[previous:lineEndIndex])
            previous = lineEndIndex

        self.description = ""
        for line in lines:
            if lines.index(line) == len(lines)-1:
                self.description = self.description + line
                continue
            self.description = self.description + line + "\n"


        self.description = self.description + lastChar

class slot:
    """Class for inventory slots. List: slots."""
    def __init__(self,x,y,page):
        self.x = x
        self.y = y
        self.page = page
        self.item = None
        slots.append(self)

    def getRect(self):
        return pygame.Rect(self.x,self.y+560,BLOCK_SIZE,BLOCK_SIZE)

    @classmethod
    def findNextEmpty(cls):
        for s in slots:
            if s.item is None:
                return s

class sellPanelObject(entity):
    """Class for objects on the sell and buy panel. List: sellPanelObjects."""
    def __init__(self, x, y, layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        entities.remove(self)
        sellPanelObjects.append(self)
    def draw(self, surf=sellPanel):
        surf.blit(self.image,(self.x,self.y))

class sellPanelItem(sellPanelObject):
    """Class for sellable items in sell panel. List: sellPanelItems."""
    def __init__(self, x, y, name, normalItem, sellable=True, buyable=False, layer=0, 
                width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        self.selected = False
        self.name = name
        self.item = normalItem
        self.sellable = sellable
        self.buyable = buyable
        sellPanelItems.append(self)
    def select(self):
        """select this item as the selectedSellable."""
        global selectedSellableItem

        # flags and UI
        self.selected = True
        selectedSellableItem = self
        highlightFrame.x,highlightFrame.y = self.x-5,self.y-5

        # description change
        for descLine in descriptionLines:
            descLine.image = renderText("","black")
        for i,line in enumerate(self.item.description.splitlines()):
            descriptionLines[i].image = renderText(line, "black")
        descriptionTitle.image = renderBigText(self.name, "black")
        descriptionTitle.x = 317 + descriptionPanel[0] - descriptionTitle.image.get_width()//2
        if self.name in BUY_PANEL_PRICE_LIST:
            buyPrice = "Buy for: " + str(BUY_PANEL_PRICE_LIST[self.name]) + "." 
        else:
            buyPrice = "Buy for: non-buyable."
        if self.name in SELL_PANEL_PRICE_LIST:
            sellPrice = "Sell for: " + str(SELL_PANEL_PRICE_LIST[self.name]) + "." 
        else:
            sellPrice = "Sell for: non-sellable."
        sellableStr = "sellable: yes." if self.sellable else "sellable: no."
        buyableStr = "buyable: yes." if self.buyable else "buyable: no."

        descriptionPriceLines[0].image = renderText(sellableStr, "black")
        descriptionPriceLines[1].image = renderText(buyableStr, "black")
        descriptionPriceLines[2].image = renderText(buyPrice, "black")    
        descriptionPriceLines[3].image = renderText(sellPrice, "black")

        if self.buyable:
            buyCount = inventory.coins//int(BUY_PANEL_PRICE_LIST[self.name])
            buyMaxCount = "buy a maximum of " + str(displayLetterAmount(buyCount)) + " " + self.name
            forPrice =  " for " + str(displayLetterAmount(
                buyCount*int(BUY_PANEL_PRICE_LIST[self.name])
                )) + " coins."
            buyMaxText = buyMaxCount + forPrice
        else:
            buyMaxText = "This is non-buyable."
        if self.sellable:
            count = inventory.items[self.item] if self.item in inventory.items else 0
            sellAllText = "sell all " + str(displayLetterAmount(
                count
                )) + " of your " + self.name + " for " + str(displayLetterAmount(
                int(SELL_PANEL_PRICE_LIST[self.name])*count
                )) + " coins."
        else:
            sellAllText = "This is non-sellable."
        buyMaxLine.image = renderText(buyMaxText, "black")
        sellAllLine.image = renderText(sellAllText, "black")

        controlSPBDimming()

    def draw(self, surf=sellPanel):
        super().draw()
        if self.sellable:
            surf.blit(sellableIndicatorImage, (self.x + self.width - 10,self.y))
        elif self.buyable:
            surf.blit(buyableIndicatorImage, (self.x + self.width - 10,self.y))
            return
        if self.buyable:
            surf.blit(buyableIndicatorImage, (self.x + self.width - 20,self.y))
            

class sellPanelButton(sellPanelObject):
    """Class for buttons like sellAll,sell1 etc. List: sellPanelButtons."""
    def __init__(self, x, y, buttonType = "buy", layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        self.disabled = False
        self.buttonType = buttonType
        self.enabledImage = self.image

        self.disabledText = ""

        # create dimmed disabled image
        self.disabledImage = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        overlay = pygame.Surface((self.width,self.height), flags=pygame.SRCALPHA)
        overlay.fill((0,0,0,BUTTON_DIM_ALPHA))
        overlay.blit(self.enabledImage, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        self.disabledImage.blit(self.enabledImage, (0,0))
        self.disabledImage.blit(overlay,(0,0))

        sellPanelButtons.append(self)
    def action(self):
        pass

    def disable(self):
        if self.disabled:
            return

        self.disabled = True
        self.image = self.disabledImage

    def enable(self):
        if not self.disabled:
            return

        self.disabled = False
        self.image = self.enabledImage



class machine(entity):
    """Class for machines like millstone. List: machines"""
    def __init__(self, x, y, image):
        super().__init__(x, y, 0,BLOCK_SIZE,BLOCK_SIZE,image)
        machines.append(self)
        shadow(self.x-10,self.y+60)

    def onLeftClick(self):
        pass

    def onRightClick(self):
        pass

    def onTick(self):
        pass
        

class millstoneMachine(machine):
    """Millstone."""
    def __init__(self, x, y):
        super().__init__(x, y, millstoneImage)
        self.holdStart = None
        self.holdTime = 0
        self.timeToComplete = 1 # 20
        self.animIndex = 0
        self.heightIndex = 0
        barX,barY = self.x-5,self.y-15
        if self.x == 0:
            barX = 0
        if self.y == 0:
            barY = 0
        self.prBar = progressBar(barX,barY)
        self.empty = True
        self.itemIn = None
        self.inputOutput = {
            wheatBundle: flour,
            charcoal: woodAsh
        }
        self.animate = False
        self.ticks = 0
        self.completed = False
    def onLeftClick(self):
        if self.holdStart is None and not self.completed:
            self.holdTime = 0
            self.holdStart = time()
        if self.holdTime >= self.timeToComplete:
            self.holdTime = 0

    def onRightClick(self):
        if selectedInvSlot.item in self.inputOutput and self.empty:
            self.empty = False
            self.itemIn = selectedInvSlot.item
            inventory.remove(selectedInvSlot.item)
            self.prBar.show()


    def onTick(self):
        # apply animations

        mouse = pygame.mouse.get_pressed()
        mousex,mousey = pygame.mouse.get_pos()

        self.animate = False
        if mouse[0] and self.getRect().collidepoint((mousex,mousey)):
            self.animate = True
        if self.animate:
            if self.ticks % 36 == 0:
                self.animIndex += 1
                if self.animIndex > len(topMillstoneSequence)-1:
                    self.animIndex = 0
            if self.ticks % 6 == 0:
                self.heightIndex += 1
                if self.heightIndex > len(sineWave)-1:
                    self.heightIndex = 0


        if mouse[2] and self.getRect().collidepoint((mousex,mousey)):
            self.onRightClick()
        if self.empty:
            self.prBar.hide()
        else:
            self.prBar.show()



        if self.holdStart is not None and self.animate:
            self.holdTime += dt
            if self.holdTime >= self.timeToComplete:
                self.prBar.hide()
                inventory.add(self.inputOutput[self.itemIn], 1, gridCoords = (self.x//BLOCK_SIZE, self.y//BLOCK_SIZE))
                self.empty = True
                self.holdStart = None
                self.holdTime = 0

        self.prBar.setAnimationFrame(int(
            self.holdTime/self.timeToComplete*len(progressBarSequence)
            ))

        self.ticks += 1

    def draw(self, surf=screen):
        if self.empty is True or self.itemIn is None:
            return super().draw(surf)

        # surf.blit(shadow, (self.x-10,self.y+60))
        surf.blit(bottomMillstoneImage, (self.x,self.y))
        smallItemIn = pygame.transform.scale_by(self.itemIn.image,0.6375)
        surf.blit(smallItemIn, (self.x+8,self.y+21))
        surf.blit(topMillstoneSequence[self.animIndex],
                   (self.x-1,self.y-sineWave[self.heightIndex]*15))

    def prepareForSaving(self):
        self.itemIn = self.itemIn.name

    @classmethod
    def loadObject(cls, objectDict):
        newMachine = millstoneMachine(objectDict["x"], objectDict["y"])
        newMachine.holdStart = objectDict["holdStart"]
        newMachine.holdTime = objectDict["holdTime"]
        newMachine.itemIn = loadItemAtrribute(objectDict, "itemIn")
        newMachine.empty = objectDict["empty"]
        newMachine.animate = objectDict["animate"]
        newMachine.ticks = objectDict["ticks"]
        newMachine.completed = objectDict["completed"]


    
        


class bowlMachine(machine):
    """Class for bowl."""
    def __init__(self, x, y):
        super().__init__(x, y, bowlImage)
        self.holdStart = None
        self.holdTime = 0
        self.timeToComplete = 10
        self.timePerItem = 5
        barX,barY = self.x-5,self.y-15
        if self.x == 0:
            barX = 0
        if self.y == 0:
            barY = 0
        self.prBar = progressBar(barX,barY)
        self.prBar.hide()
        self.empty = True
        self.itemsIn = []
        self.inputOutput = {
            (flour,waterBucket): dough,
            (waterBucket, flour): dough
        }

        self.ticks = 0
        self.possibleItemLocations = []
        self.animIndex = 0
        self.addedTimeThisFrame = False
        self.maxItems = 20

        for xx in range(23,34):
            for yy in range(35,39):
                self.possibleItemLocations.append((xx,yy))

        self.savedLoctaions = []
        for i in range(self.maxItems):
            self.savedLoctaions.append(self.possibleItemLocations[i])

    def onLeftClick(self):
        if self.holdStart is None:
            self.holdTime = 0
            self.holdStart = time()
            self.timeToComplete = self.timePerItem*len(self.itemsIn)
        if self.holdTime >= self.timeToComplete:
            self.holdTime = 0

    def onRightClick(self):
        global canPressAgain

        if not selectedInvSlot.item is None and canPressAgain and len(self.itemsIn) < self.maxItems:
            self.empty = False
            self.itemsIn.append(selectedInvSlot.item)
            inventory.remove(selectedInvSlot.item)
            self.prBar.show()
            canPressAgain = False
            if self.holdStart is not None:
                self.timeToComplete = self.timePerItem*len(self.itemsIn)
                self.updatePrBar()
            self.resetSavedLocations()

    def resetSavedLocations(self):
        self.savedLoctaions = []
        for _ in self.itemsIn:
            locationX,locationY = random.choice(self.possibleItemLocations)
            self.savedLoctaions.append((locationX,locationY))

    def onTick(self):
        mouse = pygame.mouse.get_pressed()
        mousex,mousey = pygame.mouse.get_pos()

        if self.ticks % 10 == 0:
            self.animIndex += 1
            if self.animIndex > len(bowlStickSequence)-1:
                self.animIndex = 0

        # if mouse[2] and self.getRect().collidepoint((mousex,mousey)):
        #     self.onRightClick()
        if not self.empty and self.prBar.hidden:
            self.prBar.show()
        if not (mouse[0] and self.getRect().collidepoint((mousex,mousey))):
            self.addedTimeThisFrame = False
            return
        if not mouse[0] or self.empty:
            # hide bar and stop the charging of it if not mouse pressed or 
            # it's not on the object or it's empty
            if not self.prBar.hidden:
                self.prBar.hide()
            return

        if self.holdStart is not None:
            self.holdTime += dt
            self.addedTimeThisFrame = True
            if self.holdTime >= self.timeToComplete:
                self.prBar.hide()
                if tuple(self.itemsIn) in self.inputOutput:
                    inventory.add(self.inputOutput[tuple(self.itemsIn)], 1, gridCoords = (self.x//BLOCK_SIZE,self.y//BLOCK_SIZE))
                    self.itemsIn.clear()
                else:
                    for i in self.itemsIn:
                        inventory.add(i,1, gridCoords = (self.x//BLOCK_SIZE,self.y//BLOCK_SIZE))
                    self.itemsIn.clear()
                self.empty = True
                self.holdStart = None
                self.holdTime = 0

        self.updatePrBar()

        self.ticks += 1

    def draw(self, surf=screen):
        if self.empty:
            return super().draw(surf)

        # surf.blit(shadow, (self.x-10,self.y+60))
        if self.addedTimeThisFrame:
            surf.blit(bowlBack, (self.x,self.y))

            if self.ticks % 10 == 0:
                self.savedLoctaions = []
                for i in self.itemsIn:
                    smallI = pygame.transform.scale_by(i.image, 0.3)
                    locationX,locationY = random.choice(self.possibleItemLocations)
                    surf.blit(smallI, (locationX+self.x,locationY+self.y))
                    self.savedLoctaions.append((locationX,locationY))
            else:
                for index, i in enumerate(self.itemsIn):
                    smallI = pygame.transform.scale_by(i.image, 0.3)
                    locationX,locationY = self.savedLoctaions[index]
                    surf.blit(smallI, (locationX+self.x,locationY+self.y))

            surf.blit(bowlStickSequence[self.animIndex],(self.x,self.y))
            surf.blit(bowlFront,(self.x,self.y))
        else:
            surf.blit(bowlBack, (self.x,self.y))
            for index,i in enumerate(self.itemsIn):
                smallI = pygame.transform.scale_by(i.image, 0.3)
                locationX,locationY = self.possibleItemLocations[index]
                surf.blit(smallI, (locationX+self.x,locationY+self.y))
            surf.blit(bowlStickSequence[0],(self.x,self.y))
            surf.blit(bowlFront,(self.x,self.y))

    def updatePrBar(self):
            self.prBar.setAnimationFrame(int(
        self.holdTime/self.timeToComplete*len(progressBarSequence)
        ))

    @classmethod
    def loadObject(cls, objectDict):
        newMachine = bowlMachine(objectDict["x"], objectDict["y"])
        newMachine.holdStart = objectDict["holdStart"]
        newMachine.holdTime = objectDict["holdTime"]
        if not objectDict["itemsIn"]:
            newMachine.itemsIn = []
        else:
            for itemIn in objectDict["itemsIn"]:
                newMachine.itemsIn.append(existingItems[itemIn["name"]])
        newMachine.empty = objectDict["empty"]
        newMachine.ticks = objectDict["ticks"]
        newMachine.prBar.setAnimationFrame(int(
            newMachine.holdTime/newMachine.timeToComplete*len(progressBarSequence)
            ))
        

class brickOvenMachine(machine):
    """Class for brick oven machine."""
    def __init__(self, x, y):
        super().__init__(x, y, brickOvenImage)
        self.puttableItems = { 
            # all items that you're able to put in an oven. the negative value represents
            #  the item smelting and the positive the fuel.
            # It also represents how much fuel does a smeltable 
            # use or how much power the fuel can give.
            dough: -5,
            wood: (-5,5),
            charcoal: 20,
        }

        self.produce = {
            dough: bread,
            wood: charcoal
        }

        self.fuelIn = None
        self.itemIn = None
        self.producedItem = None
        self.fuelLeft = 0
        self.holdTime = 0

        self.animIndex = 0
        self.currentSequence = None
        self.ticks = 0

        barX,barY = self.x-5,self.y-15
        if self.x == 0:
            barX = 0
        if self.y == 0:
            barY = 0
        self.prBar = progressBar(barX,barY)
        self.fuelBar = progressBar(barX, self.y+72)
        self.prBar.hide()
        self.fuelBar.hide()
        self.maxFuel = 0
        self.maxItemPower = 0
        self.justPutTheFuel = False
    def onRightClick(self):
        if self.producedItem is not None:
            return
        if selectedInvSlot.item in self.puttableItems:
            powerValue = self.puttableItems[selectedInvSlot.item]
            if isinstance(powerValue,tuple):
                if self.itemIn is None:
                    self.itemIn = selectedInvSlot.item
                    inventory.remove(selectedInvSlot.item)
                    self.holdTime = 0
                    self.justPutTheFuel = True
                    self.maxItemPower = powerValue[0]
                elif self.itemIn is not None and (
                    self.fuelIn is None or self.fuelIn == selectedInvSlot.item
                    ) and not self.justPutTheFuel:
                    self.maxFuel = powerValue[1]
                    self.fuelIn = selectedInvSlot.item
                    self.justPutTheFuel = True
                    inventory.remove(selectedInvSlot.item)
                    self.fuelLeft = powerValue[1]
                return
            if powerValue < 0 and self.itemIn is None:
                self.itemIn = selectedInvSlot.item
                inventory.remove(selectedInvSlot.item)
                self.holdTime = 0
                self.maxItemPower = powerValue
            elif powerValue > 0 and self.fuelIn is None:
                self.maxFuel = powerValue
                self.fuelIn = selectedInvSlot.item
                inventory.remove(selectedInvSlot.item)
                self.fuelLeft = powerValue


    def onLeftClick(self):
        if self.producedItem is not None:
            inventory.add(self.producedItem,1, gridCoords = (self.x//BLOCK_SIZE,self.y//BLOCK_SIZE))
            self.producedItem = None
            self.prBar.hide()
        

    def onTick(self):
        if self.currentSequence == brickOvenCookingSequence and self.ticks % 10 == 0:
            self.animIndex += 1
            if self.animIndex > len(self.currentSequence)-1:
                self.animIndex = 0

        if self.currentSequence == brickOvenCookedSequence and self.ticks % 15 == 0:
            self.animIndex += 1
            if self.animIndex > len(self.currentSequence)-1:
                self.animIndex = 0

        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        if mouse[2] and self.x < pos[0] < self.x+self.width and self.y < pos[1] < self.y+self.height:
            self.onRightClick()
        if not any(mouse):
            self.justPutTheFuel = False

        self.prBar.show() if self.itemIn is not None else None
        self.fuelBar.show() if self.fuelIn is not None else None

        if self.fuelIn is not None and self.itemIn is not None:
            self.holdTime += dt
            self.fuelLeft -= dt
            if self.fuelLeft <= 0:
                self.fuelIn = None
                self.fuelBar.hide()
                self.fuelLeft = 0
            if self.holdTime > abs(self.maxItemPower):
                self.animIndex = 0
                self.currentSequence = brickOvenCookedSequence
                if self.itemIn in self.produce:
                    self.producedItem = self.produce[self.itemIn]
                    self.itemIn = None  
                else:
                    self.producedItem = self.itemIn
                    self.itemIn = None  


        self.updateProgressBars()

        self.ticks += 1

    def draw(self, surf=screen):
        if self.itemIn is None and self.fuelIn is None:
            return super().draw(surf)

        # surf.blit(shadow, (self.x-10,self.y+60))
        if self.producedItem is None and self.itemIn is not None and self.fuelIn is not None:
            self.currentSequence = brickOvenCookingSequence
            surf.blit(self.currentSequence[self.animIndex], (self.x,self.y-40))
        elif self.producedItem is not None:
            self.currentSequence = brickOvenCookedSequence
            surf.blit(self.currentSequence[self.animIndex], (self.x,self.y-40))
        else:
            surf.blit(brickOvenImage, (self.x,self.y))
        if self.fuelIn is not None:
            smallFuelImage = pygame.transform.scale_by(self.fuelIn.image, 0.2)
            surf.blit(smallFuelImage, (self.x+16,self.y+57))
        surf.blit(brickOvenBars, (self.x,self.y))
        if self.itemIn is not None:
            smallItemImage = pygame.transform.scale_by(self.itemIn.image, 0.2375)
            surf.blit(smallItemImage, (self.x+16,self.y+35))
        if self.itemIn is None and self.producedItem is not None:
            smallItemImage = pygame.transform.scale_by(self.producedItem.image, 0.2375)
            surf.blit(smallItemImage, (self.x+16,self.y+35))

    @classmethod
    def loadObject(cls, objectDict):
        newMachine = brickOvenMachine(objectDict["x"], objectDict["y"])
        newMachine.holdTime = objectDict["holdTime"]
        newMachine.fuelLeft = objectDict["fuelLeft"]
        newMachine.animIndex = objectDict["animIndex"]
        newMachine.currentSequence = objectDict["currentSequence"]
        newMachine.maxFuel = objectDict["maxFuel"]
        newMachine.maxItemPower = objectDict["maxItemPower"]
        newMachine.itemIn = loadItemAtrribute(objectDict, "itemIn")
        newMachine.fuelIn = loadItemAtrribute(objectDict, "fuelIn")
        newMachine.ticks = objectDict["ticks"]
        newMachine.updateProgressBars()
    def updateProgressBars(self):
        if self.holdTime > 0 and self.itemIn is not None:
            self.prBar.setAnimationFrame(int(
                self.holdTime/abs(self.maxItemPower)*len(progressBarSequence)
                ))
        if self.fuelIn is not None:
            self.fuelBar.setAnimationFrame(int(
                self.fuelLeft/self.maxFuel*len(progressBarSequence)
                ))


class progressBar(entity):
    """Class for progress bars."""
    def __init__(self, x, y):
        super().__init__(x, y, 5, 90,10,progressBarSequence[0])
        self.trackedValue = 0
        self.index = 0
        self.drawCopy = self.draw
        self.hidden = False

    def changeNextFrame(self):
        """Change anuimation frame to next.""" 
        self.index += 1
        if self.index > len(progressBarSequence)-1:
            self.index = 0
        self.image = progressBarSequence[self.index]

    def setAnimationFrame(self,index):
        """Set animation frame to some value."""
        if index > len(progressBarSequence)-1:
            return
        self.index = index
        self.image = progressBarSequence[self.index]

    def hide(self):
        self.draw = self.emptyFunc
        self.hidden = True

    def show(self):
        self.draw = self.drawCopy
        self.hidden = False

    def emptyFunc(self):
        return

class shadow(entity):
    """Class for shadows of the objects. List: shadows"""
    def __init__(self, x, y):
        super().__init__(x, y, -3, 100, 40, shadowImage)
        shadows.append(self)

class transition:
    """Class for transitions. List: transitions"""
    def __init__(self, startGridx, startGridy, endGridx, endGridy, image):
        self.startGridx = startGridx
        self.startGridy = startGridy
        self.endGridx = endGridx
        self.endGridy = endGridy

        # transition properties
        self.transitionTime = 1
        self.currentFrame = 0
        self.transitionFrames = self.transitionTime/TIME_PER_FRAME
        self.maxScale = 2
        self.startScale = 0.4
        self.scale = self.startScale

        # random start end end locations
        self.startX = random.randint(startGridx*BLOCK_SIZE-BLOCK_SIZE//2, (startGridx+1)*BLOCK_SIZE-1+BLOCK_SIZE//2)
        self.startY = random.randint(startGridy*BLOCK_SIZE-BLOCK_SIZE//2, (startGridy+1)*BLOCK_SIZE-1+BLOCK_SIZE//2)
        self.endX = endGridx*BLOCK_SIZE-BLOCK_SIZE//2
        self.endY = endGridy*BLOCK_SIZE-BLOCK_SIZE//2
        self.startPos = pygame.Vector2(self.startX,self.startY)
        self.endPos = pygame.Vector2(self.endX,self.endY)

        # step per frame
        self.stepX = (self.endX - self.startX)/self.transitionFrames
        self.stepY = (self.endY - self.startY)/self.transitionFrames

        # scale step per frame
        self.scaleStep = (self.maxScale - self.startScale)/self.transitionFrames*3

        self.originalImage = image
        self.entity = entity(self.startX, self.startY, image=image)


        self.entity.draw = self.entity.drawOnOverlay
        transitions.append(self)

    def applyTransition(self):
        self.currentFrame += 1
        normalizedTime = min(1, self.currentFrame / self.transitionFrames)

        self.currentPos = self.startPos.lerp(self.endPos, normalizedTime)

        if normalizedTime < 0.2:
            scale = self.startScale + (self.maxScale - self.startScale) * (normalizedTime / 0.2)
        elif normalizedTime > 0.8:
            scale = self.startScale + (self.maxScale - self.startScale) * ((1 - normalizedTime) / 0.2)
        else:
            scale = self.maxScale

        scaledImg = pygame.transform.scale_by(self.originalImage, scale)
        rect = scaledImg.get_rect(center=self.currentPos)

        self.entity.image = scaledImg
        self.entity.x, self.entity.y = rect.topleft

        if normalizedTime >= 1:
            entities.remove(self.entity)
            transitions.remove(self)      
        
class popUp:
    def __init__(self, text, textSize, textColor, pos, duration=4.0, stayTime=0.5, floatSpeed=30.0):
        """Class for pop ups on the screen."""

        self.image = renderBigText(text, textColor, textSize).convert_alpha()
        self.x, self.y = pos

        # centralize the pos
        self.x -= self.image.get_width()//2

        self.duration = duration
        self.stayTime = stayTime
        self.floatSpeed = floatSpeed
        self.layer = 5
        
        self.elapsedTime = 0
        self.alpha = 255
        self.fadeSpeed = 255 / duration if duration > 0 else 255
        self.isFinished = False
        
        # Register to global tracking lists
        popUps.append(self)
        entities.append(self)

    def update(self, dt):
        """Updates timing, upward floating, fading, and self-cleanup."""
        if self.isFinished:
            return

        self.elapsedTime += dt

        # Wait until stayTime has passed before moving and fading
        if self.elapsedTime >= self.stayTime:
            self.y -= self.floatSpeed * dt
            self.alpha -= self.fadeSpeed * dt

            if self.alpha <= 0:
                self.alpha = 0
                self.isFinished = True
                self.destroy()
                return

            self.image.set_alpha(int(self.alpha))

    def draw(self, surface=transitionScreen):
        if not self.isFinished:
            surface.blit(self.image, (self.x, self.y))

    def destroy(self):
        """Removes the popup from global lists safely."""
        if self in popUps:
            popUps.remove(self)
        if self in entities:
            entities.remove(self)

# lists
entities:list[entity] = []
colliders:list[obstacle] = []
fields:list[field] = []
plants:list[wheat] = []
areas:list[area] = []
slots:list[slot] = []
sellPanelObjects:list[sellPanelObject] = []
sellPanelItems:list[sellPanelItem] = []
sellPanelButtons:list[sellPanelButton] = []
machines:list[machine] = []
invControlButtons:list[entity] = []
shadows: list[shadow] = []
existingItems:dict[str, item] = {}
transitions:list[transition] = []
popUps:list[popUp] = []

# create slots
for page in range(6):
    for slotX in range(80,1080, 200):
        slot(page*1280+slotX,10,page+1)

wheatSeeds = item(
    wheatSeedsImage,
    "wheat seeds",
    description="""Small, golden grains ready to be planted into soil
to grow wheat.""",
)

wheatBundle = item(
    wheatBundleImage,
    "wheat bundle",
    description="""Treat every seed with care and it will reward you with this.
A bundle of harvested wheat, ready to be processed.""",
)

farmland = item(
    soilImage,
    "farmland",
    description="""This dark earth is my whole life. Treat her with respect,
and she'll take care of your family for generations.
Tilled, rich, beautiful soil prepared for planting.""",
)

woodAsh = item(
    woodAshImage,
    "wood ash",
    description="""The powder left behind after burning wood, useful as
fertilizer. With it, wheat grows 2 times faster than usual.""",
)

millstone = item(
    millstoneImage,
    "millstone",
    description="""A heavy stone tool used for grinding wheat grains
into fine flour.
Flour might come out with a slight taste of sweat in it,
but don't worry - it's only the first few times.""",
    machineClass=millstoneMachine,
)

flour = item(
    flourImage,
    "flour",
    description="""Hard labor with a millstone finally paid off with this
magical white dust.
A fundamental ingredient used to make dough and bread.""",
)

waterBucket = item(
    waterBucketImage,
    "bucket of water",
    description="""A bucket filled with clean water, straight from a nearby
river, essential for life.
You can see your reflection in it more clearly than in a
mirror! Use it on the field and wheat there will grow 1.4 times faster!""",
)

bowl = item(
    bowlImage,
    "bowl",
    description="""A simple tool, but how useful is it! Used for combining
ingridients. Mix flour and water in it, to form dough.""",
    machineClass=bowlMachine,
)

dough = item(
    doughImage,
    "dough",
    description="""Warm beneath your hands. You can feel the life in it as
you knead, which is waiting for the heat of the oven.""",
)

brickOven = item(
    brickOvenImage,
    "brick oven",
    description="""An oven assembled using bricks. Built
for baking bread. A very powerful machine, just sometimes needs a lot of fuel. 
When placed near farmland, it defertilizes the soil, doubling wheat growth time.""",
    machineClass=brickOvenMachine,
)

bread = item(
    breadImage,
    "bread",
    description="""Ah! Love the taste of it. I will never forget what it
was like to taste that for the first time.
A freshly baked, golden-brown loaf of bread offering
nutritious sustenance.""",
)

wood = item(
    woodImage,
    "wood",
    description="""Logs, harvested staright from a forest. Can be made into
charcoal using the oven.""",
)

charcoal = item(
    charcoalImage,
    "charcoal",
    description="""Lightweight black carbon produced by heating wood,
serving as a long-burning fuel. Can be grinded into
wood ash using millstone.""",
)

# create a grid of area obbjects:
for gy in range(GRID_HEIGHT):
    for gx in range(GRID_WIDTH):
        area(gx,gy)

farmer = entity(1200,360,image=farmerImage)
rightButtonEnt = entity(990,50,image=rightButton)
leftButtonEnt = entity(30,50,image=leftButton)


rightButtonEnt.getRect = rightButtonEnt.getInvRect
leftButtonEnt.getRect = leftButtonEnt.getInvRect
entities.remove(rightButtonEnt)
entities.remove(leftButtonEnt)

# sell panel things
selectedSellableItem = sellPanelItem(60,80,"wheat bundle",wheatBundle, image=wheatBundleImage)
sellPanelItem(160,80,"wheat seeds",wheatSeeds, image=wheatSeedsImage, buyable=True)
sellPanelItem(260,80,"farmland", farmland, image=soilImage, buyable=True, sellable=False)
sellPanelItem(360, 80, "wood ash", woodAsh, image=woodAshImage, buyable=True, sellable=False)
sellPanelItem(460,80,"millstone", millstone, image=millstoneImage, buyable=True, sellable=True)
sellPanelItem(60, 180, "flour", flour, image=flourImage, buyable=False, sellable=True)
sellPanelItem(160, 180, "bucket of water", waterBucket, image=waterBucketImage, buyable=True, sellable=False)
sellPanelItem(260,180, "bowl", bowl, sellable=True,buyable=True, image=bowlImage)
sellPanelItem(360,180, "dough", dough, image=doughImage) 
sellPanelItem(460,180, "brick oven", brickOven, image=brickOvenImage, buyable=True, sellable=True)
sellPanelItem(60, 280, "bread", bread, sellable=True, buyable=False, image=breadImage) 
sellPanelItem(160, 280, "wood", wood, buyable=True, sellable=False, image=woodImage)
sellPanelObject(0,0,-1,image=sellPanelBG)

def sellCheck():
    if selectedSellableItem is None:
        return False
    
    if selectedSellableItem.item not in inventory.items:
        return False

    if not selectedSellableItem.sellable:
        return False

    return True

def buyCheck(amt=1):
    amt = int(amt)
    if selectedSellableItem is None:
        return False
    if not selectedSellableItem.buyable:
        return False
    if inventory.coins < BUY_PANEL_PRICE_LIST[selectedSellableItem.name]*amt:
        return False


    return True

def sell1():
    if not sellCheck():
        return
    
    inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]
    inventory.remove(selectedSellableItem.item)
    selectedSellableItem.select()

def buy1():
    if not buyCheck():
        return

    inventory.coins -= BUY_PANEL_PRICE_LIST[selectedSellableItem.name]
    inventory.add(selectedSellableItem.item,1, gridCoords = (selectedSellableItem.x//BLOCK_SIZE, selectedSellableItem.y//BLOCK_SIZE))
    selectedSellableItem.select()



def sellAll():
    if not sellCheck():
        return

    inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]*(
        inventory.items[selectedSellableItem.item]
        )
    inventory.items[selectedSellableItem.item] = 0
    inventory.popFromItems(selectedSellableItem.item)
    selectedSellableItem.select()


def buyMax():
    if selectedSellableItem.name not in BUY_PANEL_PRICE_LIST:
        return False

    maxAmount = inventory.coins//BUY_PANEL_PRICE_LIST[selectedSellableItem.name]
    
    if not buyCheck(maxAmount):
        return

    inventory.coins -= BUY_PANEL_PRICE_LIST[selectedSellableItem.name]*maxAmount
    inventory.add(selectedSellableItem.item,maxAmount, gridCoords = (selectedSellableItem.x//BLOCK_SIZE, selectedSellableItem.y//BLOCK_SIZE))
    selectedSellableItem.select()


def sellCustom():
    global actionOnInputEnd,inputValue

    if not selectedSellableItem.sellable:
        return

    def sellCustomAmt(amt):
        global actionOnInputEnd,inputValue

        if not sellCheck():
            return
        
        amt = int(amt)
        if inventory.items[selectedSellableItem.item] < amt:
            return

        inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]*amt
        inventory.items[selectedSellableItem.item] -= amt
        if inventory.items[selectedSellableItem.item] == 0:
            inventory.popFromItems(selectedSellableItem.item)
            selectedSellableItem.select()

        actionOnInputEnd = None

    actionOnInputEnd = sellCustomAmt
    inputValue = "-"
    selectedSellableItem.select()


def buyCustom():
    global actionOnInputEnd,inputValue

    if not selectedSellableItem.buyable:
        return

    def buyCustomAmt(amt):
        global actionOnInputEnd

        if not buyCheck(amt):
            return

        amt = int(amt)
        inventory.coins -= BUY_PANEL_PRICE_LIST[selectedSellableItem.name]*amt
        inventory.add(selectedSellableItem.item, amt, gridCoords = (selectedSellableItem.x//BLOCK_SIZE, selectedSellableItem.y//BLOCK_SIZE))
        actionOnInputEnd = None

    actionOnInputEnd = buyCustomAmt
    inputValue = "-"
    selectedSellableItem.select()

loadClassesDict = {
    "field": field,
    "brickOvenMachine": brickOvenMachine,
    "bowlMachine": bowlMachine,
    "millstoneMachine": millstoneMachine,
}

# buttons
sell1Button = sellPanelButton(60,560-192, "sell", image=sell1ButtonImage)
sellCustomButton = sellPanelButton(224,560-192, "sell", image=sellCustomButtonImage)
sellAllButton = sellPanelButton(388,560-192, "sell", image=sellAllButtonImage)
buy1Button = sellPanelButton(60,560-96, "buy",image=buy1Image)
buyCustomButton = sellPanelButton(224,560-96, "buy",image=buyCustomImage)
buyMaxButton = sellPanelButton(388, 560-96, "buy",image=buyMaxImage)
backButton = sellPanelButton(0,0, "special", image=backButtonImage)
sell1Button.action = sell1
sellAllButton.action = sellAll
sellCustomButton.action = sellCustom
buy1Button.action = buy1
buyCustomButton.action = buyCustom
buyMaxButton.action = buyMax

descriptionPanel = (635,560)
descriptionTitle = sellPanelObject(317+descriptionPanel[0],60)
descriptionLines = [
sellPanelObject(30+descriptionPanel[0],130),
sellPanelObject(30+descriptionPanel[0], 130+FONT_HEIGHT),
sellPanelObject(30+descriptionPanel[0], 130+FONT_HEIGHT*2),
sellPanelObject(30+descriptionPanel[0], 130+FONT_HEIGHT*3),
sellPanelObject(30+descriptionPanel[0], 130+FONT_HEIGHT*4),
]

descriptionPriceLines = [
sellPanelObject(30+descriptionPanel[0], 300),
sellPanelObject(30+descriptionPanel[0], 300+FONT_HEIGHT),
sellPanelObject(30+descriptionPanel[0], 300+FONT_HEIGHT*2),
sellPanelObject(30+descriptionPanel[0], 300+FONT_HEIGHT*3),
]
buyMaxLine = sellPanelObject(30+descriptionPanel[0], 300+FONT_HEIGHT*4)
sellAllLine = sellPanelObject(30+descriptionPanel[0], 300+FONT_HEIGHT*5)
buyCustomLine = sellPanelObject(912,300)

highlightFrame = sellPanelObject(-950,-950,layer=-1,image=highlightFrameImage)
SELL_PANEL_PRICE_LIST = {
    "millstone": 75,
    "flour": 15,
    "wheat seeds": 1,
    "bowl": 175,
    "wheat bundle": 5,
    "dough": 35,
    "brick oven": 450,
    "bread": 50,
}
BUY_PANEL_PRICE_LIST = {
    "wheat seeds": 1,
    "farmland": 30,
    "wood ash": 20,
    "bucket of water": 10,
    "millstone": 100,
    "bowl": 215,
    "brick oven": 500,
    "wood": 15
}

# tuple of keys here means key combination
KEY_BINDS = {
    pygame.K_ESCAPE: lambda: globals().__setitem__("sellPanelOpened",False),
    pygame.K_RIGHT: lambda: inventory.changePage("right"),
    pygame.K_LEFT: lambda: inventory.changePage("left"),
    (pygame.K_r, pygame.K_LCTRL, pygame.K_LALT): resetSavedGameContext,
    (pygame.K_m, pygame.K_i, pygame.K_l, pygame.K_o, pygame.K_n): lambda: setattr(inventory, "coins", inventory.coins + 1000)
}

NUMBERS = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9,
}

KP_NUMBERS = {
    pygame.K_KP0: 0,
    pygame.K_KP1: 1,
    pygame.K_KP2: 2,
    pygame.K_KP3: 3,
    pygame.K_KP4: 4,
    pygame.K_KP5: 5,
    pygame.K_KP6: 6,
    pygame.K_KP7: 7,
    pygame.K_KP8: 8,
    pygame.K_KP9: 9,
}

def flickUpdateFrame():
    """Flick 'updateFrame' back on."""
    global updateFrame
    updateFrame = True

def breakPlant(fieldUsed):
    """Breaks the plant, mouse is hovering on."""
    if fieldUsed is None:
        return
    if fieldUsed.plant is None:
        return
    fieldUsed.plant.breakMyself()
    flickUpdateFrame()

def placePlant(fieldUsed):
    """"Places the plant where the mouse is pointing."""

    if fieldUsed is None:
        return 

    if fieldUsed.plant is not None:
        return

    if inventory.remove(wheatSeeds):
        wheat(fieldUsed)
    flickUpdateFrame()


def saveGame():
    """Saves the game after you exit."""
    invItems = []   
    for i,count in inventory.items.items():
        invItems.append((i.name,count,slots.index(i.slot)))
    
    with open("saveFile.txt", "w") as saveFile:
        saveFile.write(str(invItems) + ";" + "\n")

    with open("saveFile.txt", "a+") as saveFile:
        saveFile.write(str(inventory.coins) + ";" + "\n")
        for f in fields:
            saveFile.write(f.toJSON() + ";" + "\n")
        for m in machines:
            saveFile.write(m.toJSON() + ";" + "\n")

def mouseScroll(directionFactor:int) -> None:
    """Covers mouse wheel controls."""
    global selectedInvSlot,sellPanelOpened,selectedSellableItem,actionOnInputEnd

    actionOnInputEnd = None

    currentSlotIndex = slots.index(selectedInvSlot)
    currentPageSlotIndexRange = [(inventory.page-1)*SLOTS_PER_PAGE, inventory.page*SLOTS_PER_PAGE-1]

    if currentPageSlotIndexRange[0] <= currentSlotIndex + directionFactor <= currentPageSlotIndexRange[1]:
        selectedInvSlot = slots[currentSlotIndex + directionFactor]
    elif currentSlotIndex + directionFactor > currentPageSlotIndexRange[1]:
        selectedInvSlot = slots[currentPageSlotIndexRange[0]]
    else:
        selectedInvSlot = slots[currentPageSlotIndexRange[1]]

    syncSellableSelectWithInvSelect()

def syncSellableSelectWithInvSelect():
    """Sets the selected sellable to the item selected in inv."""
    global selectedSellableItem

    if sellPanelOpened:
        for spi in sellPanelItems:
            if spi.item == selectedInvSlot.item:
                selectedSellableItem = spi
                selectedSellableItem.select()
                break

def setSlotIndexOnPage(index):
    """Sets selected slot to the one behind the page index given. 
    Example: index = 4, inv.page = 5, will set selected inv slot to
    slots[(5-1)*SLOTS_PER_PAGE(5)+4] = slots[24]."""
    global selectedInvSlot

    if not 1 <= index <= 5:
        return

    selectedInvSlot = slots[((inventory.page-1)*SLOTS_PER_PAGE)+index-1]
    syncSellableSelectWithInvSelect()



def mouseControl():
    """Covers everything that is activated with mouse."""
    global canPressAgain,newFarmlandCreated,selectedInvSlot,justExited,actionOnInputEnd

    mouse = pygame.mouse.get_pressed()
    mousex,mousey = pygame.mouse.get_pos()

    if mouse[2] and 0 < mousex < WIDTH and 0 < mousey < HEIGHT:
        if not sellPanelOpened:
            hoverField:field = findFieldByCoords((mousex,mousey))
            if hoverField is None and farmland in inventory.items and selectedInvSlot == farmland.slot:
                fieldx,fieldy = mousex//BLOCK_SIZE,mousey//BLOCK_SIZE
                if 0 <= fieldx <= 12 and 0 <= fieldy <= 6:
                    for m in machines:
                        if m.x//BLOCK_SIZE == fieldx and m.y//BLOCK_SIZE == fieldy:
                            return
                    newField = field(fieldx,fieldy)
                    for m in machines:
                        if isinstance(m, brickOvenMachine) and measureBlockDistance(
                            newField.x,newField.y,m.x,m.y) <= 1:
                            newField.multiplier = 0.5
    
                    inventory.remove(farmland)
                    newFarmlandCreated = True
            elif not newFarmlandCreated :
                if selectedInvSlot == wheatSeeds.slot and not mouse[0]:
                    placePlant(hoverField)
                elif selectedInvSlot == woodAsh.slot and hasattr(
                    hoverField, "fertilized") and not hoverField.fertilized:
                    hoverField.fertilize()
                    inventory.remove(woodAsh)
                elif selectedInvSlot == waterBucket.slot and hasattr(
                    hoverField, "wet") and not hoverField.wet:
                    hoverField.makeWet()
                    inventory.remove(waterBucket)
                elif selectedInvSlot.item is not None and selectedInvSlot.item.machineClass is not None and hoverField is None and 0 <= mousey//BLOCK_SIZE < 7 and 0 <= mousex//BLOCK_SIZE <= 12 and canPressAgain:
                    if not (int(mousex//BLOCK_SIZE*BLOCK_SIZE),int(mousey//BLOCK_SIZE*BLOCK_SIZE)) in [
                        (ma.x,ma.y) for ma in machines]:
                        selectedInvSlot.item.machineClass(mousex//BLOCK_SIZE*BLOCK_SIZE,
                                                          mousey//BLOCK_SIZE*BLOCK_SIZE)
                        inventory.remove(selectedInvSlot.item)
                        canPressAgain = False

            for m in machines:
                if m.getRect().collidepoint((mousex,mousey)):
                    m.onRightClick()
    if mouse[0] and 0 < mousex < WIDTH and 0 < mousey < HEIGHT:
        if 0 < mousex < WIDTH and 560 < mousey < HEIGHT:
            # in inv panel
            for s in slots:
                if s.getRect().collidepoint((mousex,mousey)):
                    selectedInvSlot = s
                    return

            if rightButtonEnt.getRect().collidepoint((mousex,mousey)) and canPressAgain:
                inventory.changePage("right")
                canPressAgain = False

            if leftButtonEnt.getRect().collidepoint((mousex,mousey)) and canPressAgain:
                inventory.changePage("left")                
                canPressAgain = False

        if not sellPanelOpened:
            # in screen
            hoverField = findFieldByCoords((mousex,mousey))
            if hoverField is None:
                for m in machines:
                    if m.getRect().collidepoint((mousex,mousey)):
                        m.onLeftClick()
                        break
            if not justExited:
                breakPlant(hoverField)            
            if farmer.getRect().collidepoint(mousex,mousey) and canPressAgain:
                showSellPanel()
        else:
            # in sell panel
            for i in sellPanelItems:
                i:sellPanelItem
                if i.getRect().collidepoint(mousex,mousey):
                    i.select()

            if canPressAgain:
                for SPButton in sellPanelButtons:
                    if SPButton.getRect().collidepoint(mousex,mousey) and not SPButton.disabled:
                        savedSlot = selectedSellableItem.item.slot
                        if selectedSellableItem.item in inventory.items:
                            savedCount = inventory.items[selectedSellableItem.item]
                        SPButton.action()
                        canPressAgain = False
                        if SPButton.buttonType == "sell":
                            try:
                                inventory.items[selectedSellableItem.item]
                            except:
                                currentCount = 0
                            else:
                                currentCount = inventory.items[selectedSellableItem.item]
                            for _ in range(min(20, (savedCount-currentCount))):
                                transition(
                                    int((savedSlot.x+BLOCK_SIZE*1.2)//BLOCK_SIZE), 
                                    int((sellPanel.get_height() + BLOCK_SIZE)//BLOCK_SIZE),
                                    (selectedSellableItem.x+BLOCK_SIZE*1.5)//BLOCK_SIZE,
                                    (selectedSellableItem.y+BLOCK_SIZE*1.5)//BLOCK_SIZE,
                                    selectedSellableItem.image
                                )
                        break
                    elif SPButton.getRect().collidepoint(mousex,mousey) and SPButton.disabled:
                        addPopUpMessage(SPButton.disabledText)

    elif not any(mouse):
        canPressAgain = True
        newFarmlandCreated = False
        justExited = False

    if any(mouse) and (not sellCustomButton.getRect().collidepoint((mousex,mousey)) or not buyCustomButton.getRect(
    ).collidepoint((mousex,mousey))) and canPressAgain:
        actionOnInputEnd = None
        canPressAgain = False



def showSellPanel():
    """Shows the 'sell and buy' panel."""
    global sellPanelOpened

    sellPanelOpened = True

def hideSellPanel():
    """Hides the 'sell and buy' panel."""
    global sellPanelOpened,justExited

    sellPanelOpened = False
    justExited = True

backButton.action = hideSellPanel

def control():
    """Covers the control of the game."""
    global inputValue,canTypeAgain, actionOnInputEnd

    keys = pygame.key.get_pressed()

    for k,action in KEY_BINDS.items():
        if not isinstance(k, tuple) and keys[k] and canTypeAgain:
            action()
            canTypeAgain = False
        elif isinstance(k, tuple) and canTypeAgain:
            if all([keys[actualKey] for actualKey in k]):
                action()
                canTypeAgain = False
        
    if not sellPanelOpened:
        for key,num in NUMBERS.items():
            if keys[key]:
                inventory.changePage(num)

    for kpKey, kpNum in KP_NUMBERS.items():
        if keys[kpKey]:
            actionOnInputEnd = None
            setSlotIndexOnPage(kpNum)

    # input
    if actionOnInputEnd is not None and canTypeAgain:
        for key,num in NUMBERS.items():
            if keys[key]:
                if inputValue == "-":
                    inputValue = str(num)
                    canTypeAgain = False
                else:
                    inputValue = inputValue + str(num)
                    canTypeAgain = False

        if keys[pygame.K_RETURN]:
            actionOnInputEnd(inputValue)
            inputValue = ""
            canTypeAgain = False

        if keys[pygame.K_BACKSPACE]:
            if keys[pygame.K_LCTRL]:
                inputValue = "-"
                canTypeAgain = False
            else:
                inputValue = inputValue[:-1]
                canTypeAgain = False

    if actionOnInputEnd is not None:
        if actionOnInputEnd.__name__ == "sellCustomAmt":
            buyCustomLine.image = renderText(
                actionOnInputEnd.__name__[:-9] + " x" + inputValue + " for " + str(
                    SELL_PANEL_PRICE_LIST[selectedSellableItem.name]*inputValueToInt()), "black")
        elif actionOnInputEnd.__name__ == "buyCustomAmt":
            buyCustomLine.image = renderText(
                actionOnInputEnd.__name__[:-9] + " x" + inputValue + " for " + str(
                    BUY_PANEL_PRICE_LIST[selectedSellableItem.name]*inputValueToInt()), "black")
    else:
        buyCustomLine.image = renderText("","black")
    


    # reset can type again
    if not any(keys):
        canTypeAgain = True



    mouseControl()

def render():
    """Covers the rendering of the game."""
    global updateFrame

    # if not updateFrame:
    #     return
    transitionScreen.fill((0,0,0,0))

    screen.fill("white")
    entities.sort(key=lambda x: x.layer)
    for ent in entities:
        if isinstance(ent,wheat):
            pass
        ent.draw()
    updateFrame = False

    inventory.items = dict(sorted(inventory.items.items(),key=lambda x: x[0].layer))
    invPanel.fill(INVENTORY_BG)
 
    inventory.draw()
    screen.blit(invPanel,(0,HEIGHT-invPanel.get_height()))

    sellPanelObjects.sort(key=lambda x: x.layer)
    if sellPanelOpened:
        sellPanel.fill((190,90,45))
        for s in sellPanelObjects:
            s.draw()

        screen.blit(sellPanel,(0,0))

    screen.blit(transitionScreen, (0,0))

def applyTransitions():
    for t in transitions:
        t.applyTransition()

def handleMusic():
    global musicThemes, lastMusicTime, intervalBetweenMusic, currentMusicInterval, soundPlaying, lastMusicEndTime

    if soundPlaying is not None and time() - lastMusicTime > soundPlaying.length:
        soundPlaying = None
        lastMusicEndTime = time()

    elif time() - lastMusicEndTime > currentMusicInterval and soundPlaying is None:
        random.choice(musicThemes).play()
        currentMusicInterval = random.randint(intervalBetweenMusic[0], intervalBetweenMusic[1])




def update():
    for pl in plants:
        pl.increaseTimePlanted()

    for m in machines:
        m.onTick()

    for p in popUps:
        p.update(dt)

    applyTransitions()
    handleMusic()

selectedInvSlot = slots[0]
screen.fill("white")
loadGame()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            mouseScroll(event.y)

    start = time()

    control()
    update()
    render()

    pygame.display.flip()

    clock.tick(MAX_FPS)
    dt = time() - start

saveGame()

pygame.quit()