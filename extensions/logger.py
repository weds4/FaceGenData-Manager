# -*- coding: utf-8 -*-
from time import localtime
from time import strftime
CRED = '\033[93m'
CEND = '\033[0m'
errorLog = {
    "noND":
        """The message \"nif/dds not found\" means that the program did not find\
 any nif or dds files to hide.\nThere are several reasons this can happen:
  1. The files are already hidden. You may have already covered this NPC \
previously.
  2. The no other loaded mods have nifs/dds's for that NPC.
  3. The NPC is missing the nif/dds from the mods you are trying to overwrite""",

    "NoMO2":
        "You did not choose a valid folder for your current MO2 profile"
    }

def logDebugInfo(errorCode):
    with open("NPC_Manager.log", "a+") as logfile:
        logfile.write(errorLog[errorCode]+'\n')

def addLineStart(line):
    ts = localtime()
    line = strftime("%x %X", ts) +' '+line
    if line[-1] != '\n':
        return line+'\n'
    else: return line

def updateLog(log, error=False): #log must be array
    for m in log:
        if error: print(CRED+m+CEND)
        else: print(m)
    log = list(map(addLineStart, log))
    with open("NPC_Manager.log", "a+") as logfile:
        logfile.writelines(log)

def cleanUpLog(sessionID):
    currentTime = int(float(sessionID)/3600/24/365)
    with open("NPC_Manager.log", "a+") as logfile:
        logfile.seek(0)
        log = logfile.readlines()
    log.reverse()
    for item in log:
        if "Ending log" in item and "[ERR] Unknown Session" not in item:
            index = 0
            for i in range(len(item)-2, 2, -1):
                try: float(item[i-2:i])
                except ValueError():
                    index = i-1
                    break
            time = float(item[index:])
            if int(time/3600/24/365) + 10 < currentTime:
                log.reverse()
                log = log[log.index(item)+1:]
                with open("NPC_Manager.log", "w+") as logfile:
                    logfile.writelines(log)
                break