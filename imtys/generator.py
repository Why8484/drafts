import random

def generate ():
    possible = [1,2,3,4,5,6,7,8,9]

    count = ""
    while type(count) != int:    
        count = int(input("SKOLKO? "))

    output = []
    for _ in range(count):
        output.append(random.choice(possible))
    
    return output

