# Example file showing a basic pygame "game loop"
import pygame
import math
import numpy as np

# pygame setup
pygame.init()
WIDTH = 900
HEIGHT = 900
display = pygame.display.set_mode((WIDTH,HEIGHT))
screen = pygame.Surface((WIDTH,HEIGHT-350))
pygame.display.set_caption("3D space")
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("comicsansms",44)

# EVERYTHING HERE WORKS IN -1..1 COORDINATE SYSTEM

def renderText(x,y, text,color):
    """Inputs the text, it's color and x,y(IN 0..w/h COORDINATE SYSTEM!!!!). 
    Renders that text as image object"""

    textSurf = font.render(text, True, color)
    return image(x,y,textSurf.get_width(),textSurf.get_height(), textSurf)


objects = []
points = []
meshes = []
images = []
marks = []
walls = []
edges = []

def floatCtoIntC(fx,fy):
    return ((fx+1)/2*WIDTH), ((fy+1)/2*HEIGHT),

def intCtoFloatC(ix,iy):
    return 2*(ix/WIDTH)+1, 2*(iy/HEIGHT)+1

def degreesToRadians(degrees):
    return degrees * math.pi/180

class image:
    def __init__(self,x,y,width,height,surf):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.surf = surf
        objects.append(self)
        images.append(self)
    def draw(self):
        display.blit(self.surf, (self.x,self.y))

class mark:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.POINT_COLOR = (50,0,255)
        self.POINT_SIZE = 10
        sx,sy = intCtoFloatC(self.x,self.y)
        self.rect = pygame.draw.rect(screen, self.POINT_COLOR, (sx-self.POINT_SIZE/2, sy-self.POINT_SIZE/2, self.POINT_SIZE,self.POINT_SIZE))
        objects.append(self)
        marks.append(self)
    def draw(self):
        sx,sy = floatCtoIntC(self.x,self.y)
        self.rect = pygame.draw.rect(screen, self.POINT_COLOR, (sx-self.POINT_SIZE/2, sy-self.POINT_SIZE/2, self.POINT_SIZE,self.POINT_SIZE))
        # self.rect = pygame.draw.circle(screen, self.POINT_COLOR, (sx,sy), self.POINT_SIZE//2)

    def destroy(self):
        objects.remove(self)
        marks.remove(self)
        del self

