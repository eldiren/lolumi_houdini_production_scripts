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
    lcoll = con.createNode('collection')
    lgraft = con.createNode('graft', 'graft_lights')
    usdrop = con.createNode('usd_rop')
    rsettings = con.createNode('rendersettings')
    beautyrvar = con.createNode('rendervar', 'beauty')
    albedorvar = con.createNode('rendervar', 'albedo')
    diffdirvar = con.createNode('rendervar', 'diffuse_direct')
    diffidirvar = con.createNode('rendervar', 'diffuse_indirect')
    specdirvar = con.createNode('rendervar', 'specular_direct')
    specidirvar = con.createNode('rendervar', 'specular_indirect')
    specrvar = con.createNode('rendervar', 'specular')
    posrvar = con.createNode('rendervar', 'position')
    normrvar = con.createNode('rendervar', 'normal')
    depthrvar = con.createNode('rendervar', 'depth')
    rproduct = con.createNode('renderproduct')
    usdrender = con.createNode('usdrender_rop')
    objnet = con.createNode('objnet', 'cam_net')
    camera = objnet.createNode('cam')
    simport = con.createNode('sceneimport', 'import_cam')
    
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
    simport.setFirstInput(refasset)
    lgraft.setFirstInput(simport)
    lcoll.setFirstInput(reflights)
    lmixer.setFirstInput(lcoll)
    lgraft.setNextInput(lmixer)
    beautyrvar.setFirstInput(lgraft)
    albedorvar.setFirstInput(beautyrvar)
    diffdirvar.setFirstInput(albedorvar)
    diffidirvar.setFirstInput(diffdirvar)
    specdirvar.setFirstInput(diffidirvar)
    specidirvar.setFirstInput(specdirvar)
    specrvar.setFirstInput(specidirvar)
    posrvar.setFirstInput(specrvar)
    normrvar.setFirstInput(posrvar)
    depthrvar.setFirstInput(normrvar)
    rproduct.setFirstInput(depthrvar)
    rsettings.setFirstInput(rproduct)
    usdrop.setFirstInput(rsettings)
    usdrender.setFirstInput(rsettings)

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
    lcoll.parm('primpattern1').set('/studio_light_set01/*')
    lcoll.parm('collectionname').set('set01')
    lgraft.parm('destpath').set('/lookdev')
    beautyrvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    beautyrvar.parm('sourceName').set('RGBA')
    beautyrvar.parm('dataType').set('color3f')
    beautyrvar.parm('xn__driverparametersaovname_jebkd').set('beauty')
    beautyrvar.parm('xn__driverparametersaovformat_shbkd').set('float3')
    albedorvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    albedorvar.parm('sourceName').set('albedo')
    albedorvar.parm('dataType').set('color3f')
    albedorvar.parm('xn__driverparametersaovname_jebkd').set('albedo')
    albedorvar.parm('xn__driverparametersaovformat_shbkd').set('float3')
    diffdirvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    diffdirvar.parm('sourceName').set('diffuse_direct')
    diffdirvar.parm('dataType').set('color3f')
    diffdirvar.parm('xn__driverparametersaovname_jebkd').set('diffuse_direct')
    diffdirvar.parm('xn__driverparametersaovformat_shbkd').set('float3')
    diffidirvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    diffidirvar.parm('sourceName').set('diffuse_indirect')
    diffidirvar.parm('dataType').set('float3')
    diffidirvar.parm('xn__driverparametersaovname_jebkd').set('diffuse_indirect')
    diffidirvar.parm('xn__driverparametersaovformat_shbkd').set('float3')
    specdirvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    specdirvar.parm('sourceName').set('specular_direct')
    specdirvar.parm('dataType').set('float3')
    specdirvar.parm('xn__driverparametersaovname_jebkd').set('specular_direct')
    specdirvar.parm('xn__driverparametersaovformat_shbkd').set('float3')
    specidirvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    specidirvar.parm('sourceName').set('specular_indirect')
    specidirvar.parm('dataType').set('float3')
    specidirvar.parm('xn__driverparametersaovname_jebkd').set('specular_indirect')
    specidirvar.parm('xn__driverparametersaovformat_shbkd').set('color3f')
    specrvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    specrvar.parm('sourceName').set('specular')
    specrvar.parm('dataType').set('float3')
    specrvar.parm('xn__driverparametersaovname_jebkd').set('specular')
    specrvar.parm('xn__driverparametersaovformat_shbkd').set('color3f')
    posrvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    posrvar.parm('sourceName').set('P')
    posrvar.parm('dataType').set('color3f')
    posrvar.parm('xn__driverparametersaovname_jebkd').set('P')
    posrvar.parm('xn__driverparametersaovformat_shbkd').set('float3')
    normrvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    normrvar.parm('sourceName').set('N')
    normrvar.parm('dataType').set('color3f')
    normrvar.parm('xn__driverparametersaovname_jebkd').set('N')
    normrvar.parm('xn__driverparametersaovformat_shbkd').set('float3')
    depthrvar.parm('primpath').set('/lookdev/Render/Products/Vars/$OS')
    depthrvar.parm('sourceName').set('Z')
    depthrvar.parm('dataType').set('color3f')
    depthrvar.parm('xn__driverparametersaovname_jebkd').set('Z')
    depthrvar.parm('xn__driverparametersaovformat_shbkd').set('float3')

    simport.parm('objdestpath').set('/lookdev/cameras')
    simport.parm('rootobject').set(objnet.path())
    simport.parm('filter').set('!!OBJ/CAMERA!!')
    simport.parm('objects').set('*')
    usdrop.parm('enableoutputprocessor_simplerelativepaths').set(0)
    usdrop.parm('defaultprim').set('/lookdev')
    usdrop.parm('lopoutput').set('`chs("../configure_asset/savepath")``chs("../configure_asset/assetname")`_lookdev.usda')
    rproduct.parm('orderedVars').set(beautyrvar.parm('primpath').eval() + ' ' + 
    albedorvar.parm('primpath').eval() + ' ' +
    diffdirvar.parm('primpath').eval() + ' ' +
    diffidirvar.parm('primpath').eval() + ' ' +
    specdirvar.parm('primpath').eval() + ' ' +
    specidirvar.parm('primpath').eval() + ' ' +
    specrvar.parm('primpath').eval() + ' ' +
    posrvar.parm('primpath').eval() + ' ' +
    normrvar.parm('primpath').eval() + ' ' +
    depthrvar.parm('primpath').eval())
    rproduct.parm('primpath').set('/lookdev/Render/Products/$OS')
    rproduct.parm('productName').set('arnoldProduct')
    rproduct.parmTuple('resolution')[0].set(1920)
    rproduct.parmTuple('resolution')[1].set(1080)
    rsettings.parm('primpath').set('/lookdev/Render/$OS')
    rsettings.parm('camera').set('/lookdev/cameras/'+ camera.name())
    rsettings.parmTuple('resolution')[0].set(1920)
    rsettings.parmTuple('resolution')[1].set(1080)
    rsettings.setDisplayFlag(True)

    if check_type('arnold_materialbuilder'):
        rsettings.parm('xn__arnoldglobalabort_on_error_control_gwbg').set('set') 
        rsettings.parm('xn__arnoldglobalabort_on_error_fjbg').set(0)
    
    if check_type('redshift_usd_material'):
        pass
        
    if check_type('pxrdisney'):
        pass
    
    if check_type('octane::NT_MAT_UNIVERSAL'):
        pass

    con.layoutChildren()