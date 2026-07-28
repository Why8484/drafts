import pygame
from  time import time
import random
import os
import math

pygame.init()
HEIGHT = 720
WIDTH = 1280
screen = pygame.display.set_mode((WIDTH,HEIGHT))
invPanel = pygame.Surface((WIDTH, HEIGHT//5))
sellPanel = pygame.Surface((WIDTH,HEIGHT*(4/5)))
sellPanelOpened = False
clock = pygame.time.Clock()
pygame.display.set_caption("farm")
INVENTORY_BG = (245,241,127)
MAX_FPS = 120
BLOCK_SIZE = 80
GRID_WIDTH = int(WIDTH/BLOCK_SIZE) #16
GRID_HEIGHT = int(HEIGHT/BLOCK_SIZE)  #9
font = pygame.font.SysFont("comicsansms",22)
bigFont = pygame.font.SysFont("comicsansms",44)
running = True
updateFrame = True
selectedSellableItem = None
canPressAgain = True
inputValue = ""
typingPosition = 780,100
actionOnInputEnd = None
canTypeAgain = True

def renderText(text:str,color):
    """Returns a surface of rendered text."""

    surf = font.render(text,False,color)
    return surf


def renderBigText(text:str,color):
    """Returns a surface of rendered text in big font."""

    surf = bigFont.render(text,False,color)
    return surf

def displayCoinsAmount():
    """Returns coin amount as 1M or 1K."""

    coinsAmt = inventory.coins

    numbers = {
        10**3: "K",
        10**6: "M",
        10**9: "T"
    }

    if coinsAmt < list(numbers.keys())[0]:
        return coinsAmt

    for n,letter in numbers.items():
        if math.floor(coinsAmt/n) < 1000:
            nDigits = 3 - len(list(str(round(coinsAmt/n))))
            returnValue = str(round(coinsAmt/n,ndigits=nDigits))
            if nDigits == 0:
                returnValue = str(round(coinsAmt/n))
            return returnValue + letter

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
    """Loads all images from folder skipping the fikles that are not images.
    Params:
        folderPath: path of the folder.
    Returns:
        list with pygame.Surface objects."""

    imageSequence = []
    joindeFolderPath = os.path.join("assets",folderPath)
    for fileName in os.listdir(joindeFolderPath):
        joinedPath = os.path.join(joindeFolderPath,fileName)
        if joinedPath.endswith((".png",".jpg","jpeg")):
            imageSequence.append((loadImage(joinedPath,False)))

    return imageSequence

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

def findAreaByGridCoords(gx,gy):
    """Finds an area object that overlaps coords given.
    Params:
        x and y: coords.
    Returns:
        area object that overlaps given coords."""

    return areas[gy*GRID_WIDTH+gx]

def findFieldByCoords(x,y):
    """Finds an field object that overlaps coords given.
    Params:
        x and y: coords.
    Returns:
        field object that overlaps given coords.
        None:if none of the fields overlap these coords."""

    x = x // BLOCK_SIZE
    y = y // BLOCK_SIZE

    areaOnCoords = findAreaByGridCoords(x,y)
    return areaOnCoords.object

def findFieldByGridCoords(gx,gy):
    """Finds an field object that has grid coordinates given.
    Params:
        gx and gy: grid coords of the wanted field object.
    Returns:
        field object with given grid coords.
        None: if there's no field with grid coords given."""

    return findAreaByGridCoords(gx,gy).object

# lists
entities = []
colliders = []
fields = []
plants = []
areas = []
slots = []
sellPanelObjects = []
sellPanelItems = []
sellPanelButtons = []

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

    for item,chance in chances.items():
        cumulativeChance += chance
        if roll <= cumulativeChance:
            return item

    return None


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
                print("Invalid entity init input")
                return
            self.image = createDefaultImage(self.width,self.height,
                                            (random.randint(0,255),random.randint(0,255),random.randint(0,255)),
                                            (random.randint(0,255),random.randint(0,255),random.randint(0,255),))
        else:
            self.image:pygame.Surface
            self.width = self.image.get_width()
            self.height = self.image.get_height()

        # sides
        self.updateSides()

        entities.append(self)

    def draw(self):
        screen.blit(self.image,(self.x,self.y))

    def updateSides(self):
        self.center = self.x+self.width//2,self.y+self.height//2
        self.centerx,self.centery = self.center
        self.left = self.x
        self.right = self.x+self.width
        self.top = self.y
        self.bottom = self.y+self.height

    def getRect(self):
        return pygame.Rect(self.x,self.y,self.width,self.height)

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

        super().__init__(x, y, -5,BLOCK_SIZE,BLOCK_SIZE,None)
        areas.append(self)
        entities.remove(self)
    def draw(self):
        return

class field(entity):
    """Field object on which you can plant plants on. List: fields."""
    def __init__(self, gridx,gridy):


        x = gridx*BLOCK_SIZE
        y = gridy*BLOCK_SIZE

        self.plant = None

        self.gridx = gridx
        self.gridy = gridy
        findAreaByGridCoords(gridx,gridy).object = self

        super().__init__(x, y, 0, image=soilImage)
        fields.append(self)

class wheat(entity):
    """Wheat object that grows on certain field. List: plants."""
    def __init__(self, field:field):
        self.field = field
        field.plant = self
        self.growthSequence = wheatGrowth
        self.timePlanted = 0
        x,y = field.x,field.y-40
        self.phase = 0
        self.growthTime = [1,1,1]
        super().__init__(x,y, 1, BLOCK_SIZE, BLOCK_SIZE, self.growthSequence[self.phase])
        plants.append(self)
    def increaseTimePlanted(self):
        """Adds dt to time planted."""
        self.timePlanted += dt
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
                inventory.add(wheatSeeds,rollFromChance({0: 60, 1: 40}))
            case 1:
                inventory.add(wheatSeeds,rollFromChance({0: 10, 1: 65, 2: 25}))
            case 2:
                inventory.add(wheatSeeds, rollFromChance({1: 50, 2: 35, 3: 15}))
            case 3:
                inventory.add(wheatSeeds, rollFromChance({2: 70, 3: 30}))
                inventory.add(wheatBundle, 1)

class inventory:
    items = {}
    coins = 0

    @classmethod
    def add(cls,item,count):
        """
        Adds some amount of some item to the items dict.
        Params:
            item: item you wanna add.
            count: how many of these items you wanna add.
        Returns:
            none.
        """
        if count == 0:
            return

        if item in cls.items.keys():
            cls.items[item] += count
        else:
            cls.items[item] = count
            emptySlot = slot.findNextEmpty()
            emptySlot.item = item
            item.slot = emptySlot
        flickUpdateFrame()

    @classmethod
    def draw(cls):
        """Draws every item in self.items."""
        for i,count in cls.items.items():
            i.draw(i.slot.x,i.slot.y)
            invPanel.blit(renderText("x"+str(count),"black"),(i.slot.x+BLOCK_SIZE/2,BLOCK_SIZE+i.title.get_height()))

        invPanel.blit(coinImage,(1080,invPanel.get_height()-90))
        invPanel.blit(renderBigText(str(displayCoinsAmount()),"black"),(1165,invPanel.get_height()-60))

    @classmethod
    def remove(cls,item):
        """Removes the one piece given iem from inventory.
        Returns true if there was that item in inventory and false if there wasn't."""
        if item not in cls.items.keys():
            return False

        cls.items[item] -= 1
        cls.popFromItems(item)
        return True
    
    @classmethod
    def popFromItems(cls,item):
        """Pops the item so it doesnt show up in inv panel. 
        Usage: when there is 0 of this item left."""
        if cls.items[item] == 0:
            item.slot.item = None
            item.slot = None
            cls.items.pop(item)



class item:
    """Class for items that show up in the inventory space. List: none."""
    def __init__(self, image, name,layer=0):
        self.image = image
        self.layer = layer
        self.name = name
        self.slot = None
    def draw(self,x,y):
        invPanel.blit(self.image,(x,y))
        self.title = renderText(self.name,"black")
        invPanel.blit(self.title,(x,y+BLOCK_SIZE))

class slot:
    """Class for inventory slots. List: slots."""
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.item = None
        slots.append(self)

    @classmethod
    def findNextEmpty(cls):
        for s in slots:
            if s.item == None:
                return s

class sellPanelObject(entity):
    """Class for objects on the sell and buy panel. List: sellPanelObjects."""
    def __init__(self, x, y, layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        entities.remove(self)
        sellPanelObjects.append(self)
    def draw(self):
        sellPanel.blit(self.image,(self.x,self.y))

class sellPanelItem(sellPanelObject):
    """Class for sellable items in sell panel. List: sellPanelItems."""
    def __init__(self, x, y, name, normalItem, layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        self.selected = False
        self.name = name
        self.item = normalItem
        sellPanelItems.append(self)
    def select(self):
        """select this item as the selectedSellable."""
        global selectedSellableItem,highlightFrame

        self.selected = True
        selectedSellableItem = self
        highlightFrame.x,highlightFrame.y = self.x-5,self.y-5

class sellPanelButton(sellPanelObject):
    """Class for buttons like sellAll,sell1 etc. List: sellPanelButtons."""
    def __init__(self, x, y, layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        sellPanelButtons.append(self)
    def action(self):
        pass

# create slots
for x in range(40,1280,200):
    slot(x,0)

wheatSeeds = item(wheatSeedsImage,"wheat seeds")
wheatBundle = item(wheatBundleImage, "wheat bundle")

# create a grid of area obbjects:
for gy in range(GRID_HEIGHT):
    for gx in range(GRID_WIDTH):
        area(gx,gy)

# test fields
field1 = field(1,1)

farmer = entity(1200,360,image=farmerImage)

# sell panel things
sellPanelItem(100,100,"wheat bundle",wheatBundle, image=wheatBundleImage) # wheat
sellPanelItem(200,100,"wheat seeds",wheatSeeds, image=wheatSeedsImage) # seeds
lineSurf = pygame.Surface((10,720))
pygame.draw.line(lineSurf,"black",(5,0),(5,720),10)
sellPanelObject(640,0,image=lineSurf)
def sell1():
    global selectedSellableItem

    if selectedSellableItem == None:
        return
    
    if selectedSellableItem.item not in inventory.items:
        return
    
    inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]
    inventory.remove(selectedSellableItem.item)

def sellAll():
    global selectedSellableItem

    if selectedSellableItem is None:
        return

    if selectedSellableItem.item not in inventory.items:
        return

    inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]*(inventory.items[selectedSellableItem.item]-1)
    inventory.items[selectedSellableItem.item] = 1
    inventory.popFromItems(selectedSellableItem.item)

def sellCustom():
    global selectedSellableItem,actionOnInputEnd,inputValue

    if selectedSellableItem is None:
        return

    if selectedSellableItem.item not in inventory.items:
        return 

    def sellCutsomAmt(amt):
        global actionOnInputEnd,inputValue

        amt = int(amt)
        if inventory.items[selectedSellableItem.item] < amt:
            return

        inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]*amt
        inventory.items[selectedSellableItem.item] -= amt
        actionOnInputEnd = None

    actionOnInputEnd = sellCutsomAmt
    inputValue = "0"



sell1Button = sellPanelButton(60,400,image=sell1ButtonImage)
sellAllButton = sellPanelButton(224,400,image=sellAllButtonImage)
sellCustomButton = sellPanelButton(388,400,image=sellCustomButtonImage)
backButton = sellPanelButton(0,0,image=backButtonImage)
sell1Button.action = sell1
sellAllButton.action = sellAll
sellCustomButton.action = sellCustom
highlightFrame = sellPanelObject(-950,-950,layer=-1,image=highlightFrameImage)
SELL_PANEL_PRICE_LIST = {
    "wheat bundle": 15,
    "wheat seeds": 1
}

# create walls of the screen
rightWall = obstacle(-40,0,width=40,height=HEIGHT+40)
leftWall = obstacle(WIDTH,0,width=40,height=HEIGHT+40)
topWall = obstacle(-40,-40,width=WIDTH+40,height=40)
bottomWall = obstacle(-40,HEIGHT,width=WIDTH+40,height=40)

KEY_BINDS = {
    pygame.K_ESCAPE: lambda: globals().__setitem__("sellPanelOpened",False)
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

def flickUpdateFrame():
    """Flick 'updateFrame' back on."""
    global updateFrame
    updateFrame = True

def breakPlant(mousex,mousey):
    """Breaks the plant, mouse is hovering on."""
    hoverField = findFieldByCoords(mousex,mousey)
    if hoverField is None:
        return
    if hoverField.plant is None:
        return
    hoverField.plant.breakMyself()
    flickUpdateFrame()

def placePlant(mousex,mousey):
    """"Places the plant where the mouse is pointing."""
    hoverField = findFieldByCoords(mousex,mousey)
    if hoverField is None:
        return 

    if hoverField.plant is not None:
        return

    if inventory.remove(wheatSeeds):
        wheat(hoverField)
    flickUpdateFrame()

def mouseControl():
    """Covers everything that is activated with mouse."""
    global canPressAgain

    mouse = pygame.mouse.get_pressed()
    mousex,mousey = pygame.mouse.get_pos()

    if mouse[2] and 0 < mousex < WIDTH and 0 < mousey < HEIGHT:
        if not sellPanelOpened:
            placePlant(mousex,mousey)
    if mouse[0] and 0 < mousex < WIDTH and 0 < mousey < HEIGHT:
        if not sellPanelOpened:
            breakPlant(mousex,mousey)
        else:
            for i in sellPanelItems:
                i:sellPanelItem
                if i.getRect().collidepoint(mousex,mousey):
                    i.select()

            if canPressAgain:
                for b in sellPanelButtons:
                    b:sellPanelButton
                    if b.getRect().collidepoint(mousex,mousey):
                        b.action()
                        canPressAgain = False
                        break

            
        if farmer.getRect().collidepoint(mousex,mousey):
            showSellPanel()

    if not any(mouse):
        canPressAgain = True

def showSellPanel():
    """Shows the 'sell and buy' panel."""
    global sellPanelOpened

    sellPanelOpened = True

def hideSellPanel():
    """Hides the 'sell and buy' panel."""
    global sellPanelOpened

    sellPanelOpened = False

backButton.action = hideSellPanel

def control():
    """Covers the control of the game."""
    global inputValue,canTypeAgain

    keys = pygame.key.get_pressed()

    for k,action in KEY_BINDS.items():
        if keys[k]:
            action()

    if actionOnInputEnd is not None and canTypeAgain:
        for key,num in NUMBERS.items():
            if keys[key]:
                if inputValue == "0":
                    inputValue = str(num)
                    canTypeAgain = False
                    break

                inputValue = inputValue + str(num)
                canTypeAgain = False
                break

        if keys[pygame.K_RETURN]:
            actionOnInputEnd(inputValue)
            inputValue = ""
            canTypeAgain = False

        if keys[pygame.K_BACKSPACE]:
            inputValue = inputValue[:-1]
            canTypeAgain = False

    if not any(keys):
        canTypeAgain = True



    mouseControl()

def render():
    """Covers the rendering of the game."""
    global updateFrame

    # if not updateFrame:
    #     return

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

        if not inputValue == "":
            sellPanel.blit(renderBigText(inputValue, "white"),typingPosition)
        screen.blit(sellPanel,(0,0))



def update():
    for pl in plants:
        pl:wheat
        pl.increaseTimePlanted()

inventory.add(wheatSeeds,1000)
inventory.add(wheatBundle,1000)
screen.fill("white")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    start = time()

    control()
    update()
    render()

    pygame.display.flip()

    clock.tick(MAX_FPS)
    dt = time() - start

pygame.quit()