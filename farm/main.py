import pygame
from  time import time

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
pygame.display.set_caption("farm")
MAX_FPS = 120
running = True
updateFrame = True

mountain = pygame.image.load("mountain.jpg").convert_alpha()
playerImage = pygame.image.load("player.png").convert_alpha()

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

entities = []

class entity:
    """Every object on a screen."""
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
            self.image = createDefaultImage(self.width,self.height,"gray","black")
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

class player(entity):
    """Main player object."""
    def __init__(self, x, y, speed,
                 width=0, height=0, image=None):
        super().__init__(x, y, width=width, height=height, image=image)
        self.speed = speed
    def move(self,axis,amt):
        if axis == "x":
            self.x += amt * self.speed
        if axis == "y":
            self.y += amt * self.speed
        flickUpdateFrame()
        

character = player(200,300,10,image=playerImage)

KEY_BINDS = {
    pygame.K_w: lambda: character.move("y",-1),
    pygame.K_a: lambda: character.move("x",-1),
    pygame.K_s: lambda: character.move("y",1),
    pygame.K_d: lambda: character.move("x",1),
}

def flickUpdateFrame():
    global updateFrame
    updateFrame = True

def control():
    keys = pygame.key.get_pressed()

    for k,action in KEY_BINDS.items():
        if keys[k]:
            action()

def render():
    global updateFrame

    if not updateFrame:
        return

    screen.fill("white")
    for ent in entities:
        ent.draw()
    updateFrame = False

screen.fill("white")
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    

    control()
    render()

    pygame.display.flip()

    clock.tick(MAX_FPS)

pygame.quit()