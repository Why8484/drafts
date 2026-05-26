import tabulate
import generator
import pipiriene
import math


elements = []
class element:
    def __init__(self, value, freq, cumulFreq):
        self.value = value
        self.freq = freq
        self.cumulFreq = cumulFreq
        elements.append(self)


maxIntervalLength = 15


def printInterval (interval, lowerBound, upperBound,arrayLength,things):
    data = [
        ["DAZNIAI: "],
        ["SUKAUPTIEJI DAZNIAI: "],
        ["SANTYKINIAI DAZNIAI: "],
        ["SANTIKINIAI SUKAUPTIEJI DAZNIAI: "],
    ]

    headers = ["NARIAI: "]

    for e in things:
        e:element
        headers.append(e.value)
        data[0].append(e.freq)
        data[1].append(e.cumulFreq)
        data[2].append(f"{e.freq}/{arrayLength}")
        data[3].append(f"{e.cumulFreq}/{arrayLength}")

    print(f"intervalas {interval} ({lowerBound}-{upperBound}):")
    print(tabulate.tabulate(data, headers=headers, tablefmt="grid"))

def ifTooBig ():
    global maxIntervalLength

    newIntervalLength = input(f"po kiek duomenu tures intervalai? ('enter' kad palikti po {maxIntervalLength}) ")
    if newIntervalLength != "":
        try:    
            maxIntervalLength = int(newIntervalLength)
        except:
            pass
    
    intervalCount = math.ceil(len(elements)/maxIntervalLength)
    for i in range(intervalCount):    
        lowerBound = elements[maxIntervalLength*i].value
        try:    
            upperBound = elements[maxIntervalLength*(i+1)].value
            upp = maxIntervalLength*(i+1)
        except:
            upperBound = elements[-1].value
            upp = -1
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        printInterval(i+1,lowerBound,upperBound,len(elements),elements[maxIntervalLength*i:upp])
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    

lowerBound = 0
upperBound = 10

def main ():
    global lowerBound,upperBound

    imtis = input("IMTIS: ")
    
    if imtis == "random":    
        possibleCount = input(f"kokie skaiciai? (ivesti reikia taip: apatine riba -- virsutine riba)('enter' kad butu {lowerBound}-{upperBound}) ")
        if possibleCount != "":
            possibleCount = possibleCount.split("--")
            if len(possibleCount) != 2: 
                print("ivesk apatine ir virsutine ribas")
                return
            lowerBound,upperBound = possibleCount
            lowerBound = int(lowerBound)
            upperBound = int(upperBound)

        imtis = str(generator.generate(lowerBound,upperBound))
        if imtis == "False":
            return
        imtis = imtis.replace("]","")
        imtis = imtis.replace("[","")
        splitter = ", "
        print(imtis)
    elif imtis == "pipiriene":
        print(pipiriene.pipiriene)
        return

    try:
        splitter
    except:    
        splitter = input("kas atskiria narius?('enter' kad butu ',') ")
        if splitter == "":
            splitter = ","
            
    array = imtis
    array = array.split(splitter)
    try:    
        array = list(map(float, array))
    except:
        print("ivesk skaicius")
        return

    array.sort()
    order = str(array)
    order = order.replace("[","")
    order = order.replace("]","")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"parasyta is eiles: {order}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"maziausias: {min(array)}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"didziausias: {max(array)}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"nariu: {len(array)}")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")



    summ = 0
    used = []
    for num in array:
        if num in used:
            continue
        used.append(num)
        freq = array.count(num)
        element(int(num), freq, summ+freq)
        summ += freq

    if len(elements) > maxIntervalLength:
        print("lentele per didele")
        inter = input("paskirstyt i intervalus? (taip/ne) ")
        if inter == "taip":
            ifTooBig()
            return
    
    values = []
    for el in elements:
        values.append(el.value)
    printInterval(0,0,max(values),len(array),elements)


while True:
    main()    
    if input("iseiti? (taip/ne) ") == "taip":
        break
    elements.clear()


    