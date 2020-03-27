yellow = "\u001b[33m"
red = "\u001b[31m"
green = "\u001b[32m"
cyan = "\u001b[36m"
magenta = "\u001b[35m"
reset = "\u001b[0m"

def debug(text):
    printmessage(text, yellow)

def debugSend(text):
    printmessage(text, cyan)

def debugRecv(text):
    printmessage(text, magenta)

def error(text):
    printmessage(text, red)

def success(text):
    printmessage(text, green)

def printmessage(text, colour):
    print(colour + text + reset)
