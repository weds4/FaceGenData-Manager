from pathlib import Path
import wx #not included in normal python install

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