from pathlib import Path
import wx #not included in normal python install
from json import load
from json import dump

def getSessionInfo():
    session = Path("SSEEdit_log.txt").stat().st_mtime
    return str(session)

def loadConfigInfo():
    with open("NPC_Manager.json", "a+") as configfile:
        configfile.seek(0)
        try:
            return load(configfile)
        except FileNotFoundError():
            return {}

def saveConfigInfo(config):
    with open("NPC_Manager.json", "w") as configfile:
        dump(config, configfile, indent=2)

def isNewSession(currentSessionID, config):
    if currentSessionID not in config:
        config[currentSessionID] = {}
        saveConfigInfo(config)
        return True
    else: return False

def requestProfilePath(title, likelyPath):
    app = wx.App(None)
    style = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
    dialog = wx.DirDialog(None, title, likelyPath, style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    del app # only here to stop the "variable unused warning"
    return path

def getNPC(sysArgs):
    return '00'+str(sysArgs[-1])[8:-1]

def getModFile(sysArgs):
    modfile = ''
    for i in range(2, len(sysArgs)):
        if sysArgs[i][0] == '\\':
            break
        elif i==2:
            modfile = modfile + sysArgs[i]
        else:
            modfile = modfile +' '+ sysArgs[i]
    for j in range(0, len(modfile)):
        if modfile[j]==']':
            modfile=modfile[j+2:] #+2 becase j is ']' and j+1 is '  '
            break
    return modfile

def locateModDir(ESfile, modsPath): #ESFile == esp, esl, esm
    directories = []
    for path in Path(modsPath).rglob('*.'+ESfile[-3:]):
        if ESfile in str(path):
            directories.append(str(path))
    #directories is all full paths, next loop turns each full path into just one folder
    for i in range(0, len(directories)):
        returnVal = directories[i][:-(len(ESfile)+1)]
        for j in range(len(returnVal)-1, 0, -1):
            if returnVal[j]=='\\':
                returnVal = returnVal[j+1:]
                break
        directories[i] = returnVal
    return directories

def verifyModFilesLocation(modPath, npc): #modPath is full path to mod folder
    fullPath = Path(modPath+"\\Meshes\\Actors\\Character\\FaceGenData\\FaceGeom")
    check1 = False
    check2 = True
    if fullPath.exists():
        for path in fullPath.rglob('*.nif'):
            basename = str(path)[-12:-4]
            if basename.upper() == npc:
                check1 = True
                break
    else: check1 = False
    fullPath = Path(modPath+"\\textures\\actors\\character\\facegendata\\facetint")
    if fullPath.exists():
        for path in fullPath.rglob('*.dds'):
            basename = str(path)[-12:-4]
            if basename.upper() == npc:
                check2 = True
                break
    else: check2 = False
    if check1 and check2:
        return True
    else:
        return False

def findWinningMod(potentials, profilePath):#search modlist.txt to find the highest-in-priority mod
    with open(profilePath+'\\modlist.txt') as modlistfile:
        modlist = modlistfile.readlines()
    for mod in modlist:
        if mod[0] == '-':
            continue
        elif mod[1:-1] in potentials:
            return mod[1:-1]

def determineKeep(listOfMods, modsPath, npc):
    value = False
    for mod in listOfMods:
        if verifyModFilesLocation(modsPath+mod, npc):
            value = mod
    return value

def listActiveMods(profilePath):
    with open(profilePath+'\\modlist.txt') as modlistfile:
        modlist = modlistfile.readlines()
    activeMods = []
    for mod in modlist:
        if mod[0] == '+':
            activeMods.append(mod[1:-1])
    return activeMods

def locateDataFiles(keep, fileType, modsPath, npc, profilePath): #DataFiles == nif, dds
    paths = []
    modslist = listActiveMods(profilePath) #used to be os.listdir "listdir(modsPath)"
    for mod in modslist:
        if mod == keep:
            continue
        if fileType == 'nif':
            fullpath = modsPath+mod+"\\Meshes\\Actors\\Character\\FaceGenData\\FaceGeom"
        else:
            fullpath = modsPath+mod+"\\textures\\actors\\character\\facegendata\\facetint"
        for path in Path(fullpath).rglob('*.'+fileType):
            basename = str(path)[-12:-4]
            if basename.upper() == npc:
                paths.append(path)
    return len(paths), paths

def requestModFolder(modsPath, npc, profilePath):
    a,nifs = locateDataFiles("nowayamodisnamedthis", 'nif', modsPath, npc, profilePath)
    for i in range(1, len(nifs)+1):
        modDir = list(nifs[i-1].parts)[-8]
        print(str(i)+":",modDir)
    selection = int(input("Please enter the number for the mod you are trying to keep: "))
    return list(nifs[selection-1].parts)[-8]

def cleanUpOldSessions(sessionID):# if there are more than 10 saved sessions that are two days older than the current session, delete them
    with open("NPC_Manager.json", "r") as configfile:
        config = load(configfile)
    configKeys = list(config)
    keyCount = len(configKeys)
    if keyCount > 10:
        check = False
        currentTime = int(float(sessionID)/3600/24/365)
        for i in range(0, keyCount-10):# hopefully this loops over the oldest n configs where n=keycount-10
            #ie keep at least ten sessions and all sessions that have occurred in the last 2 days
            item = configKeys[i]
            try:
                time_days = int(float(item)/3600/24/365)
            except ValueError(): continue
            if time_days+2 < currentTime:
                config.pop(item)
                check = True
        if check: saveConfigInfo(config)