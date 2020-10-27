# Place this as a python script in a shelf tool and if your in a LOP context
# this will set up a basic asset structure (geom, shade, and asset layers),
# plus a lookdev layer for quick inspection in USDView

def check_type(type): 
    for ntype in hou.vopNodeTypeCategory().nodeTypes().keys(): 
        if type == ntype: 
            return True 
            
    return False 
    
qpath = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor).pwd().path()

cat = str( hou.node(qpath).childTypeCategory() )
category = cat.split(' ')[-1].replace('>', '')

if category == 'Lop':
    con = hou.node(qpath)
    confasset = con.createNode('null', 'configure_asset')
    sopcreate = con.createNode('sopcreate')
    sopcreatenet = hou.node(sopcreate.path() + '/sopnet/create')
    filesop = sopcreatenet.createNode('file')
    acsop = sopcreatenet.createNode('attribcreate::2.0')
    outputsop = sopcreatenet.createNode('output')
    geom = con.createNode('configurelayer', 'configurelayer_geom')
    mlib = con.createNode('materiallibrary')
    shade = con.createNode('configurelayer', 'configurelayer_shade')
    casset = con.createNode('configurelayer', 'configurelayer_asset')
    refasset = con.createNode('reference')
    reflights = con.createNode('reference', 'studio_light_set01')
    lmixer = con.createNode('lightmixer')
    lcoll = con.createNode('collection::2.0')
    lgraft = con.createNode('graft', 'graft_lights')
    usdrop = con.createNode('usd_rop')

    larnrsettings = con.createNode('lo_arnold_render_settings::001')
    camera = con.createNode('camera')
    
    acsop.setFirstInput(filesop)
    outputsop.setFirstInput(acsop)
    outputsop.setDisplayFlag(True)
    sopcreatenet.layoutChildren()

    sopcreate.setFirstInput(confasset)
    geom.setFirstInput(sopcreate)
    mlib.setFirstInput(geom)
    shade.setFirstInput(mlib)
    casset.setFirstInput(shade)
    refasset.setInput(1, casset)
    camera.setFirstInput(refasset)
    lgraft.setFirstInput(camera)
    lcoll.setFirstInput(reflights)
    lmixer.setFirstInput(lcoll)
    lgraft.setNextInput(lmixer)
    larnrsettings.setFirstInput(lgraft)
    usdrop.setFirstInput(larnrsettings)

    hou_parm_template = hou.StringParmTemplate("assetname", "Aseet Name", 1, default_value=(["asset"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), menu_type=hou.menuType.StringReplace)
    confasset.addSpareParmTuple(hou_parm_template)

    hou_parm_template = hou.StringParmTemplate("savepath", "Save Path", 1, default_value=(["$HIP/usd/"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
    confasset.addSpareParmTuple(hou_parm_template)

    sopcreate.parm('pathprefix').set('/')
    acsop.parm('name1').set('name')
    acsop.parm('class1').set(1) #primitive
    acsop.parm('type1').set(3) #string
    acsop.parm('string1').set('`chs("../../../../configure_asset/assetname")`')
    geom.parm('setsavepath').set(1)
    geom.parm('savepath').set('`chs("../configure_asset/savepath")``chs("../configure_asset/assetname")`_geom.usdc')
    geom.parm('setdefaultprim').set(1)
    geom.parm('defaultprim').set('/`chs("../configure_asset/assetname")`')
    geom.parm('startnewlayer').set(1)
    mlib.parm('matpathprefix').set('/`chs("../configure_asset/assetname")`/materials/')
    shade.parm('setsavepath').set(1)
    shade.parm('savepath').set('`chs("../configure_asset/savepath")``chs("../configure_asset/assetname")`_shade.usdc')
    shade.parm('startnewlayer').set(1)
    casset.parm('setsavepath').set(1)
    casset.parm('setdefaultprim').set(1)
    casset.parm('defaultprim').set('/`chs("../configure_asset/assetname")`')
    casset.parm('savepath').set('`chs("../configure_asset/savepath")``chs("../configure_asset/assetname")`.usda')
    refasset.parm('reftype').set('inputref')
    refasset.parm('primpath').set('/lookdev/`chs("../configure_asset/assetname")`')
    reflights.parm('primpath').set('/$OS')
    reflights.parm('filepath1').set('$ASSETS_DIR/studios/light_rigs/usd/studio_light_set01.usdc')
    lcoll.parm('includepattern1').set('/studio_light_set01/*')
    lcoll.parm('collectionname1').set('set01')
    lgraft.parm('destpath').set('/lookdev')
    camera.parm('primpath').set('/lookdev/cameras/$OS')
    larnrsettings.parm('camera2').set(camera.parm('primpath').eval())
    usdrop.parm('enableoutputprocessor_simplerelativepaths').set(0)
    usdrop.parm('defaultprim').set('/lookdev')
    usdrop.parm('lopoutput').set('`chs("../configure_asset/savepath")``chs("../configure_asset/assetname")`_lookdev.usda')
    
    if check_type('redshift_usd_material'):
        pass
        
    if check_type('pxrdisney'):
        pass
    
    if check_type('octane::NT_MAT_UNIVERSAL'):
        pass

    con.layoutChildren()