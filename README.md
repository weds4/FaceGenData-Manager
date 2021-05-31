# NPC-FaceData-Manager
NPC conflict manager uses xEdit and Python.

Basically when you load multiple NPC mods you have plenty of conflicts, both in the esps and in loose files.
In order to patch these NPCs manually, you must choose the NPC record from the mod you want and then hide the loose files for that npc from the other mods that add it (simplified explaination)

This tool lets you apply an SSEEdit script to the NPC record you want to keep and it will add that record to a patch file called NPC_Manager (esl flagged) and then search your MO2 mods for any files that apply to that NPC which are not from the mod you are keeping. So, in xEdit, right-click on the NPC you want to apply the script to **in the esp of the mod that you want to "win" the conflict**.
The xEdit script requires MXPF.

Installation: Extract the contents of the release zip to your SSEEdit folder (where the executable is)

Made with python 3.8.9 using libraries: sys, os, wx, json and pathlib