class point:
    def __init__(self,x,y,z,color=(50,0,255)):
        self.x = x
        self.y = y
        self.z = z
        self.color = color

        points.append(self)
        self.project()
    def project(self):
        if self.z == 0:
            return
        self.mark = mark(self.x/self.z,self.y/self.z)
        self.mark.POINT_COLOR = self.color
        if hasattr(self, "isMainCharacter"):
            self.mark.POINT_COLOR = (50,50,50)
        return self.mark

    def refresh(self):
        self.mark.destroy()
        self.project()

    # MOVING(TRANSLATION)
    def moveX(self, amt):
        """Moves the vertex in axis x by some amount."""

        self.x += amt
        self.refresh()

    def moveY(self, amt):
        """Moves the vertex in axis y by some amount."""
        
        self.y += amt
        self.refresh()

    def moveZ(self, amt):
        """Moves the vertex in axis z by some amount."""
        
        self.z += amt
        self.refresh()  


    # ROTATION
    # x' = xcos(a) - ysin(a)
    # y' = xsin(a) + ycos(a)
    def rotateX(self, angle, pivot):
        """Rotates the vertex by x axis(in zy plane) by angle(in degrees) 
        around the provided pivot point. Returns the new coordinates of a vertex."""

        cx,cy,cz = pivot
        x,y,z = self.x,self.y,self.z
        tempY = y - cy
        tempZ = z - cz
        a = degreesToRadians(angle)

        x = x
        rotatedY = tempY*math.cos(a) - tempZ*math.sin(a)
        rotatedZ = tempY*math.sin(a) + tempZ*math.cos(a)

        newX = x
        newY = rotatedY + cy
        newZ = rotatedZ + cz

        self.x,self.y,self.z = newX,newY,newZ

        self.refresh()
        return newX,newY,newZ

    def rotateY(self, angle, pivot):
        """Rotates the vertex by y axis(in zx plane) by angle(in degrees) 
        around the provided pivot point. Returns the new coordinates of a vertex."""

        cx,cy,cz = pivot
        x,y,z = self.x,self.y,self.z
        tempX = x - cx
        tempZ = z - cz
        a = degreesToRadians(angle)

        rotatedX = tempX*math.cos(a) + tempZ*math.sin(a)
        y = y
        rotatedZ = tempZ*math.cos(a) - tempX*math.sin(a)

        newX = rotatedX + cx
        newY = y
        newZ = rotatedZ + cz

        self.x,self.y,self.z = newX,newY,newZ

        self.refresh()
        return newX,newY,newZ
    
    def rotateZ(self, angle, pivot):
        """Rotates the vertex by z axis(in xy plane) by angle(in degrees) 
        around the provided pivot point. Returns the new coordinates of a vertex."""

        cx,cy,cz = pivot
        x,y,z = self.x,self.y,self.z
        tempY = y - cy
        tempX = x - cx
        a = degreesToRadians(angle)

        x = x
        rotatedX = tempX*math.cos(a) - tempY*math.sin(a)
        rotatedY = tempX*math.sin(a) + tempY*math.cos(a)

        newX = rotatedX + cx
        newY = rotatedY + cy
        newZ = z

        self.x,self.y,self.z = newX,newY,newZ

        self.refresh()
        return newX,newY,newZ

    # SCALING
    def scale(self,factor,pivot,directions = ["x","y","z"]):
        x,y,z = newX,newY,newZ = self.x,self.y,self.z
        cx,cy,cz = pivot

        dx = x - cx
        dy = y - cy
        dz = z - cz

        if "x" in directions:
            newX = cx + dx * factor
        if "y" in directions:
            newY = cy + dy * factor
        if "z" in directions:
            newZ = cz + dz * factor

        self.x,self.y,self.z = newX,newY,newZ
        self.refresh()
        return newX,newY,newZ


    

class edge:
    def __init__(self,start:point,end:point):
        self.start = start
        self.end = end

        self.STROKE_COLOR = (0,0,0)
        self.STROKE_WIDTH = 4

        objects.append(self)
        edges.append(self)
    def draw(self):
        self.line = pygame.draw.line(screen,self.STROKE_COLOR,(self.start.mark.rect.center),(self.end.mark.rect.center),3)

