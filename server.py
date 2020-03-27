#consider using latest data format from client

import socket, sys
import time
import threading
import os
import conPrint

class config:
    def getConf(conf):
        f = open("server-opt.conf", "r")

        if f.mode == "r":
            contents = f.read().split("\n")
            for x in contents:
                y = x.split(" : ")
                if y[0] == conf:
                    return y[1]

    def readConfig():
        global debug
        global timeoutTolerance
        global maxPackagesPerSecond
        global portNumber

        confDebug = config.getConf("Debug")
        confTimeoutTolerance = int(config.getConf("TimeoutTolerance"))
        confMaxPackagesPerSecond = int(config.getConf("MaxPackagesPerSecond"))
        confPortNumber = int(config.getConf("PortNumber"))

        if confDebug == "True":
            debug = True
        if confTimeoutTolerance != 4:
            timeoutTolerance = confTimeoutTolerance
        if confMaxPackagesPerSecond != 25:
            maxPackagesPerSecond = confMaxPackagesPerSecond
        if confPortNumber != 5000:
            portNumber = confPortNumber

class protocolHandler:
    def connectProtocol(conn):
        data = socketHandler.receiveData(conn)
        if textHandler.correctProtocol(data, "com-0") and textHandler.isIP(data):
            socketHandler.sendMessage(("com-0 accept " + socketHandler.get_ip()), conn)
            data = socketHandler.receiveData(conn)
            if textHandler.correctProtocol(data, "com-0"):
                return True
            else:
                return False
        else:
            return

    def toleranceProtocol(conn):
        socketHandler.sendMessage("con-res 0xFE", conn)

        conPrint.error("no message received in " + str(timeoutTolerance) +  " seconds...")

        while 1:
            data = socketHandler.receiveData(conn)
            if textHandler.isToleranceResponse(data):
                if debug: conPrint.debug("tolerance response approved...")
                break

        conn.close()


class seqNrHandler:
    def increaseSeqnr():
        global seqnr
        seqnr = seqnr + 1

    def extractSeqnr(text):
        try:
            return (text.split("=")[0]).split("-")[1]
        except:
            exit()

    def correctSeqnr(text):
        global seqnr
        if seqnr - int(seqNrHandler.extractSeqnr(text)) == 0:
            return True
        else:
            return False

class textHandler:
    def correctProtocol(text, protocol):
        return text.split(" ")[0] == protocol

    def isIP(text):
        str = text.split(" ")[1]
        return len(str.split(".")) == 4

    def isToleranceResponse(text):
        return text == "con-res 0xFF"

    def isKeepAlive(text):
        return text == "con-h 0x00"

    def readMessage(text):
        return text.split("=")[1]

    def sendServerMessage(conn):
        global seqnr
        seqNrHandler.increaseSeqnr()
        socketHandler.sendMessage(("res-" + str(seqnr) + "=I am server"), conn)

class socketHandler:
    def sendMessage(text, conn):
        if debug: conPrint.debugSend("send: \t\t" + text)
        conn.send((text).encode())

    def receiveData(conn):
        while True:
            data = conn.recv(4096).decode()
            packPerSecHandler.incrementPackagePerSecond()
            if debug: conPrint.debugRecv("received: \t" + data) #debug line
            if toleranceReached == 1:
                exit()
            elif textHandler.isKeepAlive(data):
                toleranceHandler.setMessageReceived(1)
            else:
                return data

    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('255.255.255.255', 1))
            IP = s.getsockname()[0]
        finally:
            s.close()
        return IP

class packPerSecHandler:
    def packPerSecThread(conn):
        while 1:
            if state == 0: break
            time.sleep(1)
            if packagesPerSecondReceived > maxPackagesPerSecond:
                conPrint.error("too many packages received... shutting down...")
                os._exit(0)
            packPerSecHandler.resetPackPerSec()


    def packPerSecProcess(conn):
        thread0 = threading.Thread(target = packPerSecHandler.packPerSecThread, args = (conn,))

        thread0.start()

    def incrementPackagePerSecond():
        global packagesPerSecondReceived
        packagesPerSecondReceived = packagesPerSecondReceived + 1

    def resetPackPerSec():
        global packagesPerSecondReceived
        packagesPerSecondReceived = 0

class toleranceHandler:
    def startToleranceTimer(conn):
        thread1 = threading.Thread(target = serverProcess, args = (conn,))

        thread1.start()

        packPerSecHandler.packPerSecProcess(conn)

        while 1:
            time.sleep(timeoutTolerance)

            if thread1.is_alive():
                if messageReceived == 0:
                    if debug: conPrint.debug("tolerance reached...")

                    toleranceHandler.setToleranceReached(1)

                    protocolHandler.toleranceProtocol(conn)
                else:
                    if debug: conPrint.debug("tolerance not reached...")
                    toleranceHandler.setMessageReceived(0)
            else:
                break

    def setMessageReceived(n):
        global messageReceived
        messageReceived = n

    def setToleranceReached(n):
        global toleranceReached
        toleranceReached = n

def serverProcess(conn):
    if debug: conPrint.debug("starting serverProcess")
    while 1:
        data = socketHandler.receiveData(conn)
        if state == 0: break
        if seqNrHandler.correctSeqnr(data):
            toleranceHandler.setMessageReceived(1)
            print(textHandler.readMessage(data))
            textHandler.sendServerMessage(conn)
            seqNrHandler.increaseSeqnr()
    if debug: conPrint.debug("stopping serverProcess")


#The code starts here
state = 1
debug = False
timeoutTolerance = 4
maxPackagesPerSecond = 25
messageReceived = 0
toleranceReached = 0
portNumber = 5000
seqnr = 0
packagesPerSecondReceived = 0

config.readConfig()

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('0.0.0.0', portNumber))
serv.listen(5)

conn, addr = serv.accept()

if protocolHandler.connectProtocol(conn):
    conPrint.success("Connected to client!")
    toleranceHandler.startToleranceTimer(conn)
else:
    conn.close()
    conPrint.error("Not correct protocol. Closing connection.")

state = 0
print('Client disconnected')
conn.close()
