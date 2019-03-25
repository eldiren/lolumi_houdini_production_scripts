import os, sys, ctypes, string, getopt, glob, json
import hou

# imports character assets (FBX, ABC) and creates an HDA. this script creates a fetch CHOP which grabs the 
# current channel information for all the current nulls in the FBX subnet, then saves as a bclip. it the takes 
# the static geo for the character in question, and automatically creates a SOP network with proper connections 
# and one deform. The interface for the character complete with caching option. currently I haven't figured
# out how to set the CHOP output flag so you'll want to set in to the OUT null in CHOP

def charAssetsToHDA():
    this = hou.node('.')
    importNode = hou.hipFile.importFBX(this.parm('char_fbx_file').eval(), suppress_save_prompt=True, merge_into_scene=True, import_cameras=False, import_joints_and_skin=True, import_geometry=True, import_lights=False, import_animation=False, import_materials=False, resample_animation=False, resample_interval=1.0, override_framerate=False,framerate=-1, hide_joints_attached_to_skin=True, convert_joints_to_zyx_rotation_order=False, material_mode=hou.fbxMaterialMode.FBXShaderNodes, compatibility_mode=hou.fbxCompatibilityMode.Maya, single_precision_vertex_caches=False, triangulate_nurbs=False, triangulate_patches=False, import_global_ambient_light=False, import_blend_deformers_as_blend_sops=False, segment_scale_already_baked_in=True, convert_file_paths_to_relative=False, unlock_geometry=True, unlock_deformations=True, import_nulls_as_subnets=False, import_into_object_subnet=True, convert_into_y_up_coordinate_system=False)
    fbxNode = importNode[0]   
    
    if fbxNode:
        # set up the parameters
        
        # CHOP mocap params
        hou_parm_template = hou.StringParmTemplate("fbxfile", "FBX File", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.StringReplace)
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Character']), create_missing_folders=True)
        
        hou_parm_template = hou.StringParmTemplate("fbxclip", "Clip", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l CHOP/fbxagent/fbximport currentclip", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.Normal)
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Character']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("mocapswitch", "Use Mocap?", default_value=False)
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Character']), create_missing_folders=True)
        
        # Alembic params
        hou_parm_template = hou.LabelParmTemplate("labelparm", "Alembic", column_labels=([""]))
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("use_cache", "Use Cache", default_value=False)
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.FloatParmTemplate("cache_scale", "Cache Scale", 1, default_value=([1]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.MenuParmTemplate("trange", "Valid Frame Range", menu_items=(["off","normal","on"]), menu_labels=(["Render Current Frame","Render Frame Range","Render Frame Range Only (Strict)"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.FloatParmTemplate("f", "Start/End/Inc", 3, default_value=([0, 0, 1]), default_expression=(["$FSTART","$FEND",""]), default_expression_language=([hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.StringParmTemplate("cachefile", "Cache File", 1, default_value=(["$HIP/output.abc"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l exportnet/alembic filename", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.StringReplace)
        hou_parm_template.setTags({"autoscope": "0000000000000000", "filechooser_pattern": "*.abc"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ButtonParmTemplate("cache_btn", "Cache to Disk")
        hou_parm_template.setTags({"autoscope": "0000000000000000", "takecontrol": "always"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        #FBX params
        hou_parm_template = hou.SeparatorParmTemplate("sepparm")
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.LabelParmTemplate("labelparm2", "FBX", column_labels=([""]))
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.MenuParmTemplate("trange2", "Valid Frame Range", menu_items=(["off","normal","on"]), menu_labels=(["Render Current Frame","Render Frame Range","Render Frame Range Only (Strict)"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.FloatParmTemplate("f4", "Start/End/Inc", 3, default_value=([0, 0, 1]), default_expression=(["$FSTART","$FEND",""]), default_expression_language=([hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript,hou.scriptLanguage.Hscript]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.StringParmTemplate("take", "Render With Take", 1, default_value=(["_current_"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l exportnet/filmboxfbx1 take", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.Normal)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.StringParmTemplate("sopoutput", "Output File", 1, default_value=(["$HIP/out.fbx"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.FileReference, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l exportnet/filmboxfbx1 sopoutput", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.StringReplace)
        hou_parm_template.setTags({"autoscope": "0000000000000000", "filechooser_mode": "write"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("mkpath", "Create Intermediate Directories", default_value=True, default_expression='on', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("exportkind", "Export in ASCII Format", default_value=True, default_expression='on', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.StringParmTemplate("sdkversion", "FBX SDK Version", 1, default_value=([""]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="opmenu -l exportnet/filmboxfbx1 sdkversion", item_generator_script_language=hou.scriptLanguage.Hscript, menu_type=hou.menuType.Normal)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.MenuParmTemplate("vcformat", "Vertex Cache Format", menu_items=(["mayaformat","maxformat"]), menu_labels=(["Maya Compatible (MC)","3DS MAX Compatible (PC2)"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.MenuParmTemplate("invisobj", "Export Invisible Objects", menu_items=(["nullnodes","fullnodes"]), menu_labels=(["As Hidden Null Nodes","As Hidden Full Nodes"]), default_value=0, icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.FloatParmTemplate("polylod", "Conversion Level of Detail", 1, default_value=([1]), min=0, max=5, min_is_strict=True, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("detectconstpointobjs", "Detect Constant Point Count Dynamic Objects", default_value=True, default_expression='on', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("convertsurfaces", "Convert NURBS and Bezier Surfaces to Polygons", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("conservemem", "Conserve Memory at the Expense of Export Time", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("deformsasvcs", "Export Deforms as Vertex Caches", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("forceblendshape", "Force Blend Shape Export", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("forceskindeform", "Force Skin Deform Export", default_value=False, default_expression='off', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ToggleParmTemplate("exportendeffectors", "Export End Effectors", default_value=True, default_expression='on', default_expression_language=hou.scriptLanguage.Hscript)
        hou_parm_template.setTags({"autoscope": "0000000000000000"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        hou_parm_template = hou.ButtonParmTemplate("execute", "Save to Disk")
        hou_parm_template.setTags({"autoscope": "0000000000000000", "takecontrol": "always"})
        fbxNode.addSpareParmTuple(hou_parm_template, in_folder=(['Cache']), create_missing_folders=True)
        
        children = fbxNode.children()
        fbxNodeName = fbxNode.name().rsplit('_', 1)
        
        charGeo = fbxNode.createNode('geo', fbxNodeName[0] + '_geo')
        if len(charGeo.children()) > 0:
            charGeo.children()[0].destroy() # older version of houdini had a lone file node

        ccache = charGeo.createNode('alembic', 'char_abc_cache')
        ccache.parm('fileName').set('`chs("../../cachefile")`')
        cscale = charGeo.createNode('xform', 'cache_scale')
        cscale.setFirstInput(ccache)
        cscale.parm('scale').setExpression('ch("../../cache_scale")')
        cswitch = charGeo.createNode('switch', 'cache_switch')
        cswitch.parm('input').setExpression('ch("../../use_cache")')
        
        exportNet = fbxNode.createNode('ropnet', 'exportnet')
        alembicRop = exportNet.createNode('alembic', 'alembic')
        alembicRop.parm('execute').setExpression('ch("../../cache_btn")')
        alembicRop.parm('trange').setExpression('ch("../../trange")')
        alembicRop.parm('f1').setExpression('ch("../../f1")')
        alembicRop.parm('f2').setExpression('ch("../../f2")')
        alembicRop.parm('f3').setExpression('ch("../../f3")')
        alembicRop.parm('use_sop_path').set(1)
        alembicRop.parm('sop_path').set('../../' + charGeo.name())
        alembicRop.parm('build_from_path').set(1)
        alembicRop.parm('path_attrib').set('path')
        alembicRop.parm('root').set('')

        fbxRop = exportNet.createNode('filmboxfbx', 'fbx')
        fbxRop.parm('startnode').set('`opfullpath("../../")`')
        fbxRop.parm('createsubnetroot').set(0)
        
        fbxRop.parm('trange').setExpression('ch("../../trange2")')
        fbxRop.parm('f1').setExpression('ch("../../f41")')
        fbxRop.parm('f2').setExpression('ch("../../f42")')
        fbxRop.parm('f3').setExpression('ch("../../f43")')
        fbxRop.parm('take').setExpression('ch("../../take")')
        fbxRop.parm('sopoutput').setExpression('ch("../../sopoutput")')
        fbxRop.parm('mkpath').setExpression('ch("../../mkpath")')
        fbxRop.parm('exportkind').setExpression('ch("../../exportkind")')
        fbxRop.parm('sdkversion').setExpression('ch("../../sdkversion")')
        fbxRop.parm('vcformat').setExpression('ch("../../vcformat")')
        fbxRop.parm('invisobj').setExpression('ch("../../invisobj")')
        fbxRop.parm('polylod').setExpression('ch("../../polylod")')
        fbxRop.parm('detectconstpointobjs').setExpression('ch("../../detectconstpointobjs")')
        fbxRop.parm('convertsurfaces').setExpression('ch("../../convertsurfaces")')
        fbxRop.parm('conservemem').setExpression('ch("../../conservemem")')
        fbxRop.parm('deformsasvcs').setExpression('ch("../../deformsasvcs")')
        fbxRop.parm('forceblendshape').setExpression('ch("../../forceblendshape")')
        fbxRop.parm('forceskindeform').setExpression('ch("../../forceskindeform")')
        fbxRop.parm('exportendeffectors').setExpression('ch("../../exportendeffectors")')
        fbxRop.parm('execute').setExpression('ch("../../execute")')
        
        rigBox = fbxNode.createNetworkBox()
        rigBox.setComment('Rig')
                        
        for child in children:
            # for the fbxchop we need to rename it and set up a bclip/agent network to
            # drive animation on the joints
            if child.type().name() == 'chopnet':
                child.destroy()
            
            if child.type().name() == 'null':
                 # we want to set CHOP expressions for nulls so they move the bones with our mocap CHOPs
                 if child.name() is not fbxNodeName[0]: # check to make sure this is not the root null
                    child.parmTuple('t').deleteAllKeyframes()
                    child.parmTuple('r').deleteAllKeyframes()
                    child.parm('rx').setExpression('chop("../CHOP/OUT/$OS:$CH")')
                    child.parm('ry').setExpression('chop("../CHOP/OUT/$OS:$CH")')
                    child.parm('rz').setExpression('chop("../CHOP/OUT/$OS:$CH")')
                    child.parm('tx').setExpression('chop("../CHOP/OUT/$OS:$CH")')
                    child.parm('ty').setExpression('chop("../CHOP/OUT/$OS:$CH")')
                    child.parm('tz').setExpression('chop("../CHOP/OUT/$OS:$CH")')
                    rigBox.addNode(child)
            
            if child.type().name() == 'bone':
                # add the bones to the rig net box
                rigBox.addNode(child)
                    
            if child.type().name() == 'geo':
                if child.name() is not charGeo.name():
                    # we want to convert these to a single geo pointing to a alembic
                    hou.copyNodesTo(child.children(), charGeo)
                    child.destroy()
        
        rigBox.fitAroundContents()
        
        # build the CHOP network
        child = fbxNode.createNode('chopnet', 'CHOP')
        
        #let's fetch the original tpose and place in in a bclip
        fetch = child.createNode('fetch')
        fetch.parm('rate').set(24)
        fetch.parm('nodepath').set('../../* ')
        
        bclip = fetch.clipData(True)
        fileName = this.parm('char_bclip_file').eval()
        
        f = open(hou.expandString(fileName), 'wb')
        f.write(bclip)
        
        f.close()
        
        fetch.destroy()
        
        tposeChop = child.createNode('file', 'tpose_clip')
        tposeChop.parm('file').set(fileName)
        agentChop = child.createNode('agent', 'mocap')
        agentChop.parm('clipname').set('`chs("../../fbxclip")`')
        switch = child.createNode('switch', 'switch')
        switch.parm('index').setExpression('ch("../../mocapswitch")')
        
        outChop = child.createNode('null', 'OUT')
        sopNode = child.createNode('sopnet', 'fbxagent')
        
        switch.setFirstInput(tposeChop)
        switch.setNextInput(agentChop)
        outChop.setFirstInput(switch)
        
        fbxImport = sopNode.createNode('agent', 'fbximport')
        fbxImport.parm('fbxfile').set('`chs("../../../fbxfile")`')
        
        fbxImport.parm('input').set(2)
        
        agentChop.parm('soppath').set('../fbxagent/fbximport')
        
        outChop.setDisplayFlag(True)
        #outChop.setRenderFlag(True)
        
        child.layoutChildren()
        
        # work on the character geo point all the captures to an alembic file
        overMerge = charGeo.createNode('merge', 'merge')
        
        alembic = charGeo.createNode('alembic', 'char_abc_geo')
        fileName = this.parm('char_abc_file').eval()
        alembic.parm('fileName').set(fileName)
        
        unpack = charGeo.createNode('unpack', 'unpack')
        unpack.setFirstInput(alembic)
        unpack.parm('transfer_attributes').set('path shop_materialpath')
        
        children = charGeo.children()
        for child in children:
            if child.type().name() == 'file':
                nodeName = child.name()   
                deleteNode = charGeo.createNode('delete', 'isolate_' + nodeName)
                deleteNode.parm('negate').set(1)
                deleteNode.parm('group').set('@path="/' + nodeName + '/*"')
                deleteNode.setFirstInput(unpack)
                if len(child.outputs()) > 0:
                    delOutput = child.outputs()[0]
                    delOutput.setFirstInput(deleteNode)
                
                child.destroy()
            elif child.type().name() == 'deform':
                child.destroy()
            elif child.type().name() == 'channel':
                child.destroy()
            elif child.type().name() == 'capture':
                child.setGenericFlag(hou.nodeFlag.Lock, False) 
            elif child.type().name() == 'captureoverride':
                overMerge.setNextInput(child)
        
        deform = charGeo.createNode('deform', 'deform')
        deform.setFirstInput(overMerge)
        cswitch.setFirstInput(deform)
        cswitch.setNextInput(cscale)
        
        cswitch.setDisplayFlag(True)
        cswitch.setRenderFlag(True)
        
        charGeo.layoutChildren()

        hdaNode = fbxNode.createDigitalAsset(this.parm('asset_name').eval(), this.parm('hda_location').eval(), this.parm('desc').eval())
        hdaDef = hdaNode.type().definition()
        hdaOptions = hdaDef.options()
        hdaDef.save(hdaDef.libraryFilePath(), hdaNode, hdaOptions)