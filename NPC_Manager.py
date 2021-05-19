# -*- coding: utf-8 -*-
# starting refactor 5/7/2021
try:
    from os import system
    import sys
    from pathlib import PurePath
    import extensions.logger as logger
    import extensions.ExtensionFuncs as exf
except ModuleNotFoundError as e:
    input(e)

def main():
    try:
        # initialization steps
        system("")# summmon system to get colored text!
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

        npc = exf.getNPC(sys.argv)
        modfile = exf.getModFile(sys.argv)
        modspath = configInfo["MO2Location"] + "\\mods\\"
        profileData = exf.getModlist(profilePath, modspath)# a list of pathlib Paths to all active mods
        logger.updateLog(["esp is "+modfile, "npc is "+npc, "mods path is "+modspath], "active mods count is "+str(len(profileData)))

        # main script
        if modfile not in configInfo[currentSession]:# if config doesnt have an entry for this mod yet
            modDirs = exf.locateModDir(modfile, profileData)# time consumer: should be a lot faster now
            logger.updateLog(["modDir is "+modDirs[0].name])
            if exf.verifyModFilesLocation(profileData, npc, modDirs[0]):# check if the mo2\mods folder which has the modfile has the nif/dds files for the current npc
                configInfo[currentSession][modfile] = [modDirs[0].name] #must be in list to handle bijin scenario
                exf.saveConfigInfo(configInfo)
                exf.hideFiles(modDirs[0].name, npc, profileData)
            else:# it doesn't have the nif/dds files
                modDir = exf.requestModFolder(modspath, npc, profilePath)
                configInfo[currentSession][modfile] = [modDir]
                exf.saveConfigInfo(configInfo)
                exf.hideFiles(modDir, npc, profileData)
        else:# config does have an entry for this mod
            modDir = exf.determineKeep(configInfo[currentSession][modfile], modspath, npc)
            if modDir and exf.verifyModFilesLocation(profileData, npc, modDir):
                logger.updateLog(["modDir is "+modDir])
                exf.hideFiles(modDir, npc, profileData)
            else:# it doesn't have the nif/dds files
                modDir = exf.requestModFolder(modspath, npc, profilePath)
                configInfo[currentSession][modfile].append(modDir)
                exf.saveConfigInfo(configInfo)
                logger.updateLog(["modDir is "+modDir])
                exf.hideFiles(modDir, npc, profileData)
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