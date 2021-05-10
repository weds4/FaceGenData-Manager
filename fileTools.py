from pathlib import Path

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