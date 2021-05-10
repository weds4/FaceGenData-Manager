# -*- coding: utf-8 -*-
#starting refactor 5/7/2021
try:
    import wx #not included in normal python install
    from os import rename
    from os import system
    import sys
    from pathlib import Path
    from pathlib import PurePath
    import logger
    import configstorage as cs
except Exception as e:
    input(e)


class nifDdsError(LookupError):
    '''nif/dds missing'''

class MO2Error(LookupError):
    '''MO2 profile not specified'''

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

def findWinningMod(potentials, profilePath):#search modlist.txt to find the highest-in-priority mod
    with open(profilePath+'\\modlist.txt') as modlistfile:
        modlist = modlistfile.readlines()
    for mod in modlist:
        if mod[0] == '-':
            continue
        elif mod[1:-1] in potentials:
            return mod[1:-1]

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

def main():
    try:
        system("") #summmon system to get colored text!

        #initialization steps
        currentSession = cs.getSessionInfo()
        configInfo = cs.loadConfigInfo()
        logger.updateLog(["Starting log for: "+currentSession])
        MO2Location = configInfo.get("MO2Location", "")
        if MO2Location: MO2Location=MO2Location+"\\profiles"
        if cs.isNewSession(currentSession, configInfo):
            profilePath = requestProfilePath("Please choose your current MO2 profile's folder", MO2Location)
            if profilePath is None:
                logger.logDebugInfo("NoMO2")
                raise MO2Error("Must choose the folder of the current MO2 profile")
            configInfo[currentSession]["profilePath"] = profilePath
            cs.saveConfigInfo(configInfo)
        else:
            profilePath = configInfo[currentSession].get("profilePath", None)
        if profilePath is None:
            profilePath = requestProfilePath("Please choose your current MO2 profile's folder", MO2Location)
            if profilePath is None:
                logger.logDebugInfo("NoMO2")
                raise MO2Error("Must choose the folder of the current MO2 profile")
            configInfo[currentSession]["profilePath"] = profilePath
            cs.saveConfigInfo(configInfo)
        if MO2Location == "":
            MO2Location = str(PurePath(profilePath).parents[1])
            configInfo["MO2Location"] = MO2Location
            cs.saveConfigInfo(configInfo)
        #
        #main script
        npc = getNPC(sys.argv)
        logger.updateLog(["npc is "+npc])
        modfile = getModFile(sys.argv)
        logger.updateLog(["esp is "+modfile])
        modspath = configInfo["MO2Location"] + "\\mods\\"
        if modfile not in configInfo[currentSession]: #if config doesnt have an entry for this mod yet
            modDirs = locateModDir(modfile, modspath)#time consumer
            if len(modDirs) == 1:#only one folder in mo2\mods has this modfile
                logger.updateLog(["modDir is "+modDirs[0]])
                if verifyModFilesLocation(modspath+modDirs[0], npc):# check if the mo2\mods folder which has the modfile has the nif/dds files for the current npc
                    configInfo[currentSession][modfile] = [modDirs[0]]
                    cs.saveConfigInfo(configInfo)
                    hideFiles(modDirs[0], modspath, npc, profilePath)
                else:# it doesn't have the nif/dds files
                    modDir = requestModFolder(modspath, npc, profilePath)
                    configInfo[currentSession][modfile] = [modDir]
                    cs.saveConfigInfo(configInfo)
                    hideFiles(modDir, modspath, npc, profilePath)
            else:#multiple folders in mo2\mods have this modfile
                modDir = findWinningMod(modDirs, configInfo[currentSession]["profilePath"])
                if verifyModFilesLocation(modspath+modDir, npc):# check if the mo2\mods folder which has the modfile has the nif/dds files for the current npc
                    configInfo[currentSession][modfile] = [modDir]
                    cs.saveConfigInfo(configInfo) # used to have "if modDir:" in front, removed it cause idthink it applies anymore
                    logger.updateLog(["modDir is "+modDir])
                    hideFiles(modDir, modspath, npc, profilePath)
                else:# it doesn't have the nif/dds files
                    modDir = requestModFolder(modspath, npc, profilePath)
                    configInfo[currentSession][modfile] = [modDir]
                    cs.saveConfigInfo(configInfo)
                    hideFiles(modDir, modspath, npc, profilePath)
        else: #config does have an entry for this mod
            modDir = determineKeep(configInfo[currentSession][modfile], modspath, npc)
            if modDir and verifyModFilesLocation(modspath+modDir, npc):
                hideFiles(modDir, modspath, npc, profilePath)
            else: #it doesn't have the nif/dds files
                modDir = requestModFolder(modspath, npc, profilePath)
                configInfo[currentSession][modfile].append(modDir)
                cs.saveConfigInfo(configInfo)
                logger.updateLog(["modDir is "+modDir])
                hideFiles(modDir, modspath, npc, profilePath)
        #
        cs.cleanUpOldSessions(currentSession)
        logger.updateLog(["Ending log for: "+currentSession])
    #
    except Exception as e:
        exception = sys.exc_info()[0]
        logger.updateLog([f"Error: {exception}, {e}"], True)
        try:
            currentSession = cs.getSessionInfo()
            logger.updateLog(["Ending log for: "+currentSession])
        except FileNotFoundError():
            logger.updateLog(["Ending log for: [ERR] Unknown Session"])
        input("Press Enter to quit")
#
if __name__ == '__main__':
    main()
    input('end of __main__')