class cube:
    def __init__(self,center:tuple[float,float,float],size):
        self.x,self.y,self.z = x,y,z = center
        self.size = size
        halfSize = size/2
        self.xRotation = 0
        self.yRotation = 0
        self.zRotation = 0

        self.xSize,self.ySize,self.zSize = size,size,size

        # creating vertices
        self.vertices = [
            # front wall
            point(x-halfSize,y+halfSize,z-halfSize),
            point(x-halfSize,y-halfSize,z-halfSize),
            point(x+halfSize,y-halfSize,z-halfSize),
            point(x+halfSize,y+halfSize,z-halfSize),

            # back wall
            point(x-halfSize,y+halfSize,z+halfSize),
            point(x-halfSize,y-halfSize,z+halfSize),
            point(x+halfSize,y-halfSize,z+halfSize),
            point(x+halfSize,y+halfSize,z+halfSize),
        ]

        self.edges = [
            # front wall
            self.edgeFromIndices(0,1),
            self.edgeFromIndices(1,2),
            self.edgeFromIndices(2,3),
            self.edgeFromIndices(3,0),

            # back wall
            self.edgeFromIndices(4,5),
            self.edgeFromIndices(5,6),
            self.edgeFromIndices(6,7),
            self.edgeFromIndices(7,4),

            # sides
            self.edgeFromIndices(0,4),
            self.edgeFromIndices(1,5),
            self.edgeFromIndices(2,6),
            self.edgeFromIndices(3,7),
        ]

        self.walls = [
            self.wallFromIndices(0,1,2,3), # front wall
            self.wallFromIndices(4,5,6,7), # back wall
            self.wallFromIndices(1,5,4,0), # left wall
            self.wallFromIndices(2,6,7,3), # right wall
            self.wallFromIndices(1,5,6,2), # top wall
            self.wallFromIndices(0,4,7,3), # bottom wall
        ]
        meshes.append(self)

    def wallFromIndices(self,i1,i2,i3,i4):
        return wall([self.vertices[i1],self.vertices[i2],self.vertices[i3],self.vertices[i4]])

    def wallFromEdgeIndices(self,e1,e2,e3,e4):
        return wall([self.edges[e1],self.edges[e2],self.edges[e3],self.edges[e4], "orange"])

    def edgeFromIndices(self,i1,i2):
        return edge(self.vertices[i1],self.vertices[i2])

    # MOVING(TRANSLATING)
    def move(self,axis,amt):
        if axis == "x":
            self.moveX(amt)
        elif axis == "y":
            self.moveY(amt)
        elif axis == "z":
            self.moveZ(amt)
        else:
            return print("ivalid axis input")
        render()

    def moveX(self,amt):
        self.x += amt
        for vertex in self.vertices:
            vertex.moveX(amt)

    def moveY(self,amt):
        amt *= -1
        self.y += amt

        for vertex in self.vertices:
            vertex.moveY(amt)

    def moveZ(self,amt):
        self.z += amt

        for vertex in self.vertices:
            vertex.moveZ(amt)

    # ROTATING
    def rotate(self,axis,amt, custom = False):
        usedAmt = amt*30 if not custom else amt

        if axis == "x":
            self.rotateX(usedAmt)
            self.xRotation = divmod(self.xRotation,360)[1]
            # self.moveY(amt/14)
        elif axis == "y":
            self.rotateY(usedAmt)
            self.yRotation = divmod(self.yRotation,360)[1]
            # self.moveX(-amt/24)
        elif axis == "z":
            self.rotateZ(usedAmt)
            self.zRotation = divmod(self.zRotation,360)[1]
        else:
            return print("invalid axis input")
        render()

        
    def rotateX(self,amt):
        self.xRotation += amt

        for vertex in self.vertices:
            vertex.rotateX(amt, (self.x,self.y,self.z))

    def rotateY(self,amt):
        self.yRotation += amt

        for vertex in self.vertices:
            vertex.rotateY(amt, (self.x,self.y,self.z))

    def rotateZ(self,amt):
        self.zRotation += amt

        for vertex in self.vertices:
            vertex.rotateZ(amt, (self.x,self.y,self.z))

    # SCALING
    def scale(self, axis, factore):
        if factore <= 0:
            return
        factor = factore

        if axis == "":
            self.size *= factor
            self.xSize *= factor
            self.ySize *= factor
            self.zSize *= factor

            for vertex in self.vertices:
                vertex.scale(factor, (self.x,self.y,self.z))

        if axis == "x":
            self.xSize *= factor

            for vertex in self.vertices:
                vertex.scale(factor, (self.x,self.y,self.z),directions=["x"])        

        if axis == "y":
            self.ySize *= factor

            for vertex in self.vertices:
                vertex.scale(factor, (self.x,self.y,self.z), directions=["y"])        

        if axis == "z":
            self.zSize *= factor

            for vertex in self.vertices:
                vertex.scale(factor, (self.x,self.y,self.z), directions=["z"])
        render()

    def destroy(self):
        if CURRENT_AXIS != "":
            return

        for v in self.vertices:
            points.remove(v)

        for e in self.edges:
            objects.remove(e)

        objects.remove(self)
        meshes.remove(self)
        del self
        

class circle(cube):
    def __init__(self, center, vertexes, radius):
        self.vertices = []
        self.edges = []
        self.walls = []

        self.x,self.y,self.z = cx,cy,cz = center
        self.size = radius*2
        self.xRotation = 0
        self.yRotation = 0
        self.zRotation = 0

        self.xSize,self.ySize,self.zSize = radius*2,radius*2,radius*2
        for i in range(vertexes):
            angle = i * (math.pi*2/vertexes)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            self.vertices.append(point(x,y,cz))

        for vertexIndex in range(len(self.vertices)):
            if vertexIndex == len(self.vertices)-1:
                self.edges.append(edge(self.vertices[vertexIndex],self.vertices[0]))
                continue
            self.edges.append(edge(self.vertices[vertexIndex],self.vertices[vertexIndex+1]))

