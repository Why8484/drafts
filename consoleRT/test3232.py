import pygetwindow as gw
import time
import os

col,row = os.get_terminal_size()

# Give yourself a second to make sure the terminal is the active window
time.sleep(0.5)

while True:
    # Get the currently active window
    win = gw.getActiveWindow()

    if win:
        print(f"Terminal Title: {win.title}")
        print(f"Position (X, Y): ({win.left}, {win.top})")
        print(f"Size (Width x Height in pixels): {win.width}x{win.height}")
    else:
        print("Could not find active window.")

    input()