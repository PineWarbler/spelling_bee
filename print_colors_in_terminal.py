from colorama import Fore


def PrintAngry(msg, useColors):
    if useColors:
        print(Fore.RED + msg)
    else:
        print(msg)


def PrintGreen(msg, useColors):
    if useColors:
        print(Fore.GREEN + msg)
    else:
        print(msg)


def PrintYellow(msg, useColors):
    if useColors:
        print(Fore.YELLOW + msg)
    else:
        print(msg)
