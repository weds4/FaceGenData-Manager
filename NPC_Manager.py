# -*- coding: utf-8 -*-
#starting refactor 5/7/2021
try:
    from os import rename
    from os import system
    import sys
    from pathlib import PurePath
    import extensions.logger as logger
    import extensions.ExtensionFuncs as exf
except Exception as e:
    input(e)

class nifDdsError(LookupError):
    '''nif/dds missing'''

class MO2Error(LookupError):
    '''MO2 profile not specified'''

def hideFiles(keep, modspath, npc, profilePath):
    a,nifs = exf.locateDataFiles(keep, 'nif', modspath, npc, profilePath)
    b,ddss = exf.locateDataFiles(keep, 'dds', modspath, npc, profilePath)
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
        currentSession = exf.getSessionInfo()
        configInfo = exf.loadConfigInfo()
        logger.updateLog(["Starting log for: "+currentSession])
        MO2Location = configInfo.get("MO2Location", "")
        if MO2Location: MO2Location=MO2Location+"\\profiles"
        if exf.isNewSession(currentSession, configInfo):
            profilePath = exf.requestProfilePath("Please choose your current MO2 profile's folder", MO2Location)
            if profilePath is None:
                logger.logDebugInfo("NoMO2")
                raise MO2Error("Must choose the folder of the current MO2 profile")
            configInfo[currentSession]["profilePath"] = profilePath
            exf.saveConfigInfo(configInfo)
        else:
            profilePath = configInfo[currentSession].get("profilePath", None)
        if profilePath is None:
            profilePath = exf.requestProfilePath("Please choose your current MO2 profile's folder", MO2Location)
            if profilePath is None:
                logger.logDebugInfo("NoMO2")
                raise MO2Error("Must choose the folder of the current MO2 profile")
            configInfo[currentSession]["profilePath"] = profilePath
            exf.saveConfigInfo(configInfo)
        if MO2Location == "":
            MO2Location = str(PurePath(profilePath).parents[1])
            configInfo["MO2Location"] = MO2Location
            exf.saveConfigInfo(configInfo)
        #
        #main script
        npc = exf.getNPC(sys.argv)
        modfile = exf.getModFile(sys.argv)
        logger.updateLog(["esp is "+modfile, "npc is "+npc])
        modspath = configInfo["MO2Location"] + "\\mods\\"
        if modfile not in configInfo[currentSession]: #if config doesnt have an entry for this mod yet
            modDirs = exf.locateModDir(modfile, modspath)#time consumer
            if len(modDirs) == 1:#only one folder in mo2\mods has this modfile
                logger.updateLog(["modDir is "+modDirs[0]])
                if exf.verifyModFilesLocation(modspath+modDirs[0], npc):# check if the mo2\mods folder which has the modfile has the nif/dds files for the current npc
                    configInfo[currentSession][modfile] = [modDirs[0]]
                    exf.saveConfigInfo(configInfo)
                    hideFiles(modDirs[0], modspath, npc, profilePath)
                else:# it doesn't have the nif/dds files
                    modDir = exf.requestModFolder(modspath, npc, profilePath)
                    configInfo[currentSession][modfile] = [modDir]
                    exf.saveConfigInfo(configInfo)
                    hideFiles(modDir, modspath, npc, profilePath)
            else:# multiple folders in mo2\mods have this modfile
                modDir = exf.findWinningMod(modDirs, configInfo[currentSession]["profilePath"])
                if exf.verifyModFilesLocation(modspath+modDir, npc):# check if the mo2\mods folder which has the modfile has the nif/dds files for the current npc
                    configInfo[currentSession][modfile] = [modDir]
                    exf.saveConfigInfo(configInfo) # used to have "if modDir:" in front, removed it cause idthink it applies anymore
                    logger.updateLog(["modDir is "+modDir])
                    hideFiles(modDir, modspath, npc, profilePath)
                else:# it doesn't have the nif/dds files
                    modDir = exf.requestModFolder(modspath, npc, profilePath)
                    configInfo[currentSession][modfile] = [modDir]
                    exf.saveConfigInfo(configInfo)
                    hideFiles(modDir, modspath, npc, profilePath)
        else: #config does have an entry for this mod
            modDir = exf.determineKeep(configInfo[currentSession][modfile], modspath, npc)
            if modDir and exf.verifyModFilesLocation(modspath+modDir, npc):
                hideFiles(modDir, modspath, npc, profilePath)
            else: #it doesn't have the nif/dds files
                modDir = exf.requestModFolder(modspath, npc, profilePath)
                configInfo[currentSession][modfile].append(modDir)
                exf.saveConfigInfo(configInfo)
                logger.updateLog(["modDir is "+modDir])
                hideFiles(modDir, modspath, npc, profilePath)
        #
        exf.cleanUpOldSessions(currentSession)
        logger.updateLog(["Ending log for: "+currentSession])
    #
    except Exception as e:
        exception = sys.exc_info()[0]
        logger.updateLog([f"Error: {exception}, {e}"], True)
        try:
            currentSession = exf.getSessionInfo()
            logger.updateLog(["Ending log for: "+currentSession])
        except FileNotFoundError():
            logger.updateLog(["Ending log for: [ERR] Unknown Session"])
        input("Press Enter to quit")
#
if __name__ == '__main__':
    main()
    input('end of __main__')