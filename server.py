#Look into using socket.recvfrom(4096), as that also provides the senders ip
#Then you can send back to that ip. Can then possibly use SOCK_DGRAM instead
#Also opens up for multiple senders.
#Maybe the same in client?
#p. 191 in book

import socket, sys

def sendMessage(text, conn):
    conn.send((text).encode())

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
        data = conn.recv(4096).decode()
        if debug:
            print("raw: " + data) #debug line
        return data

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

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('0.0.0.0', 5000))
serv.listen(5)
seqnr = 0

while True:
    conn, addr = serv.accept()

    if connectProtocol(conn):
        while 1:
            data = receiveData(conn)
            if correctSeqnr(data):
                print(readMessage(data))
                sendServerMessage(conn)
                increaseSeqnr()
        conn.close()
        print('Client disconnected')
    else:
        conn.close()
        print("Not correct protocol. Closing connection.")
        break
