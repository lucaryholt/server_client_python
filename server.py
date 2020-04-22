import socket, sys, time, threading, os
from datetime import datetime
import conPrint, configReader

class logPrinter:
    def printToLog(type, text):
        #logFileName = "serverlog.txt"
        file = open(logFileName, "a")
        file.write(logPrinter.getType(type) + logPrinter.getDateAndTime() + ": " + text + "\n")
        file.close()

    def getDateAndTime():
        now = datetime.now()
        dateTimeString = now.strftime("%d/%m/%Y %H:%M:%S")
        return dateTimeString

    def getType(type):
        if type == "info":
            return "INFO: "
        elif type == "error":
            return "ERROR: "

class protocolHandler:
    def connectProtocol(conn):
        data = socketHandler.receiveData(conn)
        if textHandler.correctProtocol(data, "com-0") and textHandler.isIP(data):
            logPrinter.printToLog("info", data)
            socketHandler.sendMessage(("com-0 accept " + socketHandler.get_ip()), conn)
            data = socketHandler.receiveData(conn)
            if textHandler.correctProtocol(data, "com-0"):
                logPrinter.printToLog("info", data)
                return True
            else:
                logPrinter.printToLog("error", (data + " {FAILED SECOND HANDSHAKE}"))
                return False
        else:
            logPrinter.printToLog("error", (data + " {FAILED FIRST HANDSHAKE}"))
            return

    def terminationProtocol(conn):
        if debug: conPrint.debug("requesting termination...")
        socketHandler.sendMessage("con-res 0xFE", conn)

        time.sleep(2)

        setState(0)

    def recvTerminationProtocol(conn):
        if debug: conPrint.debug("client requested termination... closing connection...")
        socketHandler.sendMessage("con-res 0xFF", conn)

        print("closing connection...")

        setState(0)


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

    def isTerminationResponse(text):
        return text == "con-res 0xFF"

    def isTerminationRequest(text):
        return text == "con-res 0xFE"

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
            setLatestData(data)
            packPerSecHandler.incrementPackagePerSecond()
            if textHandler.isTerminationRequest(data):
                protocolHandler.recvTerminationProtocol(conn)
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
            if state == 0:
                exit()
            time.sleep(1)

            if packagesPerSecondReceived > maxPackagesPerSecond:
                conPrint.error("too many packages received... shutting down...")
                protocolHandler.terminationProtocol(conn)
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

                    conPrint.error("no message received in " + str(timeoutTolerance) +  " seconds...")

                    toleranceHandler.setToleranceReached(1)

                    protocolHandler.terminationProtocol(conn)
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

def setLatestData(data):
    global latestData
    latestData = data

def setState(n):
    global state
    state = n

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
fileName = "server-opt.conf"
logFileName = configReader.readString(fileName, "LogFileName")
debug = configReader.readBoolean(fileName, "Debug")
timeoutTolerance = configReader.readInt(fileName, "TimeoutTolerance")
maxPackagesPerSecond = configReader.readInt(fileName, "MaxPackagesPerSecond")
portNumber = configReader.readInt(fileName, "PortNumber")

state = 1
messageReceived = 0
toleranceReached = 0
seqnr = 0
packagesPerSecondReceived = 0
latestData = ""

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

print('Client disconnected')
conn.close()
