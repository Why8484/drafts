import pygame
from  time import time
import random
import os
import math

pygame.init()
HEIGHT = 720
WIDTH = 1280
screen = pygame.display.set_mode((WIDTH,HEIGHT))
invPanel = pygame.Surface((WIDTH, 160)) # 1280 X 160
sellPanel = pygame.Surface((WIDTH,560)) # 1280 X 560
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
font = pygame.font.Font(r"assets\font.ttf",FONT_HEIGHT)
bigFont = pygame.font.Font(r"assets\font.ttf",BIG_FONT_HEIGHT)
mediumFont = pygame.font.Font(r"assets\font.ttf", 44)
running = True
updateFrame = True
selectedSellableItem = None
newFarmlandCreated = False
canPressAgain = True
inputValue = ""
typingPosition = 780,100
actionOnInputEnd = None
canTypeAgain = True
selectedInvSlot = None
justExited = False

def renderText(text:str,color):
    """Returns a surface of rendered text."""

    surf = font.render(text,False,color)
    return surf


def renderBigText(text:str,color,size=BIG_FONT_HEIGHT):
    """Returns a surface of rendered text in big font."""

    if size == BIG_FONT_HEIGHT:
        surf = bigFont.render(text,False,color)
    elif size == 44:
        surf = mediumFont.render(text,False,color)
    return surf

def displayLetterAmount(amt):
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
    """Loads all images from folder skipping the fikles that are not images. And sor6ts them by name if name is 0.png, 9.png etc.
    Params:
        folderPath: path of the folder.
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
    for surf,fn in imageSequence:
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
fertilizedSoilImage = loadImage("fertilizedSoil.png")
millstoneImage = loadImage("millstoneFull.png")
progressBarSequence = loadFromFolder("progressBar")
flourImage = loadImage("flour.png")
waterBucketImage = loadImage("waterBucket.png")
bowlImage = loadImage("bowl.png")
doughImage = loadImage("dough.png")
brickOvenImage = loadImage("brickOven.png")
breadImage = loadImage("bread.png")
charcoalImage = loadImage("charcoal.png")
woodImage = loadImage("wood.png")
wetSoilImage = loadImage("wetSoil.png")
fertilizedWetSoilImage = loadImage("fertilizedWetSoil.png")
rightButton = loadImage("rightButton.png")
leftButton = loadImage("leftButton.png")

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
        gx and gy: coords.
    Returns:
        area object that overlaps given coords."""

    return areas[gy*GRID_WIDTH+gx]

def findAreaByCoords(x,y):
    """Finds an area object that overlaps coords given.
    Params:
        x and y: coords.
    Returns:
        area object that overlaps given coords."""

    gx = x//BLOCK_SIZE
    gy = y//BLOCK_SIZE

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
        self.multiplier = 1
        self.fertilized = False
        self.wet = False
        findAreaByGridCoords(gridx,gridy).object = self

        super().__init__(x, y, 0, image=soilImage)
        fields.append(self)

    def fertilize(self):
        """Increase multiplier to 3."""
        self.multiplier = 3 if not self.wet else 3.5
        self.image = fertilizedSoilImage if not self.wet else fertilizedWetSoilImage
        self.fertilized = True

    def makeWet(self):
        """Increase multiplier to 1.8."""
        self.multiplier = 1.8 if not self.fertilized else 3.5
        self.image = wetSoilImage if not self.fertilized else fertilizedWetSoilImage
        self.wet = True

class wheat(entity):
    """Wheat object that grows on certain field. List: plants."""
    def __init__(self, field:field):
        self.field = field
        field.plant = self
        self.growthSequence = wheatGrowth
        self.timePlanted = 0
        x,y = field.x,field.y-40
        self.phase = 0
        self.growthTime = [random.randint(8,12),random.randint(11,19),random.randint(7,19),random.randint(19,25)]
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
                inventory.add(wheatSeeds,rollFromChance({0: 60, 1: 40}))
            case 1:
                inventory.add(wheatSeeds,rollFromChance({0: 10, 1: 65, 2: 25}))
            case 2:
                inventory.add(wheatSeeds, rollFromChance({1: 50, 2: 35, 3: 15}))
            case 3:
                inventory.add(wheatSeeds, rollFromChance({2: 100}))
            case 4:
                inventory.add(wheatSeeds, rollFromChance({2: 60, 3: 35, 4:5}))
                inventory.add(wheatBundle, 1)

