def getTermSize():
    import shutil
    termSize = shutil.get_terminal_size((80,20))
    return termSize

def checkTermSize():
    if getTermSize().lines < 20 or getTermSize().columns < 80:
        print("Too Small Terminal Size")
        quit()

def clearScreen():
    from os import system, name
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')