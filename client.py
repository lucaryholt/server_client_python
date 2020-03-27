#add keepalive time to conf

import socket
import threading
import time
import os

def connectionProtocol(conn):
    sendMessage("com-0 " + get_ip())
    if correctAcceptProtocol(receiveData(conn)):
        sendMessage("com-0 accept")
        return True

def toleranceProtocol(conn):
    if debug: print("server tolerance reached... closing connection...")
    sendMessage("con-res 0xFF")

    print("server timeout... closing...")

    conn.close()
    os._exit(0)

def keepAliveProcess():
    thread = threading.Thread(target = keepAliveThread, args = ())

    thread.start()

def keepAliveThread():
    while 1:
        time.sleep(keepAliveTime)
        sendMessage("con-h 0x00")

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

def isToleranceMessage(text):
    return text == "con-res 0xFE"

def sendMessage(text):
    client.send((text).encode())

def receiveData(socket):
    while True:
        data = client.recv(4096).decode()
        if debug: print("raw: " + data) #debug line
        if isToleranceMessage(data):
            toleranceProtocol(socket)
        return data

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

def clientProcess(conn):
    if debug: print("starting clientProcess...")
    if keepAlive: keepAliveProcess()
    initiateReceive(conn)
    message = input('Message: ')
    while message != 'Q':
        sendChatMessage(message)
        time.sleep(0.1)
        data = latestData
        if correctSeqnr(data):
            print(readMessage(data))
            increaseSeqnr()
        else:
            exit()
        message = input('Message: ')
    if debug: print("stopping clientProcess...")

def getLatestData(conn):
    while 1:
        setLatestData(receiveData(conn))

def initiateReceive(conn):
    thread1 = threading.Thread(target = getLatestData, args = (conn,))
    thread1.start()

def setLatestData(data):
    global latestData
    latestData = data

def getConf(conf):
    f = open("client-opt.conf", "r")

    if f.mode == "r":
        contents = f.read().split("\n")
        for x in contents:
            y = x.split(" : ")
            if y[0] == conf:
                return y[1]

#The code starts here
debug = False
keepAlive = False
keepAliveTime = 3
seqnr = -1
latestData = ""

confDebug = getConf("Debug")
confKeepAlive = getConf("KeepAlive")
confKeepAliveTime = int(getConf("KeepAliveTime"))

if  confDebug == "True":
    debug = True
if  confKeepAlive == "True":
    keepAlive = True
if  confKeepAliveTime != 3:
    keepAliveTime = confKeepAliveTime

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('0.0.0.0', 5000))

if connectionProtocol(client):
    print("The connection is ready!")
    clientProcess(client)

client.close()
exit()
