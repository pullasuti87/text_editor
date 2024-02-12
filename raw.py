# raw mode -> key press is immediately sent to the program with out press Enter

# notes:
# ICANON -> reading line by line, when disabled input is read byte by byte
# ECHO -> prints key (terminal) that is typed
# tty.setraw seems to disable lot of flags (not sure which ones),
# but hey it works!


import sys
import termios
import tty

# import signal


def enable_raw_mode():
    # standard input
    fd = sys.stdin.fileno()

    # save original settings
    original_termios = termios.tcgetattr(fd)

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

    # restore terminal settings
    termios.tcsetattr(fd, termios.TCSAFLUSH, original_termios)


def main():
    # raw mode and save settings
    original_termios = enable_raw_mode()

    try:

        while True:
            # read one character
            c = sys.stdin.read(1)

            # ascii value
            print(ord(c), end="\r\n")

            # quit
            if c == "q":
                break
    finally:
        # exit raw mode
        disable_raw_mode(original_termios)

    # timeout


if __name__ == "__main__":
    main()
