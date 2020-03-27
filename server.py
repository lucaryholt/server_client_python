#Mangler at serveren sender con-res 0xFE og client svarer med con-res 0xFF
#F.eks. lave ny metode der hedder interruptProtocol?

import socket, sys
import multiprocessing
import time
import threading
import os

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

def toleranceProtocol(conn):
    sendMessage("con-res 0xFE", conn)

    while 1:
        data = receiveData(conn)
        if isToleranceResponse(data):
            if debug: print("tolerance response approved...")
            break

    conn.close()

def isIP(text):
    str = text.split(" ")[1]
    return len(str.split(".")) == 4

def isToleranceResponse(text):
    return text == "con-res 0xFF"

def receiveData(conn):
    while True:
        data = conn.recv(4096).decode()
        if debug: print("raw: " + data) #debug line
        if toleranceReached == 1:
            toleranceProtocol(conn)
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

def serverProcess(conn):
    if debug: print("starting serverProcess")
    t = threading.currentThread()
    while 1:
        data = receiveData(conn)
        if correctSeqnr(data):
            setMessageReceived(1)
            print(readMessage(data))
            sendServerMessage(conn)
            increaseSeqnr()
    if debug: print("stopping serverProcess")

def startToleranceTimer(conn):
    thread1 = threading.Thread(target = serverProcess, args = (conn,))

    thread1.start()

    while 1:
        time.sleep(4)

        if thread1.is_alive():
            if messageReceived == 0:
                if debug: print("tolerance reached...")

                setToleranceReached(1)
            else:
                if debug: print("tolerance not reached...")
                setMessageReceived(0)

def setMessageReceived(n):
    global messageReceived
    messageReceived = n

def setToleranceReached(n):
    global toleranceReached
    toleranceReached = n

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
messageReceived = 0
toleranceReached = 0

conn, addr = serv.accept()

try:
    if connectProtocol(conn):
        startToleranceTimer(conn)
    else:
        conn.close()
        print("Not correct protocol. Closing connection.")
except ConnectionResetError:
    print("connection closed... shutting down...")
    os._exit(0)
except BrokenPipeError:
    print("connection failed... shutting down...")
    os._exit(0)


conn.close()
print('Client disconnected')
