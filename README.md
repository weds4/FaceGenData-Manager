# NPC-FaceGenData-Manager
NPC conflict manager uses xEdit and Python.

Basically when you load multiple NPC mods you have plenty of conflicts, both in the esps and in loose files.
In order to patch these NPCs manually, you must choose the NPC record from the mod you want and then hide the loose files for that npc from the other mods that add it (simplified explanation)

This tool lets you apply an SSEEdit script to the NPC record you want to keep and it will add that record to a patch file called NPC_Manager (esl flagged) and then search your MO2 mods for any files that apply to that NPC which are not from the mod you are keeping and hide them. So, in xEdit, right-click on the NPC you want to apply the script to **in the esp of the mod that you want to "win" the conflict**.
The xEdit script requires MXPF.

Installation: Extract the contents of the release zip to your SSEEdit folder (where the executable is)

How to use: run SSEEdit with your full mod list (but before smashed/bashed patches). If you know the NPCs you want to patch already, find the NPC record from the mod whose appearance you want to use and run the _NPC_Manager script on that record. It will copy the NPC to a new mod file\* (NPC_Manager.esp) and then run a program to rename the FaceGen files for that NPC to *oldname*.mohidden (so that they appear hidden in MO2). By doing this you will have the correct record changes in NPC_Manager.esp and no conflicting files\*\* which might cause the black face bug.


\*if the NPC uses a template record (ABCS -> Template Flags -> Use Traits), then the NPC record will be copied, but the hiding program will not run. This is because the FaceGen files for that NPC rely on the FaceGen data of a different NPC (the template) so there will not be any files to hide

\*\*this program only hides loose files, so FaceGen data that is packed into .bsa's can still cause problems, depending on load order.


Made with python 3.8.9 using libraries: sys, os, wx, json and pathlib
