from colorama import Fore, Style


def PrintAngry(msg, useColors):
    if useColors:
        print(Fore.RED + msg + Style.RESET_ALL)
    else:
        print(msg)


def PrintGreen(msg, useColors):
    if useColors:
        print(Fore.GREEN + msg + Style.RESET_ALL)
    else:
        print(msg)


def PrintYellow(msg, useColors):
    if useColors:
        print(Fore.YELLOW + msg + Style.RESET_ALL)
    else:
        print(msg)
