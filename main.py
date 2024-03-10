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
CX = 0
CY = 0

""" terminal """


def die(msg):
    sys.stderr.write("error-> " + msg + "\r\n")
    sys.exit(1)


def enable_raw_mode():
    # standard input
    fd = sys.stdin.fileno()

    try:
        # save original settings
        original_termios = termios.tcgetattr(fd)
    except termios.error as e:
        die(str(e))

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
    except termios.error as e:
        die(str(e))


# TODO: might need error handling
def editor_read_key():
    # read one character
    c = sys.stdin.read(1)
    if c == "\x1b":
        c = sys.stdin.read(2)
        match c:
            case "[A":
                return "k"
            case "[B":
                return "j"
            case "[C":
                return "l"
            case "[D":
                return "h"

    # ascii value
    # print(ord(c), c, end="\r\n")
    return c


def get_window_size():
    columns, rows = os.get_terminal_size(0)
    return columns, rows


""" TODO: APPEND BUFFER(maybe) """


""" output """


def editor_refresh_screen():
    # \x1b -> escape character
    # NOTE: "\x1b\[K -> clear line from cursor right"
    # [2J -> clear entire screen
    sys.stdout.write("\x1b[2J")
    # \x1b[H -> move cursor top-left corner
    sys.stdout.write("\x1b[H")
    # writes output stream
    sys.stdout.flush()


def editor_draw_rows():
    columns, rows = get_window_size()

    for i in range(rows):
        sys.stdout.write("\x1b[K")

        if i != rows - 1:
            sys.stdout.write("~\r\n")
            if i == rows // 2.5:
                welcome_msg = "SerpenScripter -- version " + VERSION + "\r\n"
                centered_msg = center_text(welcome_msg, columns)
                sys.stdout.write("~" + centered_msg[1:])
        else:
            sys.stdout.write("~")


def center_text(msg, width):
    padding = max((width - len(msg)) // 2, 0)
    return " " * padding + msg


""" input """


def editor_move_cursor(key):
    global CX, CY

    match key:
        case "h":
            CX -= 1
        case "l":
            CX += 1
        case "k":
            CY -= 1
        case "j":
            CY += 1
    if key in ["h", "l", "k", "j"]:
        sys.stdout.write(f"\x1b[{CY+1};{CX+1}H")
        sys.stdout.flush()


def editor_process_keypress(raw_mode):
    while True:
        c = editor_read_key()
        editor_move_cursor(c)
        # quit -> ctrl-q
        if ord(c) == 17:
            break

    # exit raw mode
    disable_raw_mode(raw_mode)
    editor_refresh_screen()
    sys.exit(0)


""" init """


def init_editor():
    # hide cursor
    sys.stdout.write("\x1b[?25l")

    editor_draw_rows()
    # \x1b[H -> move cursor top-left corner
    sys.stdout.write("\x1b[H")

    # show cursor
    sys.stdout.write("\x1b[?25h")

    # writes output stream
    sys.stdout.flush()


def main():
    # raw mode and save settings
    original_termios = enable_raw_mode()

    init_editor()
    editor_process_keypress(original_termios)


if __name__ == "__main__":
    main()