class inventory:
    items = {}
    coins = 9000000
    page = 1
    previousPage = 1
    LAST_PAGE = 6

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
        invPanel.blit(highlightFrameImage,(selectedInvSlot.x-5,selectedInvSlot.y-5))
        for i,count in cls.items.items():
            i.draw(i.slot.x,i.slot.y)
            countText = renderText("x"+str(count),"black")
            invPanel.blit(countText,(i.slot.x+BLOCK_SIZE/2-countText.get_width()//2,i.slot.y+BLOCK_SIZE+i.title.get_height()+10))

        invPanel.blit(coinImage,(1080,invPanel.get_height()-90))
        leftButtonEnt.draw(invPanel)
        rightButtonEnt.draw(invPanel)
        invPanel.blit(renderBigText(str(displayCoinsAmount()),"black",44),(1165,invPanel.get_height()-60))


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

    @classmethod
    def changePage(cls, pageNum="right"):
        """Changes the page of the inventory to param pageNum.
        PageNum could also be equal to 'right'(changes the page to one directly to the right of the current one)
        or 'left'(changes the page to one directly to the left of the current one)."""

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

    @classmethod
    def applyPage(cls):
        index = cls.previousPage - cls.page

        for s in slots:
            s.x += index*1280






class item:
    """Class for items that show up in the inventory space. List: none."""
    def __init__(self, image, name,layer=0,description="",machineClass=None):
        self.image = image
        self.machineClass = machineClass
        self.layer = layer
        self.name = name
        self.slot = None
        self.description = description
    def draw(self,x,y):
        invPanel.blit(self.image,(x,y))
        self.title = renderText(self.name,"black")
        invPanel.blit(self.title,(x+BLOCK_SIZE//2-self.title.get_width()//2,y+BLOCK_SIZE+10))

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
    def __init__(self, x, y, name, normalItem, sellable=True, buyable=False, layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        self.selected = False
        self.name = name
        self.item = normalItem
        self.sellable = sellable
        self.buyable = buyable
        sellPanelItems.append(self)
    def select(self):
        """select this item as the selectedSellable."""
        global selectedSellableItem,highlightFrame,descriptionLines,descriptionPrice,descriptionTitle,descriptionPanel

        self.selected = True
        selectedSellableItem = self
        highlightFrame.x,highlightFrame.y = self.x-5,self.y-5

        for descLine in descriptionLines:
            descLine.image = renderText("","black")
        for i,line in enumerate(self.item.description.splitlines()):
            descriptionLines[i].image = renderText(line, "black")
        descriptionTitle.image = renderBigText(self.name, "black")
        descriptionTitle.x = 317 + descriptionPanel[0] - descriptionTitle.image.get_width()//2
        buyPrice = "Buy for: " + str(BUY_PANEL_PRICE_LIST[self.name]) + "." if self.name in BUY_PANEL_PRICE_LIST else "Buy for: non-buyable."
        sellPrice = "Sell for: " + str(SELL_PANEL_PRICE_LIST[self.name]) + "." if self.name in SELL_PANEL_PRICE_LIST else "Sell for: non-sellable."
        sellableStr = "sellable: yes." if self.sellable else "sellable: no."
        buyableStr = "buyable: yes." if self.buyable else "buyable: no."

        descriptionPriceLines[0].image = renderText(sellableStr, "black")
        descriptionPriceLines[1].image = renderText(buyableStr, "black")
        descriptionPriceLines[2].image = renderText(buyPrice, "black")    
        descriptionPriceLines[3].image = renderText(sellPrice, "black")

        if self.buyable:
            buyMaxText = "buy a maximum of " + str(displayLetterAmount(inventory.coins//int(BUY_PANEL_PRICE_LIST[self.name]))) + " " + self.name + " for " + str(displayLetterAmount(inventory.coins//int(BUY_PANEL_PRICE_LIST[self.name])*int(BUY_PANEL_PRICE_LIST[self.name]))) + " coins."
        else:
            buyMaxText = "This is non-buyable."
        if self.sellable:
            count = inventory.items[self.item] if self.item in inventory.items else 0
            sellAllText = "sell all " + str(displayLetterAmount(count)) + " of your " + self.name + " for " + str(displayLetterAmount(int(SELL_PANEL_PRICE_LIST[self.name])*count)) + " coins."
        else:
            sellAllText = "This is non-sellable."
        buyMaxLine.image = renderText(buyMaxText, "black")
        sellAllLine.image = renderText(sellAllText, "black")

    def draw(self):
        super().draw()
        if self.sellable:
            sellPanel.blit(sellableIndicatorImage, (self.x + self.width - 10,self.y))
        elif self.buyable:
            sellPanel.blit(buyableIndicatorImage, (self.x + self.width - 10,self.y))
            return
        if self.buyable:
            sellPanel.blit(buyableIndicatorImage, (self.x + self.width - 20,self.y))
            

class sellPanelButton(sellPanelObject):
    """Class for buttons like sellAll,sell1 etc. List: sellPanelButtons."""
    def __init__(self, x, y, layer=0, width=0, height=0, image=None):
        super().__init__(x, y, layer, width, height, image)
        sellPanelButtons.append(self)
    def action(self):
        pass

class machine(entity):
    """Class for machines like millstone. List: machines"""
    def __init__(self, x, y, image):
        super().__init__(x, y, 0,BLOCK_SIZE,BLOCK_SIZE,image)
        machines.append(self)

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
        self.timeToComplete = 0.1
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


    def onTick(self):
        mouse = pygame.mouse.get_pressed()
        mousex,mousey = pygame.mouse.get_pos()
        if mouse[2] and self.getRect().collidepoint((mousex,mousey)):
            self.onRightClick()
        if not self.empty and self.prBar.hidden:
            self.prBar.show()
        if ((not mouse[0] and self.getRect().collidepoint((mousex,mousey))) or self.empty) and not self.completed:
            self.holdStart = None
            if not self.prBar.hidden:
                self.prBar.hide()
            return

        if self.holdStart is not None:
            self.holdTime += dt
            if self.holdTime >= self.timeToComplete:
                self.prBar.hide()
                inventory.add(self.inputOutput[self.itemIn], 1)
                self.empty = True
                self.holdStart = None
                self.holdTime = 0

        self.prBar.setAnimationFrame(int(self.holdTime/self.timeToComplete*len(progressBarSequence)))

class bowlMachine(machine):
    """Class for bowl."""
    def __init__(self, x, y):
        super().__init__(x, y, bowlImage)
        self.holdStart = None
        self.holdTime = 0
        self.timeToComplete = 0.1
        barX,barY = self.x-5,self.y-15
        if self.x == 0:
            barX = 0
        if self.y == 0:
            barY = 0
        self.prBar = progressBar(barX,barY)
        self.empty = True
        self.itemsIn = []
        self.inputOutput = {
            (flour,waterBucket): dough,
            (waterBucket, flour): dough
        }
        self.increaseHoldTime = True

    def onLeftClick(self):
        global canPressAgain

        if self.holdStart is None:
            self.holdTime = 0
            self.holdStart = time()
        if self.holdTime >= self.timeToComplete:
            self.holdTime = 0

    def onRightClick(self):
        global canPressAgain

        if not selectedInvSlot.item is None and canPressAgain:
            self.empty = False
            self.itemsIn.append(selectedInvSlot.item)
            inventory.remove(selectedInvSlot.item)
            canPressAgain = False


    def onTick(self):
        mouse = pygame.mouse.get_pressed()
        mousex,mousey = pygame.mouse.get_pos()
        if mouse[2] and self.getRect().collidepoint((mousex,mousey)):
            self.onRightClick()
        if not self.empty and self.prBar.hidden:
            self.prBar.show()
        if ((not mouse[0] and self.getRect().collidepoint((mousex,mousey))) or self.empty):
            # hide bar and stop the charging of it if not mouse pressed or it's not on the object or it's empty
            self.holdStart = None
            if not self.prBar.hidden:
                self.prBar.hide()
            return

        if self.holdStart is not None and self.increaseHoldTime:
            self.holdTime += dt
            if self.holdTime >= self.timeToComplete:
                self.prBar.hide()
                if tuple(self.itemsIn) in self.inputOutput:
                    inventory.add(self.inputOutput[tuple(self.itemsIn)], 1)
                    self.itemsIn.clear()
                else:
                    for i in self.itemsIn:
                        inventory.add(i,1)
                    self.itemsIn.clear()
                self.empty = True
                self.holdStart = None
                self.holdTime = 0

        if not self.increaseHoldTime:
            self.increaseHoldTime = True

        self.prBar.setAnimationFrame(int(self.holdTime/self.timeToComplete*len(progressBarSequence)))

class brickOvenMachine(machine):
    def __init__(self, x, y):
        super().__init__(x, y, brickOvenImage)
        self.puttableItems = { 
            # all items that you're able to put in an oven. the negatice value represents the item smelting and the positive the fuel.
            # It also represents how much fuel does a smeltable use or how much power the fuel can give.
            dough: -5,
            wood: (-3,5),
            charcoal: 10,
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


        barX,barY = self.x-5,self.y-15
        if self.x == 0:
            barX = 0
        if self.y == 0:
            barY = 0
        self.prBar = progressBar(barX,barY)
        self.fuelBar = progressBar(barX, self.y+72)
        self.prBar.hide()
        self.fuelBar.hide()
        self.MaxFuel = 0
        self.MaxItemPower = 0
        self.justPutTheFuel = False
    def onRightClick(self):
        if self.producedItem is not None:
            return
        if selectedInvSlot.item in self.puttableItems:
            powerValue = self.puttableItems[selectedInvSlot.item]
            if type(powerValue) == tuple:
                if self.itemIn is None:
                    self.itemIn = selectedInvSlot.item
                    inventory.remove(selectedInvSlot.item)
                    self.holdTime = 0
                    self.justPutTheFuel = True
                    self.MaxItemPower = powerValue[0]
                elif self.itemIn is not None and (self.fuelIn is None or self.fuelIn == selectedInvSlot.item) and not self.justPutTheFuel:
                    self.MaxFuel = powerValue[1]
                    self.fuelIn = selectedInvSlot.item
                    self.justPutTheFuel = True
                    inventory.remove(selectedInvSlot.item)
                    self.fuelLeft = powerValue[1]
                return
            if powerValue < 0 and self.itemIn is None:
                self.itemIn = selectedInvSlot.item
                inventory.remove(selectedInvSlot.item)
                self.holdTime = 0
                self.MaxItemPower = powerValue
            elif powerValue > 0 and self.fuelIn is None:
                self.MaxFuel = powerValue
                self.fuelIn = selectedInvSlot.item
                inventory.remove(selectedInvSlot.item)
                self.fuelLeft = powerValue


    def onLeftClick(self):
        if self.producedItem is not None:
            inventory.add(self.producedItem,1)
            self.producedItem = None
            self.prBar.hide()
            return

    def onTick(self):
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
            if self.holdTime > abs(self.MaxItemPower):
                if self.itemIn in self.produce:
                    self.producedItem = self.produce[self.itemIn]
                    self.itemIn = None  
                else:
                    self.producedItem = self.itemIn
                    self.itemIn = None  


        if self.holdTime > 0 and self.itemIn is not None:
            self.prBar.setAnimationFrame(int(self.holdTime/abs(self.MaxItemPower)*len(progressBarSequence)))
        if self.fuelIn is not None:
            self.fuelBar.setAnimationFrame(int(self.fuelLeft/self.MaxFuel*len(progressBarSequence)))

class progressBar(entity):
    """Class for progress bars."""
    def __init__(self, x, y):
        super().__init__(x, y, 5, 90,10,progressBarSequence[0])
        self.trackedValue = 0
        self.index = 0
        self.drawCopy = None
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
        self.drawCopy = self.draw
        self.draw = self.emptyFunc
        self.hidden = True

    def show(self):
        if self.drawCopy is None:
            return

        self.draw = self.drawCopy
        self.hidden = False

    def emptyFunc(self):
        return

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

# create slots
for page in range(6):
    for x in range(80,1080, 200):
        slot(page*1280+x,10,page+1)

wheatSeeds = item(
    wheatSeedsImage,
    "wheat seeds",
    description="""Small, golden grains ready to be sown into soil
to grow wheat.""",
)

wheatBundle = item(
    wheatBundleImage,
    "wheat bundle",
    description="""Treat every seed with care and it will reward you with this.
A bundle of harvested wheat stalks, ready to be processed.""",
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
fertilizer.""",
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
After you know the work put into it, it looks even better
than... Let's say... another white dust.
A fundamental ingredient used to make dough and bread.""",
)

waterBucket = item(
    waterBucketImage,
    "bucket of water",
    description="""A bucket filled with clean water, straight from a nearby
river, essential for life.
You can see your reflection in it more clearer than in a
mirror!""",
)

bowl = item(
    bowlImage,
    "bowl",
    description="""A simple tool, but how useful is it! Used for combining
ingridients.""",
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
    description="""An oven assembled using bricks. Built to retain high heat
for baking bread.""",
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

# test fields
field1 = field(1,1)

farmer = entity(1200,360,image=farmerImage)
rightButtonEnt = entity(990,50,image=rightButton)
leftButtonEnt = entity(30,50,image=leftButton)


rightButtonEnt.getRect = rightButtonEnt.getInvRect
leftButtonEnt.getRect = leftButtonEnt.getInvRect
entities.remove(rightButtonEnt)
entities.remove(leftButtonEnt)

# sell panel things
sellPanelItem(60,80,"wheat bundle",wheatBundle, image=wheatBundleImage) # wheat
sellPanelItem(160,80,"wheat seeds",wheatSeeds, image=wheatSeedsImage, buyable=True) # seeds
sellPanelItem(260,80,"farmland", farmland, image=soilImage, buyable=True, sellable=False) # farmland
sellPanelItem(360, 80, "wood ash", woodAsh, image=woodAshImage, buyable=True, sellable=False) # wood ash
sellPanelItem(460,80,"millstone", millstone, image=millstoneImage, buyable=True, sellable=True) # millstone
sellPanelItem(60, 180, "flour", flour, image=flourImage, buyable=False, sellable=True) #flour
sellPanelItem(160, 180, "bucket of water", waterBucket, image=waterBucketImage, buyable=True, sellable=False) # bucket of water
sellPanelItem(260,180, "bowl", bowl, sellable=True,buyable=True, image=bowlImage) # bowl
sellPanelItem(360,180, "dough", dough, image=doughImage) # dough
sellPanelItem(460,180, "brick oven", brickOven, image=brickOvenImage, buyable=True, sellable=True) # brick oven
sellPanelItem(60, 280, "bread", bread, sellable=True, buyable=False, image=breadImage) # bread
sellPanelItem(160, 280, "wood", wood, buyable=True, sellable=False, image=woodImage) # wood
lineSurf = pygame.Surface((10,720))
pygame.draw.line(lineSurf,"black",(5,0),(5,720),10)
sellPanelObject(640,0,image=lineSurf)

def sellCheck():
    global selectedSellableItem

    if selectedSellableItem is None:
        return False
    
    if selectedSellableItem.item not in inventory.items:
        return False

    if not selectedSellableItem.sellable:
        return False

    return True

def buyCheck(amt=1):
    global selectedSellableItem

    amt = int(amt)

    if selectedSellableItem is None:
        return False
    if not selectedSellableItem.buyable:
        return False
    if inventory.coins < BUY_PANEL_PRICE_LIST[selectedSellableItem.name]*amt:
        return False


    return True

def sell1():
    global selectedSellableItem

    if not sellCheck():
        return
    
    inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]
    inventory.remove(selectedSellableItem.item)
    selectedSellableItem.select()

def buy1():
    global selectedSellableItem

    if not buyCheck():
        return

    inventory.coins -= BUY_PANEL_PRICE_LIST[selectedSellableItem.name]
    inventory.add(selectedSellableItem.item,1)
    selectedSellableItem.select()



def sellAll():
    global selectedSellableItem

    if not sellCheck():
        return

    inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]*(inventory.items[selectedSellableItem.item])
    inventory.items[selectedSellableItem.item] = 0
    inventory.popFromItems(selectedSellableItem.item)
    selectedSellableItem.select()


def buyMax():
    global selectedSellableItem

    if selectedSellableItem.name not in BUY_PANEL_PRICE_LIST.keys():
        return False

    maxAmount = inventory.coins//BUY_PANEL_PRICE_LIST[selectedSellableItem.name]
    
    if not buyCheck(maxAmount):
        return

    inventory.coins -= BUY_PANEL_PRICE_LIST[selectedSellableItem.name]*maxAmount
    inventory.add(selectedSellableItem.item,maxAmount)
    selectedSellableItem.select()


def sellCustom():
    global selectedSellableItem,actionOnInputEnd,inputValue

    def sellCutsomAmt(amt):
        global actionOnInputEnd,inputValue

        if not sellCheck():
            return
        
        amt = int(amt)
        if inventory.items[selectedSellableItem.item] < amt:
            return

        inventory.coins += SELL_PANEL_PRICE_LIST[selectedSellableItem.name]*amt
        inventory.items[selectedSellableItem.item] -= amt
        actionOnInputEnd = None

    actionOnInputEnd = sellCutsomAmt
    inputValue = "-"
    selectedSellableItem.select()


def buyCustom():
    global actionOnInputEnd,inputValue

    def buyCustomAmt(amt):
        global actionOnInputEnd

        if not buyCheck(amt):
            return

        amt = int(amt)
        inventory.coins -= BUY_PANEL_PRICE_LIST[selectedSellableItem.name]*amt
        inventory.add(selectedSellableItem.item, amt)
        actionOnInputEnd = None

    actionOnInputEnd = buyCustomAmt
    inputValue = "-"
    selectedSellableItem.select()



# buttons
sell1Button = sellPanelButton(60,560-192,image=sell1ButtonImage)
sellCustomButton = sellPanelButton(224,560-192,image=sellCustomButtonImage)
sellAllButton = sellPanelButton(388,560-192,image=sellAllButtonImage)
buy1Button = sellPanelButton(60,560-96, image=buy1Image)
buyCustomButton = sellPanelButton(224,560-96, image=buyCustomImage)
buyMaxButton = sellPanelButton(388, 560-96, image=buyMaxImage)
backButton = sellPanelButton(0,0,image=backButtonImage)
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

highlightFrame = sellPanelObject(-950,-950,layer=-1,image=highlightFrameImage)
SELL_PANEL_PRICE_LIST = {
    "millstone": 75,
    "flour": 20,
    "wheat seeds": 1,
    "bowl": 50,
    "wheat bundle": 5,
    "dough": 30,
    "brick oven": 450,
    "bread": 45,
}
BUY_PANEL_PRICE_LIST = {
    "wheat seeds": 1,
    "farmland": 30,
    "wood ash": 20,
    "bucket of water": 10,
    "millstone": 100,
    "bowl": 75,
    "brick oven": 500,
    "wood": 5
}

entity(0,0,image=renderText("бурундук", "black"))

KEY_BINDS = {
    pygame.K_ESCAPE: lambda: globals().__setitem__("sellPanelOpened",False),
    pygame.K_RIGHT: lambda: inventory.changePage("right"),
    pygame.K_LEFT: lambda: inventory.changePage("left")
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

def breakPlant(field):
    """Breaks the plant, mouse is hovering on."""
    if field is None:
        return
    if field.plant is None:
        return
    field.plant.breakMyself()
    flickUpdateFrame()

def placePlant(field):
    """"Places the plant where the mouse is pointing."""

    if field is None:
        return 

    if field.plant is not None:
        return

    if inventory.remove(wheatSeeds):
        wheat(field)
    flickUpdateFrame()

def mouseControl():
    """Covers everything that is activated with mouse."""
    global canPressAgain,newFarmlandCreated,selectedInvSlot,justExited

    mouse = pygame.mouse.get_pressed()
    mousex,mousey = pygame.mouse.get_pos()

    if mouse[2] and 0 < mousex < WIDTH and 0 < mousey < HEIGHT:
        if not sellPanelOpened:
            hoverField:field = findFieldByCoords(mousex,mousey)
            if hoverField is None and farmland in inventory.items and selectedInvSlot == farmland.slot:
                fieldx,fieldy = mousex//BLOCK_SIZE,mousey//BLOCK_SIZE
                if 0 <= fieldx <= 12 and 0 <= fieldy <= 6:
                    for m in machines:
                        if m.x//BLOCK_SIZE == fieldx and m.y//BLOCK_SIZE == fieldy:
                            return
                    field(fieldx,fieldy)
                    inventory.remove(farmland)
                    newFarmlandCreated = True
            elif not newFarmlandCreated :
                if selectedInvSlot == wheatSeeds.slot and not mouse[0]:
                    placePlant(hoverField)
                elif selectedInvSlot == woodAsh.slot and hasattr(hoverField, "fertilized") and not hoverField.fertilized:
                    hoverField.fertilize()
                    inventory.remove(woodAsh)
                elif selectedInvSlot == waterBucket.slot and hasattr(hoverField, "wet") and not hoverField.wet:
                    hoverField.makeWet()
                    inventory.remove(waterBucket)
                elif selectedInvSlot.item is not None and selectedInvSlot.item.machineClass is not None and hoverField is None and 0 <= mousey//BLOCK_SIZE < 7 and 0 <= mousex//BLOCK_SIZE <= 12 and canPressAgain:
                    selectedInvSlot.item.machineClass(mousex//BLOCK_SIZE*BLOCK_SIZE,mousey//BLOCK_SIZE*BLOCK_SIZE)
                    inventory.remove(selectedInvSlot.item)
                    canPressAgain = False
            else:
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
            hoverField = findFieldByCoords(mousex,mousey)
            if hoverField is None:
                for m in machines:
                    if m.getRect().collidepoint((mousex,mousey)):
                        m.onLeftClick()
                        break
            if not justExited:
                breakPlant(hoverField)            
            if farmer.getRect().collidepoint(mousex,mousey):
                showSellPanel()
        else:
            # in sell panel
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



    elif not any(mouse):
        canPressAgain = True
        newFarmlandCreated = False
        justExited = False

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
    global inputValue,canTypeAgain

    keys = pygame.key.get_pressed()

    for k,action in KEY_BINDS.items():
        if keys[k] and canTypeAgain:
            action()
            canTypeAgain = False

    if not sellPanelOpened:
        for key,num in NUMBERS.items():
            if keys[key]:
                inventory.changePage(num)

    # input
    if actionOnInputEnd is not None and canTypeAgain:
        for key,num in NUMBERS.items():
            if keys[key]:
                if inputValue == "-":
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

    # reset can type again
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
        pl.increaseTimePlanted()

    for m in machines:
        m.onTick()

inventory.add(woodAsh,100)
inventory.add(brickOven,1 )
inventory.add(dough,10)
inventory.add(wood,100)
selectedInvSlot = list(inventory.items.keys())[0].slot
screen.fill("white")
while running:
    print(inventory.page)
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