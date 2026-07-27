import pygame
from  time import time
import random
import os

pygame.init()
HEIGHT = 720
WIDTH = 1280
screen = pygame.display.set_mode((WIDTH,HEIGHT))
invPanel = pygame.Surface((WIDTH, HEIGHT//5))
clock = pygame.time.Clock()
pygame.display.set_caption("farm")
INVENTORY_BG = (245,241,127)
MAX_FPS = 120
BLOCK_SIZE = 80
GRID_WIDTH = int(WIDTH/BLOCK_SIZE) #16
GRID_HEIGHT = int(HEIGHT/BLOCK_SIZE)  #9
font = pygame.font.SysFont("comicsansms",22)
running = True
updateFrame = True

def renderText(text:str,color):
    surf = font.render(text,False,color)
    return surf

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
wheatItemImage = loadImage("wheat bundle.png")
wheatSeedsImage = loadImage("wheat seeds.png")

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
        self.growthTime = [2,2,4]
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
        for i,count in cls.items.items():
            i.draw(i.slot.x,i.slot.y)
            invPanel.blit(renderText("x"+str(count),"black"),(i.slot.x+BLOCK_SIZE/2,BLOCK_SIZE+i.title.get_height()))

    @classmethod
    def remove(cls,item):
        """Removes the one piece given iem from inventory.
        Returns true if there was that item in inventory and false if there wasn't."""
        if item not in cls.items.keys():
            return False

        cls.items[item] -= 1
        if cls.items[item] == 0:
            item.slot.item = None
            item.slot = None
            cls.items.pop(item)
        return True

class item:
    """Class for items that show up in the inventory space. List: none."""
    def __init__(self, image, name):
        self.image = image
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
        
# create slots
for x in range(40,1280,200):
    slot(x,0)

wheatSeeds = item(wheatSeedsImage,"wheat seeds")
wheatBundle = item(wheatItemImage, "wheat bundle")

# create a grid of area obbjects:
for gy in range(GRID_HEIGHT):
    for gx in range(GRID_WIDTH):
        area(gx,gy)

# test fields
field1 = field(1,1)

# create walls of the screen
rightWall = obstacle(-40,0,width=40,height=HEIGHT+40)
leftWall = obstacle(WIDTH,0,width=40,height=HEIGHT+40)
topWall = obstacle(-40,-40,width=WIDTH+40,height=40)
bottomWall = obstacle(-40,HEIGHT,width=WIDTH+40,height=40)

KEY_BINDS = {
}

def flickUpdateFrame():
    """Flick 'updateFrame' back on."""
    global updateFrame
    updateFrame = True

def mouseControl():
    """Covers everything that is activated with mouse."""

    mouse = pygame.mouse.get_pressed()
    mousex,mousey = pygame.mouse.get_pos()

    if mouse[2] and 0 < mousex < WIDTH and 0 < mousey < HEIGHT:
        hoverField = findFieldByCoords(mousex,mousey)
        if hoverField is None:
            return 

        if hoverField.plant is not None:
            return

        if inventory.remove(wheatSeeds):
            wheat(hoverField)
        flickUpdateFrame()
    if mouse[0] and 0 < mousex < WIDTH and 0 < mousey < HEIGHT:
        hoverField = findFieldByCoords(mousex,mousey)
        if hoverField is None:
            return
        if hoverField.plant is None:
            return
        hoverField.plant.breakMyself()
        flickUpdateFrame()
        
        

def control():
    """Covers the control of the game."""

    keys = pygame.key.get_pressed()

    for k,action in KEY_BINDS.items():
        if keys[k]:
            action()

    mouseControl()

def render():
    """Covers the rendering of the game."""
    global updateFrame

    # if not updateFrame:
    #     return

    screen.fill("white")
    for ent in entities:
        if isinstance(ent,wheat):
            pass
        ent.draw()
    updateFrame = False

    invPanel.fill((245,241,127))
    inventory.draw()
    screen.blit(invPanel,(0,HEIGHT-invPanel.get_height()))


def update():
    for pl in plants:
        pl:wheat
        pl.increaseTimePlanted()

inventory.add(wheatSeeds,1)
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
    print(inventory.items)

pygame.quit()