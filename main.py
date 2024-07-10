# raw mode -> key press is immediately sent to the program with out press Enter

# notes:
# ICANON -> reading line by line, when disabled input is read byte by byte
# ECHO -> prints key (terminal) that is typed
# tty.setraw seems to disable lot of flags (not sure which ones),
# but hey it works!


import sys
import os
import termios
import tty

# import signal

VERSION = "1.0.0"
# cursor x and y
CX = 1
CY = 0
ARROW_UP = 1000
ARROW_DOWN = 1001
ARROW_RIGHT = 1002
ARROW_LEFT = 1003
DEL_KEY = 1004
HOME_KEY = 1005
END_KEY = 1006
PAGE_UP = 1007
PAGE_DOWN = 1008

""" terminal """


def error_msg(msg):
    sys.stderr.write("error-> " + msg + "\r\n")
    sys.exit(1)


def enable_raw_mode():
    # standard input
    fd = sys.stdin.fileno()

    try:
        # save original settings
        original_termios = termios.tcgetattr(fd)
    except termios.error as e:
        error_msg(str(e))

    # terminal to raw mode (disables ICANON and ECHO flags)
    tty.setraw(fd)

    # seems that is not needed
    # block (ctrl-c -> SIGINT) and (ctrl-z -> SIGTSTP)
    # just in case, seems to be disabled by default in raw
    # signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTSTP})

    return original_termios


def disable_raw_mode(original_termios):
    # standard input
    fd = sys.stdin.fileno()

    # unblock (ctrl-c -> SIGINT) and (ctrl-z -> SIGTSTP)
    # signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGINT, signal.SIGTSTP})
    try:
        # restore terminal settings
        termios.tcsetattr(fd, termios.TCSAFLUSH, original_termios)
        # reset colors
        sys.stdout.write("\x1b[m")
    except termios.error as e:
        error_msg(str(e))


# TODO: error handling
def read_key():
    global ARROW_UP, ARROW_DOWN, ARROW_RIGHT, ARROW_LEFT, PAGE_UP, PAGE_DOWN
    # read one character
    c = sys.stdin.read(1)
    if c == "\x1b":
        c = sys.stdin.read(2)
        match c:
            case "[A":
                return ARROW_UP
            case "[B":
                return ARROW_DOWN
            case "[C":
                return ARROW_RIGHT
            case "[D":
                return ARROW_LEFT
            case "[5":
                return PAGE_UP
            case "[6":
                return PAGE_DOWN
            case "[H":
                return HOME_KEY
            case "[F":
                return END_KEY
            case "[3":
                return DEL_KEY

    # ascii value
    return c


def get_window_size():
    columns, rows = os.get_terminal_size(0)
    return columns, rows


""" TODO: APPEND BUFFER(maybe) """


""" output """


def refresh_screen():
    # \x1b -> escape character
    # NOTE: "\x1b\[K -> clear line from cursor right"
    # [2J -> clear entire screen
    sys.stdout.write("\x1b[2J")
    # \x1b[H -> move cursor top-left corner
    sys.stdout.write("\x1b[H")
    # writes output stream
    sys.stdout.flush()


def draw_rows():
    columns, rows = get_window_size()

    for i in range(rows):
        sys.stdout.write("~\r\n")
        if i == rows // 2.5:
            title = "SerpenScripter -- version " + VERSION + "\r\n"
            centered_title = center_text(title, columns)
            sys.stdout.write("~" + centered_title)


def center_text(msg, width):
    padding = max((width - len(msg)) // 2, 0)
    return " " * padding + msg


def clear_title():
    columns, rows = get_window_size()
    column = 2
    row = rows // 2.5
    sys.stdout.write(f"\x1b[{int(row)};{column}H")
    # erase from cursor to end of line
    sys.stdout.write("\x1b[K")


def draw_statusline(filename=None):
    columns, rows = get_window_size()

    # last line
    sys.stdout.write(f"\x1b[{rows-1};0H")
    # background color
    sys.stdout.write("\x1b[42;1m")

    """ feels little hacky """
    if filename:
        sys.stdout.write("  " + filename + (" " * (columns - len("  " + filename))))
    else:
        sys.stdout.write("  [no name]" + (" " * (columns - len("  [no name]"))))

    # reset color
    sys.stdout.write("\x1b[m")
    sys.stdout.flush()


""" input """


def move_cursor(key):
    global CX, CY, ARROW_UP, ARROW_DOWN, ARROW_RIGHT, ARROW_LEFT

    if key == ARROW_UP:
        if CY > 0:
            CY -= 1
    elif key == ARROW_DOWN:
        if CY < get_window_size()[1] - 3:
            CY += 1
    elif key == ARROW_RIGHT:
        if CX < get_window_size()[0] - 1:
            CX += 1
    elif key == ARROW_LEFT:
        if CX > 1:
            CX -= 1

    if key in [ARROW_UP, ARROW_DOWN, ARROW_RIGHT, ARROW_LEFT]:
        move_cursor_to(CX, CY)


def move_cursor_to(x, y):
    sys.stdout.write(f"\x1b[{y+1};{x+1}H")
    sys.stdout.flush()


def move_multiple_lines(direction, lines):
    for _ in range(lines):
        move_cursor(direction)


def process_keypress(raw_mode):
    global PAGE_UP, PAGE_DOWN, HOME_KEY, END_KEY, DEL_KEY, CX, CY
    while True:
        c = read_key()
        move_cursor(c)

        if c == PAGE_UP:
            move_multiple_lines(ARROW_UP, get_window_size()[1] - 1)
        elif c == PAGE_DOWN:
            move_multiple_lines(ARROW_DOWN, get_window_size()[1] - 2)
        elif c == HOME_KEY:
            CX = 1
            move_cursor_to(CX, CY)
        elif c == END_KEY:
            CX = get_window_size()[0] - 1
            move_cursor_to(CX, CY)
        elif c == DEL_KEY:
            print("delete")

        if not isinstance(c, int) and len(c) == 1:
            if ord(c) == 17:
                break
            else:
                continue
        else:
            continue

    # exit raw mode
    disable_raw_mode(raw_mode)
    refresh_screen()
    sys.exit(0)


""" init """


def init_editor():
    # hide cursor
    sys.stdout.write("\x1b[?25l")

    draw_rows()
    if len(sys.argv) > 1:
        draw_statusline(sys.argv[1])
    else:
        draw_statusline()
    # \x1b[H -> move cursor top-second-left corner
    sys.stdout.write("\x1b[1;2H")

    # show cursor
    sys.stdout.write("\x1b[?25h")

    # writes output stream
    sys.stdout.flush()


def main():
    # raw mode and save settings
    original_termios = enable_raw_mode()

    init_editor()

    """ TODO: change this"""
    clear_title()

    process_keypress(original_termios)


if __name__ == "__main__":
    main()
