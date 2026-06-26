def indexDict (dict,obj):
    index = -1
    for val in dict.values():
        index += 1
        if val == obj:
            return index 
        

test = {
    "s":12,
    "o":13
}

print(indexDict(test,13))