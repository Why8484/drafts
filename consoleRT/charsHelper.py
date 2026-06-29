string = """$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,"^`'. """
lst = list(string)
lst.reverse()

for i, e in enumerate(lst):
    print(f'{i}: "{e}",')

