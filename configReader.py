def getConf(fileName, conf):
    f = open(fileName, "r")

    if f.mode == "r":
        contents = f.read().split("\n")
        for x in contents:
            y = x.split(" : ")
            if y[0] == conf:
                return y[1]

def readBoolean(fileName, conf):
    value = getConf(fileName, conf)
    if value == "True":
        return True
    elif value == "False":
        return False

def readInt(fileName, conf):
    return int(getConf(fileName, conf))

def readFloat(fileName, conf):
    return float(getConf(fileName, conf))

def readString(fileName, conf):
    return getConf(fileName, conf)
