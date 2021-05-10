
from json import load
from json import dump
from pathlib import Path

def getSessionInfo():
    session = Path("SSEEdit_log.txt").stat().st_mtime
    return str(session)

def loadConfigInfo():
    with open("NPC_Manager.json", "a+") as configfile:
        configfile.seek(0)
        try: return load(configfile)
        except: return {}

def saveConfigInfo(config):
    with open("NPC_Manager.json", "w") as configfile:
            dump(config, configfile, indent=2)

def isNewSession(currentSessionID, config):
    if not currentSessionID in config:
        config[currentSessionID] = {}
        saveConfigInfo(config)
        return True
    else: return False

def cleanUpOldSessions(sessionID):# if there are saved sessions that are two days older than the current session, delete them
    with open("NPC_Manager.json", "r") as configfile:
        config = load(configfile)
    check = False
    currentTime = int(float(sessionID)/3600/24/365)
    for item in list(config):
        try:
            time_days = int(float(item)/3600/24/365)
        except: continue
        if time_days+2 < currentTime:
            config.pop(item)
            check = True
        if check: saveConfigInfo(config)