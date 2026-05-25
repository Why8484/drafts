import tabulate
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

def main ():
    imtis = input("RASAI IMTI: ")

    splitter = input("kas atskiria narius?('enter' kad butu ',') ")
    if splitter == "":
        splitter = ","
            

    array = imtis
    array = array.split(splitter)
    array = list(map(int, array))

    array.sort()
    order = str(array)
    order.replace("[","")
    order.replace("]","")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"parasyta is eiles: {order}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"maziausias: {min(array)}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"didziausias: {max(array)}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    elements = []
    class element:
        def __init__(self, value, freq, cumulFreq):
            self.value = value
            self.freq = freq
            self.cumulFreq = cumulFreq
            elements.append(self)

    length = len(array)


    summ = 0
    used = []
    for num in array:
        if num in used:
            continue
        used.append(num)
        freq = array.count(num)
        element(num, freq, summ+freq)
        summ += freq



    data = [
        ["DAZNIAI: "],
        ["SUKAUPTIEJI DAZNIAI: "],
        ["SANTYKINIAI DAZNIAI: "],
        ["SANTIKINIAI SUKAUPTIEJI DAZNIAI: "],
    ]

    headers = ["NARIAI: "]

    for e in elements:
        e:element
        headers.append(e.value)
        data[0].append(e.freq)
        data[1].append(e.cumulFreq)
        data[2].append(f"{e.freq}/{length}")
        data[3].append(f"{e.cumulFreq}/{length}")

    print(tabulate.tabulate(data, headers=headers, tablefmt="grid"))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60


pygame.quit()




        