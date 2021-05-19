# -*- coding: utf-8 -*-
try:
    from pathlib import Path
    import wx# not included in normal python install
    from json import load
    from json import dump
    import extensions.logger as logger
    from os import rename
except ModuleNotFoundError as e:
    input(e)

class MO2Error(Exception):
    '''MO2 profile not specified'''

class nifDdsError(Exception):
    '''called for nif or dds files not being found'''

def dataPath(datatype):
    if datatype == 'nif':
        return "Meshes\\Actors\\Character\\FaceGenData\\FaceGeom"
    elif datatype == 'dds':
        return "textures\\Actors\\Character\\FaceGenData\\FaceTint"

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
    '''create the wx prompt to get the profile path'''
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
    '''inspect sysArgv for the npc formID'''
    return '00'+str(sysArgs[-1])[8:-1]

def getModFile(sysArgs):
    '''inspect sysArgv for the mod name'''
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
            modfile=modfile[j+2:]# +2 becase j is ']' and j+1 is '  '
            break
    return modfile

def getModlist(profilePath, modsPath):
    '''this returns an ordered list (of windows Paths) for every active mod in the selected profile, highest in mod order first'''
    with open(profilePath+"\\modlist.txt") as modlisttxt:
        temp = modlisttxt.readlines()
    return [Path(modsPath+line[1:-1]) for line in temp if line[0] == "+"]

def locateModDir(ESfile, modlist):# ESFile == esp, esl, esm
    '''this returns a list (of strings) of all "MO2\\mods" directories that have the ESfile in them'''
    return [path.parent for mod in modlist for path in mod.rglob(ESfile)]

def verifyModFilesLocation(modlist, npc, keep):
    '''returns True or None if a nif and dds are found. Not Fool-Proof'''
    check = [path for path in keep.rglob(npc+'.???')]# expects keep is Path!
    if check:
        length = len(check)
        if length == 2:# good
            if check[0].parents[1].name.lower() == 'facegeom' and check[1].parents[1].name.lower() == 'facetint':# better!
                if check[0].name.upper() == f"{npc}.NIF" and check[1].name.upper() == f"{npc}.DDS":# best
                    return True
                else: pass
            else:
                pass
        elif length == 1:
            pass
        else:
            pass

    if check and check[0] == f"{npc}.NIF" and check[1] == f"{npc}.DDS":
        return True

def listActiveMods(modlist):# possibly unused
    '''this returns a list of just the folder name for all the full Paths in modlist'''
    return [path.name for path in modlist]

def locateDataFiles(modlist, npc, keep):# DataFiles == nif, dds
    '''this returns full Paths to each file that deserves to be hidden'''
    return [pathsList for pathsList in
            [[path for path in mod.rglob(npc+'.???')]
             for mod in modlist if mod.name != keep] if pathsList]# expects keep is string

def hideFiles(modlist, npc, keep):
    '''this does the actual hiding of files using os.rename'''
    dataFiles = locateDataFiles(modlist, npc, keep)# expects keep is string
    messages = []
    error = False
    if dataFiles:
        messages.append("Data files were found")
        for modFiles in dataFiles:
            length = len(modFiles)
            modname = modFiles[0].parents[6].name
            if length == 2:# good
                if modFiles[0].suffix.lower() == '.nif' and modFiles[1].suffix.lower() == '.dds':
                    for file in modFiles:
                        fileString = str(file)
                        rename(fileString, fileString+".mohidden")
                    messages.append(f"successfully hid nif and dds for {npc} from \"{modname}\"")

                else:
                    error = True
                    messages.append(f"something is wrong with the file structure in \"{modname}\"")
                    messages.append(f"Error: 2 files found for {npc}, but they failed to be nif and dds")
            elif length == 1:
                error = True
                foundFileType = modFiles[0].suffix.lower()
                if foundFileType == '.nif':
                    messages.append(f"\"{modname}\" has only a nif file for {npc}")
                elif foundFileType == '.dds':
                    messages.append(f"\"{modname}\" has only a dds file for {npc}")
            else:
                error = True
                messages.append(f"something is wrong with the file structure in \"{modname}\"")
                messages.append(f"Error: there are more than 2 files with name {npc} and a 3 character suffix")
    else:
        error = True
        messages.append(f"Error: No data files for {npc} found in any active mods! (beside the nif+dds in {keep})")
    if len(messages) > 0:
        if error:
            logger.updateLog(messages, True)
            logger.logDebugInfo("noND")
            raise nifDdsError("nifs and/or dds's were not hidden as expected")
        else: logger.updateLog(messages)

def requestModFolder(modlist, npc):
    '''returns path to selected mod folder'''
    modFiles = locateDataFiles(modlist, npc, "")
    paths = list(dict.fromkeys([file.parents[6] for mod in modFiles for n, file in enumerate(mod) if file not in mod[:n]]))
    print('')
    for i, name in enumerate(paths):
        print(str(i+1)+":",name.name)
    selection = int(input("Please enter the number for the mod you are trying to keep: "))
    return paths[selection-1]

def determineKeep(npc, modspath, listOfMods):# listOfMods is a list of string mod folder names
    for mod in [Path(modspath+modFolder) for modFolder in listOfMods]:
        check = [path.name.upper() for path in mod.rglob(npc+'.???')]
        if check and check[0] == f"{npc}.NIF" and check[1] == f"{npc}.DDS":
            print(f'type of mod is {type(mod)}')
            return mod

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
            # ie keep at least ten sessions and all sessions that have occurred in the last 2 days
            item = configKeys[i]
            try:
                time_days = int(float(item)/3600/24/365)
            except ValueError(): continue
            if time_days+2 < currentTime:
                config.pop(item)
                check = True
            i+=1
        if check: saveConfigInfo(config)