class wall:
    def __init__(self,points):
        self.points = points
        self.pointCenters = []
        self.polygon = None
        self.color = (100,100,100)
        
        self.EDGE_COLOR = "black"

        if len(points) < 3:
            return


        for p in self.points:
            p:point
            self.pointCenters.append(p.mark.rect.center)

        objects.append(self)
        walls.append(self)

    def draw(self):
        self.refresh()
        self.polygon = pygame.draw.polygon(screen, self.color, self.pointCenters)
        # self.polygonOutline = pygame.draw.polygon(screen, self.EDGE_COLOR, self.pointCenters,width=3)

    def refresh(self):
        self.pointCenters = []
        if len(points) < 3:
            return

        for p in self.points:
            p:point
            self.pointCenters.append(p.mark.rect.center)

class sphere(cube):
    def __init__(self, radius, center, vertexes):
        cx,cy,cz = self.x,self.y,self.z = center
        zCopy = self.z
        self.xSize,self.ySize,self.zSize = radius*2,radius*2,radius*2

        self.xRotation,self.yRotation,self.zRotation = 0,0,0

        self.vertices = []
        self.edges = []
        self.walls = []
        self.layers = []

        zLevels = np.linspace(-radius,radius,vertexes)

        for z in zLevels:
            if z == 0:
                continue
            r = np.sqrt(radius**2 - z**2)
            newLayer = circle((cx,cy,z), vertexes, r)
            self.vertices.extend(newLayer.vertices)
            self.edges.extend(newLayer.edges)
            self.layers.append(newLayer)

        # connect layers
        for layerIndex, l in enumerate(self.layers):
            l:circle
            for vertexIndex, v in enumerate(l.vertices):
                if layerIndex + 1 == len(self.layers):
                    break
                self.edges.append(edge(l.vertices[vertexIndex], self.layers[layerIndex+1].vertices[vertexIndex]))
                # self.walls.append(wall([l.vertices[vertexIndex],
                #                          self.layers[layerIndex+1].vertices[vertexIndex], 
                #                          l.vertices[vertexIndex+1],
                #                          self.layers[layerIndex+1].vertices[vertexIndex+1]]))
        

        middleCircle = self.layers[len(self.layers)//2-1]
        self.x,self.y,self.z = middleCircle.x,middleCircle.y,middleCircle.z
        self.moveZ(zCopy-self.z)


        




        


mainPoint:point = None
def placeObjects():
    global selectedObject

    # cube((0.2,0.2,1),0.2)
    selectedObject = sphere(0.1,(0.1,0.1,0.5),12)
    # circle((0.1,0.1,2),12,12)

placeObjects()


def render():
    display.fill((200,200,200))
    for i in images:
        i.draw()
    display.blit(screen,(0,0))
    for m in marks:
        m.draw()
    screen.fill("white")
    for w in walls:
        w.draw()
    for e in  edges:
        e.draw()

    

def doAction(factor=1):
    try:
        if actionPerforming == selectedObject.scale:  
            if factor == 1:
                actionPerforming(CURRENT_AXIS, factor+PER_FRAME_VALUE)
            else:
                actionPerforming(CURRENT_AXIS, 1-PER_FRAME_VALUE)
        else:
            actionPerforming(CURRENT_AXIS,factor*PER_FRAME_VALUE)
    except:
        pass
    showActionProperties()

def doActionCustomAmt(amt):
    try:
        if actionPerforming == selectedObject.rotate:
            actionPerforming(CURRENT_AXIS, amt,custom=True)
        else:
            actionPerforming(CURRENT_AXIS, amt)
    except:
        pass


PER_FRAME_VALUE = 0.02
BUFFED_PER_FRAME_VALUE = 0.1
DEFAULT_PER_FRAME_VALUE = PER_FRAME_VALUE
NERFED_PER_FRAME_VALUE = 0.002

KEY_BINDINGS = {
    pygame.K_UP: lambda: doAction(1),
    pygame.K_DOWN: lambda: doAction(-1),

    pygame.K_ESCAPE: lambda: (globals().__setitem__("actionPerforming",None), globals().__setitem__("CURRENT_AXIS","")),
}
ACTIONS = {
    pygame.K_r: selectedObject.rotate,
    pygame.K_g: selectedObject.move,
    pygame.K_s: selectedObject.scale,
    pygame.K_q: selectedObject.destroy
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
    pygame.K_MINUS: "-",
    pygame.K_PERIOD: ".",
}

READABLE_ACTION_NAMES = {
    selectedObject.rotate: "ROTATION",
    selectedObject.move: "MOVING",
    selectedObject.scale: "SCALING"
}

AXIS_KEYS = {
    pygame.K_x: "x",
    pygame.K_y: "y",
    pygame.K_z: "z",
}
CURRENT_AXIS = ""

actionPerforming = None
canPressAgain = True

numberExpression = ""
def control():
    global PER_FRAME_VALUE,NERFED_PER_FRAME_VALUE,BUFFED_PER_FRAME_VALUE, CURRENT_AXIS, actionPerforming, canPressAgain, numberExpression

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
        PER_FRAME_VALUE = BUFFED_PER_FRAME_VALUE

    elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        PER_FRAME_VALUE = NERFED_PER_FRAME_VALUE

    else:
        PER_FRAME_VALUE = DEFAULT_PER_FRAME_VALUE

    for key, action in ACTIONS.items():
        if keys[key]:
            actionPerforming = action
            CURRENT_AXIS = ""
            showActionProperties()

    if actionPerforming is not None:
        for key, axis in AXIS_KEYS.items():
            if keys[key]:
                CURRENT_AXIS = axis
                showActionProperties()
        for numKey,num in NUMBERS.items():
            if keys[numKey] and canPressAgain:
                numberExpression = numberExpression + str(num)
                showActionProperties()
                canPressAgain = False
        if keys[pygame.K_RETURN] and numberExpression != "":
            doActionCustomAmt(float(numberExpression))
            numberExpression = ""
            showActionProperties()
        if keys[pygame.K_BACKSPACE] and numberExpression != "" and canPressAgain:
            numberExpression = numberExpression[:-1]
            canPressAgain = False
            showActionProperties()

    for key, action in KEY_BINDINGS.items():
        if keys[key]:
            action() 
            canPressAgain = False

    if not any(keys):
        canPressAgain = True  

    
                     
def createStringWithSpaces(strs:list[str], space:str) -> str:
    """Makes a string of all small strings provided with preferable spaces between them.
    Turns an element into a string if it's not one already."""

    string = ""
    for s in strs:
        string = string + str(s)
        string = string + space

    return string

def showActionProperties():
    global actionImage, axisImage,numberExpressionImage, sizeImage

    images.clear()

    readableActName = ""
    for action, readable in READABLE_ACTION_NAMES.items():
        if actionPerforming == action:
            readableActName = readable.upper()

    currentAxis = CURRENT_AXIS.upper()

    positionStr = createStringWithSpaces(["POSITION:", round(selectedObject.x,2),round(selectedObject.y,2),round(selectedObject.z,2)], "     ")
    rotationStr = createStringWithSpaces(["ROTATION:", round(selectedObject.xRotation,2),round(selectedObject.yRotation,2),round(selectedObject.zRotation,2)], "     ")
    sizeStr = createStringWithSpaces(["SIZE:        ", round(selectedObject.xSize,2),round(selectedObject.ySize,2),round(selectedObject.zSize,2)], "      ")
    axesStr = createStringWithSpaces(["X","Y","Z"], "       ")



    actionImage = renderText(20,HEIGHT-100,readableActName,"black")
    axisImage = renderText(WIDTH//2-30, HEIGHT-100, currentAxis, "black")
    numberExpressionImage = renderText(WIDTH-200, HEIGHT-100, numberExpression, "black")
    sizeImage = renderText(20,HEIGHT-100-actionImage.height, sizeStr, "black")
    rotationImage = renderText(20,sizeImage.y-sizeImage.height, rotationStr, "black")
    positionStr = renderText(20, rotationImage.y-rotationImage.height, positionStr, "black")
    axesImage = renderText(350,positionStr.y-positionStr.height-10,axesStr, "black")
    


showActionProperties()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



    control()    
    render()



    pygame.display.flip()

    clock.tick(60)

pygame.quit()