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


"""  terminal """


def die(msg):
    sys.stderr.write("error-> " + msg + "\r\n")
    sys.exit(1)


def enable_raw_mode():
    # standard input
    fd = sys.stdin.fileno()

    try:
        # save original settings
        original_termios = termios.tcgetattr(fd)

        # terminal to raw mode (disables ICANON and ECHO flags)
        tty.setraw(fd)
    except termios.error as e:
        die(str(e))

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


"""  init """


def main():
    # raw mode and save settings
    original_termios = enable_raw_mode()

    try:

        while True:
            # read one character
            c = sys.stdin.read(1)

            # ascii value
            print(ord(c), c, end="\r\n")

            # quit -> ctrl-q
            if ord(c) == 17:
                break
    finally:
        # exit raw mode
        disable_raw_mode(original_termios)


if __name__ == "__main__":
    main()
