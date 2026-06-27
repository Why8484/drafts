



def Mode():
    chance = float(input("chance: "))
    goodChance =  float(input("good chance: "))
    res = 0
    resChance = 0


    def getChance(chance,tries):
        combined = (1-((1-(chance/100))**tries))*100
        return combined

    for x in range(1,1000000):
        combined = getChance(chance,x)
        if combined >= goodChance:
            res = x
            resChance = combined
            break

    print(f"{res} tries for {resChance}%")

def noMode ():
    chance = float(input("chance: "))
    tries =  float(input("tries: "))


    def getChance(chance,tries):
        combined = (1-((1-(chance/100))**tries))*100
        return combined

    print(getChance(chance,tries))

while True:
    mode = input("use mode(how many tries for good chance)(y/n)? ")

    if mode == "n":
        noMode()
    else:
        Mode()

    if input("press 'enter' to exit ...") == "":
        break
