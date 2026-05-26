import random

def generate (low,high):
    possible = list(range(low,high))
    if not possible:
        print("imtis yra tuscia")
        return False

    count = ""
    while type(count) != int:    
        count = int(input("KIEK? "))

    output = []
    for _ in range(count):
        output.append(random.choice(possible))
    
    return output

