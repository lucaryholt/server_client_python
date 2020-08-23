import socket, threading, time, os
from datetime import datetime
import conPrint, configReader

class latestDataHandler:
    def getLatestData(conn):
        while 1:
            latestDataHandler.setLatestData(socketHandler.receiveData(conn))

    def setLatestData(data):
        global latestData
        latestData = data

class protocolHandler:
    def connectionProtocol(conn):
        if handshakeSkip:
            socketHandler.sendMessage("com-0 accept")
        else:
            socketHandler.sendMessage("com-0 " + socketHandler.get_ip())
        if textHandler.correctAcceptProtocol(socketHandler.receiveData(conn)):
            socketHandler.sendMessage("com-0 accept")
            return True
        else:
            conPrint.error("server refused connection...")
            os._exit(0)

    def terminationProtocol(conn):
        if debug: conPrint.debug("requesting termination...")
        socketHandler.sendMessage("con-res 0xFE")

        time.sleep(2)

        os._exit(0)

    def recvTerminationProtocol(conn):
        if debug: conPrint.debug("server requested termination...")
        socketHandler.sendMessage("con-res 0xFF")

        print("closing connection...")

        conn.close()
        os._exit(0)

class seqNrHandler:
    def increaseSeqnr():
        global seqnr
        seqnr = seqnr + 1

    def extractSeqnr(text):
        return (text.split("=")[0]).split("-")[1]

    def correctSeqnr(text):
        global seqnr
        if int(seqNrHandler.extractSeqnr(text)) - seqnr == 1:
            return True

class keepAliveHandler:
    def keepAliveThread():
        while 1:
            time.sleep(keepAliveTime)
            socketHandler.sendMessage("con-h 0x00")

    def keepAliveProcess():
        thread = threading.Thread(target = keepAliveHandler.keepAliveThread, args = ())

        thread.start()

class textHandler:
    def readMessage(text):
        return text.split("=")[1]

    def sendChatMessage(text):
        global seqnr
        seqNrHandler.increaseSeqnr()
        socketHandler.sendMessage("msg-" + str(seqnr) + "=" + text)

    def correctAcceptProtocol(text):
        data = text.split(" ")
        return data[0] == "com-0" and data[1] == "accept" and textHandler.isIP(data[2])

    def isIP(text):
        return len(text.split(".")) == 4

    def isTerminationRequest(text):
        return text == "con-res 0xFE"

    def isTerminationResponse(text):
        return text == "con-res 0xFF"

class socketHandler:
    def sendMessage(text):
        if debug: conPrint.debugSend("sent: \t\t" + text)
        client.send((text).encode())

    def receiveData(socket):
        while True:
            data = client.recv(4096).decode()
            print(data)
            if data != "":
                if debug: conPrint.debugRecv("received: \t" + data) #debug line
                if textHandler.isTerminationRequest(data):
                    protocolHandler.recvTerminationProtocol(socket)
                else:
                    return data

    def initiateReceive(conn):
        thread1 = threading.Thread(target = latestDataHandler.getLatestData, args = (conn,))
        thread1.start()

    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('255.255.255.255', 1))
            IP = s.getsockname()[0]
        finally:
            s.close()
        return IP

def clientProcess(conn):
    if debug: conPrint.debug("starting clientProcess...")
    if keepAlive: keepAliveHandler.keepAliveProcess()
    socketHandler.initiateReceive(conn)
    message = input()
    while message != 'Q':
        textHandler.sendChatMessage(message)
        time.sleep(0.1)
        data = latestData
        if seqNrHandler.correctSeqnr(data):
            print(textHandler.readMessage(data))
            seqNrHandler.increaseSeqnr()
        else:
            exit()
        message = input()
    protocolHandler.terminationProtocol(conn)
    if debug: conPrint.debug("stopping clientProcess...")

#Code starts here
fileName = "client-opt.conf"
debug = configReader.readBoolean(fileName, "Debug")
keepAlive = configReader.readBoolean(fileName, "KeepAlive")
keepAliveTime = configReader.readFloat(fileName, "KeepAliveTime")
portNumber = configReader.readInt(fileName, "PortNumber")
ipAddress = configReader.readString(fileName, "IPAddress")
handshakeSkip = configReader.readBoolean(fileName, "HandshakeSkip")

seqnr = 20
latestData = ""

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ipAddress, portNumber))

if protocolHandler.connectionProtocol(client):
    conPrint.success("The connection is ready!")
    clientProcess(client)

client.close()
exit() #probably redundant, as the code exits after this line anyway
