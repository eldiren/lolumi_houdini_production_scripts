
# Usually placed in a Python Sop this code will look through the prims
# and generate parameters for each unique set, allowing you to change
# the names of assets, it also create useful subset groups which
# can be used in Solaris via SOpImport for shading

node = hou.pwd()
geo = node.geometry()


bodyGrp = geo.createPrimGroup('body')
eyemoistureGrp = geo.createPrimGroup('eyeMoisture')
eyesGrp = geo.createPrimGroup('eyes')


pname = ''
for prim in geo.prims():
    path = prim.attribValue('name')
    path = path.split('.Shape')[0]
    matname = prim.attribValue('fbx_material_name')

    if matname in ('Face','Lips','Torso','Legs', 'Toenails', 'Fingernails', 'Arms', 'Mouth', 'Teeth', 'Ears', 'EyeSocket'):
        bodyGrp.add(prim)

    if matname in ('Pupils', 'Sclera', 'Irises'):
        eyesGrp.add(prim)
        
    if matname in ('EyeMoisture', 'Cornea'):
        eyemoistureGrp.add(prim)

    # create parms for changing main object names
    if pname != path:
        parm = node.parm(path+'name')
        if not parm:
            hou_parm_template = hou.StringParmTemplate(path+'name', path+' New Name', 1, default_value=([path]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
            node.addSpareParmTuple(hou_parm_template)
            pname = path
            
        prim.setAttribValue('name', parm.eval())