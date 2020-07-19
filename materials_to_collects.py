# used in a shelf tool this allows you to take imported materials
# and attach them automatically to a collect network, mainly built
# as a first step for Hydra based networks

mnodes = hou.selectedNodes()
pnode = mnodes[0].parent()

for mat in mnodes:
    mat.setMaterialFlag(False)
    mname = mat.name()
    mat.setName('arnold_materialbuilder',unique_name=True)
    cnode = pnode.createNode('collect', mname)
    cnode.setFirstInput(mat)
    
pnode.layoutChildren()