import sys
import termios
import tty


def enable_raw_mode():
    # standard input
    fd = sys.stdin.fileno()

    # save original settings
    original_termios = termios.tcgetattr(fd)

    # Set the terminal to raw mode
    tty.setraw(fd)

    return original_termios


def disable_raw_mode(original_termios):
    # standard input
    fd = sys.stdin.fileno()

    # restore terminal settings
    termios.tcsetattr(fd, termios.TCSAFLUSH, original_termios)


def main():
    # raw mode and save settings
    original_termios = enable_raw_mode()

    try:
        while True:
            # read one character
            c = sys.stdin.read(1)

            # quit
            if c == "q":
                break
    finally:
        # exit raw mode
        disable_raw_mode(original_termios)


if __name__ == "__main__":
    main()
