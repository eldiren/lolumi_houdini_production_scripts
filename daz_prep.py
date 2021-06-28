
# Placed in a null with exec bound buttons, gen will add the appropriate
# daz groups to the incoming geo for shading and set renaming parms for
# the main objects, clear will clear everything gen created out

def gen():
    pnode = hou.node(hou.pwd().path()+'/..')
    node = hou.node(hou.pwd().path()+'/../subnet1')

    input1 = hou.item(node.path()+'/1')
    out1 = hou.node(node.path()+'/output0')

    bodyGrp = node.createNode('groupcreate', 'body')
    bodyGrp.parm('basegroup').set(
        '@fbx_material_name=Face,Lips,Torso,Legs,Toenails,Fingernails,Arms,Mouth,Teeth,Ears,EyeSocket')
    bodyGrp.setFirstInput(input1)

    eyemoistureGrp = node.createNode('groupcreate', 'eyeMoisture')
    eyemoistureGrp.parm('basegroup').set(
        '@fbx_material_name=EyeMoisture,Cornea')
    eyemoistureGrp.setFirstInput(bodyGrp)

    eyesGrp = node.createNode('groupcreate', 'eyes')
    eyesGrp.parm('basegroup').set('@fbx_material_name=Pupils,Sclera,Irises')
    eyesGrp.setFirstInput(eyemoistureGrp)

    # pack geo to loop through names faster
    pack = node.createNode('pack')
    pack.parm('createpath').set(0)
    pack.parm('packbyname').set(1)
    pack.parm('nameattribute').set('name')
    pack.parm('transfer_attributes').set('name')
    pack.setFirstInput(input1)
    geo = pack.geometry()

    attribedit = node.createNode('attribstringedit')
    attribedit.parm('primattriblist').set('name')
    attribedit.parm('filters').set(len(geo.prims()))
    attribedit.setFirstInput(eyesGrp)

    bodyname = node.createNode('name')
    bodyname.setFirstInput(attribedit)
    bodyname.parm('numnames').set(2)
    bodyname.parm('group1').set('eyeMoisture')
    bodyname.parm('name1').set('eyeMoisture')
    bodyname.parm('group2').set('eyes')
    bodyname.parm('name2').set('eyes')

    grpdel = node.createNode('groupdelete')
    grpdel.parm('group1').set('*')
    grpdel.setFirstInput(bodyname)

    switch = node.createNode('switch')
    switch.parm('input').setExpression('ch("../../split_body")')
    switch.setFirstInput(attribedit)
    switch.setNextInput(grpdel)

    out1.setFirstInput(switch)

    i = 0
    for prim in geo.prims():
        path = prim.attribValue('name')
        attribedit.parm('from'+str(i)).set(path)

        path = path.split('.Shape')[0]
        path = path.replace(' ', '_')
        parmName = 'daz_' + path + 'name'
        attribedit.parm('to'+str(i)).set('\`chs("../../' + parmName + '")\`')

        # create parms for changing main object names
        hou_parm_template = hou.StringParmTemplate(parmName, path+' New Name', 1, default_value=([path]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(
            []), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
        pnode.addSpareParmTuple(hou_parm_template)

        i += 1

    pack.destroy()
    node.layoutChildren()


def clear():
    node = hou.node('..')
    geo = node.geometry()

    ptg = node.parmTemplateGroup()

    subnet = hou.node(hou.pwd().path()+'/../subnet1')

    input1 = hou.item(subnet.path()+'/1')
    out1 = hou.node(subnet.path()+'/output0')

    bodyGrp = hou.node(hou.pwd().path()+'/../subnet1/body')
    if(bodyGrp):
        bodyGrp.destroy()

    eyemoistureGrp = hou.node(hou.pwd().path()+'/../subnet1/eyeMoisture')
    if(eyemoistureGrp):
        eyemoistureGrp.destroy()

    eyesGrp = hou.node(hou.pwd().path()+'/../subnet1/eyes')
    if(eyesGrp):
        eyesGrp.destroy()

    attribedit = hou.node(hou.pwd().path()+'/../subnet1/attribstringedit1')
    if(attribedit):
        attribedit.destroy()

    bodyname = hou.node(hou.pwd().path()+'/../subnet1/name1')
    if(bodyname):
        bodyname.destroy()

    grpdel = hou.node(hou.pwd().path()+'/../subnet1/groupdelete1')
    if(grpdel):
        grpdel.destroy()

    switch = hou.node(hou.pwd().path()+'/../subnet1/switch1')
    if(switch):
        switch.destroy()

    # pack geo to loop through names faster
    pack = subnet.createNode('pack')
    pack.parm('createpath').set(0)
    pack.parm('packbyname').set(1)
    pack.parm('nameattribute').set('name')
    pack.parm('transfer_attributes').set('name')
    pack.setFirstInput(input1)
    geo = pack.geometry()

    i = 0
    for prim in geo.prims():
        path = prim.attribValue('name')
        path = path.split('.Shape')[0]
        path = path.replace(' ', '_')

        # create parms for changing main object names
        n = ptg.find(path+'name')
        if n:
            ptg.remove(n)

        i += 1

    pack.destroy()
    node.layoutChildren()

    node.setParmTemplateGroup(ptg)
