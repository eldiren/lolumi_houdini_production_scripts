# sister script for xform_json_for_solaris, this script will take
# a json exported for the previous script and with a selected
# stagemanger will populate it with transforms and prim paths
# this effectively recreates the C4D scene

import json

fName = hou.ui.selectFile(title="Select scene export json...", pattern='*.json')
usdDir = hou.ui.selectFile(title="Select usd asset directory...", file_type=hou.fileType.Directory)
stagePath = hou.ui.readInput('Optional stage path to place assets')

fName = hou.expandString(fName)

node = hou.selectedNodes()[0]
data = {}

if node:
    if node.type().name() == 'stagemanager':
        amt = node.parm('num_changes').eval()
        
        with open(fName, 'r') as f:
            data = json.load(f)
            
            node.parm('num_changes').set(amt+len(data))
            
            i = amt + 1
            for k,v in data.items():
                node.parm('primpath' + str(i)).set(k)
                node.parm('setxform' + str(i)).set(1)
                node.parm('reffilepath' + str(i)).set(stagePath[1] + usdDir + k + ".usdc")

                node.parmTuple('t' + str(i))[0].set(v['translate'][0])
                node.parmTuple('t' + str(i))[1].set(v['translate'][1])
                node.parmTuple('t' + str(i))[2].set(v['translate'][2])

                node.parmTuple('r' + str(i))[0].set(v['rotation'][0])
                node.parmTuple('r' + str(i))[1].set(v['rotation'][1])
                node.parmTuple('r' + str(i))[2].set(v['rotation'][2])

                i += 1
                