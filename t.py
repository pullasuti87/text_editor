import sys
import termios
import tty
import os


def getch():
    """single character from input"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def print_screen(lines, top, height):
    os.system("clear")
    for i in range(height):
        if top + i < len(lines):
            print(lines[top + i])


lines = [f"Line {i}" for i in range(1, 101)]
top_line = 0
screen_height = os.get_terminal_size().lines - 1

print_screen(lines, top_line, screen_height)

while True:
    key = getch()

    if key == "q":
        break
    elif key == "\x1b":  # arrow key prefix
        key = getch()
        if key == "[":
            key = getch()
            if key == "A" and top_line > 0:  # up
                top_line -= 1
            elif key == "B" and top_line < len(lines) - screen_height:  # down
                top_line += 1

    print_screen(lines, top_line, screen_height)
