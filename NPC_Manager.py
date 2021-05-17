# -*- coding: utf-8 -*-
#starting refactor 5/7/2021
try:
    from os import system
    import sys
    from pathlib import PurePath
    import extensions.logger as logger
    import extensions.ExtensionFuncs as exf
except Exception as e:
    input(e)

def main():
    try:
        #initialization steps
        system("") #summmon system to get colored text!
        currentSession = exf.getSessionInfo()
        configInfo = exf.loadConfigInfo()
        logger.updateLog(["Starting log for: "+currentSession])
        MO2Location = configInfo.get("MO2Location", "")
        if MO2Location: MO2Location=MO2Location+"\\profiles"

        if exf.isNewSession(currentSession, configInfo):
            profilePath = exf.getProfilePath(MO2Location, configInfo, currentSession)
        else:
            profilePath = configInfo[currentSession].get("profilePath", None)
        if profilePath is None:
            profilePath = exf.getProfilePath(MO2Location, configInfo, currentSession)

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
                    exf.hideFiles(modDirs[0], modspath, npc, profilePath)
                else:# it doesn't have the nif/dds files
                    modDir = exf.requestModFolder(modspath, npc, profilePath)
                    configInfo[currentSession][modfile] = [modDir]
                    exf.saveConfigInfo(configInfo)
                    exf.hideFiles(modDir, modspath, npc, profilePath)
            else:# multiple folders in mo2\mods have this modfile
                modDir = exf.findWinningMod(modDirs, configInfo[currentSession]["profilePath"])
                if exf.verifyModFilesLocation(modspath+modDir, npc):# check if the mo2\mods folder which has the modfile has the nif/dds files for the current npc
                    configInfo[currentSession][modfile] = [modDir]
                    exf.saveConfigInfo(configInfo) # used to have "if modDir:" in front, removed it cause idthink it applies anymore
                    logger.updateLog(["modDir is "+modDir])
                    exf.hideFiles(modDir, modspath, npc, profilePath)
                else:# it doesn't have the nif/dds files
                    modDir = exf.requestModFolder(modspath, npc, profilePath)
                    configInfo[currentSession][modfile] = [modDir]
                    exf.saveConfigInfo(configInfo)
                    exf.hideFiles(modDir, modspath, npc, profilePath)
        else: #config does have an entry for this mod
            modDir = exf.determineKeep(configInfo[currentSession][modfile], modspath, npc)
            if modDir and exf.verifyModFilesLocation(modspath+modDir, npc):
                exf.hideFiles(modDir, modspath, npc, profilePath)
            else: #it doesn't have the nif/dds files
                modDir = exf.requestModFolder(modspath, npc, profilePath)
                configInfo[currentSession][modfile].append(modDir)
                exf.saveConfigInfo(configInfo)
                logger.updateLog(["modDir is "+modDir])
                exf.hideFiles(modDir, modspath, npc, profilePath)
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