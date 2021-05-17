try:
    from pathlib import Path
    import wx #not included in normal python install
    from json import load
    from json import dump
    import extensions.logger as logger
    from os import rename
except ModuleNotFoundError as e:
    input(e)

class MO2Error(LookupError):
    '''MO2 profile not specified'''

class nifDdsError(LookupError):
    '''nif/dds missing'''

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

def getProfilePath(MO2Location, configInfo, currentSession):
    '''get profile path using wx prompt'''
    profilePath = requestProfilePath("Please choose your current MO2 profile's folder", MO2Location)
    if profilePath is None:
        logger.logDebugInfo("NoMO2")
        raise MO2Error("Must choose the folder of the current MO2 profile")
    configInfo[currentSession]["profilePath"] = profilePath
    saveConfigInfo(configInfo)
    return profilePath
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

def getModlist(profilePath, modsPath):
    '''this returns a list (of windows paths) for every active mod in the selected profile'''
    with open(profilePath+"\\modlist.txt") as modlisttxt:
        temp = modlisttxt.readlines()
    return [Path(modsPath+line[1:-1]) for line in temp if line[0] == "+"]

def locateModDir(ESfile, modlist): #ESFile == esp, esl, esm
    '''this returns a list (of strings) of all "MO2\\mods" directories that have the ESfile in them'''
    return [str(path.parent) for mod in modlist for path in mod.rglob(ESfile)]

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
    return check1 and check2

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
    a,nifs = locateDataFiles("", 'nif', modsPath, npc, profilePath)
    for i in range(1, len(nifs)+1):
        modDir = list(nifs[i-1].parts)[-8]
        print(str(i)+":",modDir)
    selection = int(input("Please enter the number for the mod you are trying to keep: "))
    return list(nifs[selection-1].parts)[-8]

def hideFiles(keep, modspath, npc, profilePath):
    a,nifs = locateDataFiles(keep, 'nif', modspath, npc, profilePath)
    b,ddss = locateDataFiles(keep, 'dds', modspath, npc, profilePath)
    messages = []
    error = False
    if a:
        for file in nifs:
            fileString = str(file)
            rename(fileString, fileString+".mohidden")
        messages.append("nif-hide success!")
    else:
        messages.append("Error: did not hide nif")
        error = True
    if b:
        for file in ddss:
            fileString = str(file)
            rename(fileString, fileString+".mohidden")
        messages.append("dds-hide success!")
    else:
        messages.append("Error: did not hide dds")
        error = True

    if len(messages) > 0:
        if error:
            logger.updateLog(messages, True)
            logger.logDebugInfo("noND")
            raise nifDdsError("nifs and/or dds's were not hidden as expected")
        else: logger.updateLog(messages)


def cleanUpOldSessions(sessionID):# if there are more than 10 saved sessions that are two days older than the current session, delete them
    with open("NPC_Manager.json", "r") as configfile:
        config = load(configfile)
    configKeys = list(config)
    keyCount = len(configKeys)
    if keyCount > 10:
        check = False
        currentTime = int(float(sessionID)/3600/24/365)
        i = 0
        while i < keyCount-10:# hopefully this loops over the oldest n configs where n=keycount-10
            #ie keep at least ten sessions and all sessions that have occurred in the last 2 days
            item = configKeys[i]
            try:
                time_days = int(float(item)/3600/24/365)
            except ValueError(): continue
            if time_days+2 < currentTime:
                config.pop(item)
                check = True
            i+=1
        if check: saveConfigInfo(config)