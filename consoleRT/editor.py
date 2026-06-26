from PIL import Image,ImageGrab


retry = True
while retry:
    path = input("Enter path: ")
    if path == "clipboard":
        img = ImageGrab.grabclipboard()
        if img:
            retry = False
    else:    
        img = Image.open(path).convert("RGB")
        retry = False

pixels = list(img.getdata())
pixelsNCoords = []

for y in range(img.height):    
    pixelsNCoords.append([])
    for x in range(img.width):
        pixelsNCoords[y].append(pixels[y*img.width+x])


print(pixelsNCoords)
