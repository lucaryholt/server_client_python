import socket, sys

def connectionProtocol(conn):
    sendMessage("com-0 " + get_ip())
    if correctAcceptProtocol(receiveData(conn)):
        sendMessage("com-0 accept")
        return True

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('255.255.255.255', 1))
        IP = s.getsockname()[0]
    finally:
        s.close()
    return IP

def correctAcceptProtocol(text):
    data = text.split(" ")
    return data[0] == "com-0" and data[1] == "accept" and isIP(data[2])

def isIP(text):
    return len(text.split(".")) == 4

def sendMessage(text):
    client.sendto(text.encode(),(serverName, serverPort))

def receiveData(socket):
    while True:
        data, serverAddress = socket.recvfrom(4096)
        if debug:
            print("raw: " + data.decode()) #debug line
        return data.decode()

def readMessage(text):
    return text.split("=")[1]

def sendChatMessage(text):
    global seqnr
    increaseSeqnr()
    sendMessage("msg-" + str(seqnr) + "=" + text)

def increaseSeqnr():
    global seqnr
    seqnr = seqnr + 1

def extractSeqnr(text):
    return (text.split("=")[0]).split("-")[1]

def correctSeqnr(text):
    global seqnr
    if int(extractSeqnr(text)) - seqnr == 1:
        return True

#The code starts here
debug = False

if len(sys.argv) == 2:
    if sys.argv[1] == "-help":
        print("Use -debug to see raw incoming messages")
        exit()
    if sys.argv[1] == "-debug":
        debug = True

serverName = '0.0.0.0'
serverPort = 5000
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seqnr = -1

if connectionProtocol(client) == False:
    exit()
print("The connection is ready!")

message = input('Message: ')
while message != 'Q':
    sendChatMessage(message)
    data = receiveData(client)
    if correctSeqnr(data):
        print(readMessage(data))
        increaseSeqnr()
    else:
        exit()
    message = input('Message: ')

client.close()
