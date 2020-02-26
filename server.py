import socket, sys

def sendMessage(text, conn):
    conn.sendto(text.encode(), clientAddress)

def correctProtocol(text, protocol):
    return text.split(" ")[0] == protocol

def connectProtocol(conn):
    data = receiveData(conn)
    if correctProtocol(data, "com-0") and isIP(data):
        sendMessage(("com-0 accept " + get_ip()), conn)
        data = receiveData(conn)
        if correctProtocol(data, "com-0"):
            return True
        else:
            return False
    else:
        return

def isIP(text):
    str = text.split(" ")[1]
    return len(str.split(".")) == 4

def receiveData(conn):
    while True:
        global clientAddress
        data, clientAddress = conn.recvfrom(4096)
        if debug:
            print("raw: " + data.decode()) #debug line
        return data.decode()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('255.255.255.255', 1))
        IP = s.getsockname()[0]
    finally:
        s.close()
    return IP

def readMessage(text):
    return text.split("=")[1]

def sendServerMessage(conn):
    global seqnr
    increaseSeqnr()
    sendMessage(("res-" + str(seqnr) + "=I am server"), conn)

def increaseSeqnr():
    global seqnr
    seqnr = seqnr + 1

def extractSeqnr(text):
    return (text.split("=")[0]).split("-")[1]

def correctSeqnr(text):
    global seqnr
    if seqnr - int(extractSeqnr(text)) == 0:
        return True
    else:
        return False

#The code starts here
debug = False

if len(sys.argv) == 2:
    if sys.argv[1] == "-help":
        print("Use -debug to see raw incoming messages")
        exit()
    if sys.argv[1] == "-debug":
        debug = True

clientAddress = ()
serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serv.bind(('0.0.0.0', 5000))
seqnr = 0

while True:
    if connectProtocol(serv):
        while 1:
            data = receiveData(serv)
            if correctSeqnr(data):
                print(readMessage(data))
                sendServerMessage(serv)
                increaseSeqnr()
        conn.close()
        print('Client disconnected')
    else:
        conn.close()
        print("Not correct protocol. Closing connection.")
        break
