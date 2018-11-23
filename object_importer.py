# Normally used in the Scripts section of a digital asset as a PythonModule
# This script accepts a directory of set of files normally export via objects_to_docs.py
# in C4D, it also accepts an abc file generated from objects_to_particles.py in C4d
# using a combination of the two it can import a whole scene with instances automatically
# and it can set the materials too

import os, sys, ctypes, string, getopt, glob, json

import hou
from arnold import *

import htoa
from htoa.universe import HaUniverse
from htoa.node.node import pullHouParms, houdiniParmGet, arnoldParmSet
from htoa.node.parms import *

universe = None

###
# Class to represent an Arnold node. Makes AtNode pointer hashable.
###
class ArnoldNode:
    
    def __init__(self, n):
        self.node = None
        self.nodePtr = 0
        if not n: return

        if hasattr(n, "contents"):
            self.node = n
            self.nodePtr = ctypes.addressof(n.contents)
        else:
            self.nodePtr = n
            self.node = NullToNone(n, POINTER(AtNode))
            
        if self.node:
            self.node = self.node.contents
    
    def IsValid(self):
        return self.node is not None
        
    def GetNodeEntry(self):
        return AiNodeGetNodeEntry(self.node)
        
    def GetNodeEntryName(self):
        return AiNodeEntryGetName(self.GetNodeEntry())
        
    def GetName(self):
        return AiNodeGetName(self.node)
            
    def __hash__(self):
        return self.nodePtr
        
    def  __eq__(self, other):
        return isinstance(other, ArnoldNode) and self.nodePtr == other.nodePtr
    
    def  __ne__(self, other):
        return not self.__eq__(other)
        
    def  __cmp__(self, other):
        if not isinstance(other, ArnoldNode): return -1
        if self.nodePtr == other.nodePtr: return 0
        if self.nodePtr < other.nodePtr: return -1
        return 1
    
###
# Class to represent a link between shaders.
###    
class ShaderLink:
    def __init__(self, param, link):
        self.param = param
        self.link = link

###
# Opens the Arnold universe.
###
def Begin():
    global universe
    universe = HaUniverse()
    universe.reset()

###
# Closes the Arnold universe.
###
def End():
    global universe
          
    universe.destroy()
    universe.release()

###
# Creates a shader in the network by the given Arnold node.
# Sets all parameters.
###
def CreateShader(material, shader):
    if shader is None: 
        return None

    nodeEntry = shader.GetNodeEntry()
    nodeEntryName = shader.GetNodeEntryName()
    
    name = shader.GetName()
    name = name.split('|')[-1]
    name = name.split('/')[-1]
    
    shaderNode = hou.node(material.path()).createNode("arnold::" + nodeEntryName, name)
    
    if shaderNode is None:
        return None
    
    # set parameters
    piter = AiNodeEntryGetParamIterator(nodeEntry)
    while not AiParamIteratorFinished(piter):
        pentry = AiParamIteratorGetNext(piter)
        param = AiParamGetName(pentry)
        paramType = AiParamGetType(pentry)
        
        if paramType == AI_TYPE_BYTE:
            shaderNode.parm(param).set(AiNodeGetByte(shader.node, param))
        if paramType == AI_TYPE_INT:
            shaderNode.parm(param).set(AiNodeGetInt(shader.node, param))
        if paramType == AI_TYPE_UINT:
            shaderNode.parm(param).set(AiNodeGetUInt(shader.node, param))
        if paramType == AI_TYPE_BOOLEAN:
            shaderNode.parm(param).set(AiNodeGetBool(shader.node, param))
        if paramType == AI_TYPE_FLOAT:
            shaderNode.parm(param).set(AiNodeGetFlt(shader.node, param))
        if paramType == AI_TYPE_RGB:
            rgb = AiNodeGetRGB(shader.node, param)
            shaderNode.parmTuple(param)[0].set(rgb.r)
            shaderNode.parmTuple(param)[1].set(rgb.g)
            shaderNode.parmTuple(param)[2].set(rgb.b)
        if paramType == AI_TYPE_RGBA:
            rgba = AiNodeGetRGBA(shader.node, param)
            shaderNode.parmTuple(param)[0].set(rgba.r)
            shaderNode.parmTuple(param)[1].set(rgba.g)
            shaderNode.parmTuple(param)[2].set(rgba.b)
        if paramType == AI_TYPE_VECTOR:
            v = AiNodeGetVec(shader.node, param)
            shaderNode.parmTuple(param)[0].set(v.x)
            shaderNode.parmTuple(param)[1].set(v.y)
            shaderNode.parmTuple(param)[2].set(v.z)
        if paramType == AI_TYPE_VECTOR2:
            v = AiNodeGetVec2(shader.node, param)
            shaderNode.parmTuple(param)[0].set(v.x)
            shaderNode.parmTuple(param)[1].set(v.y)
        if paramType == AI_TYPE_STRING:
            if (param != "name"):
              shaderNode.parm(param).set(AiNodeGetStr(shader.node, param))
        if paramType == AI_TYPE_MATRIX:
            matrix = AtMatrix()
            AiNodeGetMatrix(shader.node, param, matrix)
            #v1 = c4d.Vector(matrix.a00, matrix.a01, matrix.a02) 
            #v2 = c4d.Vector(matrix.a10, matrix.a11, matrix.a12)
            #v3 = c4d.Vector(matrix.a20, matrix.a21, matrix.a22)
            #off = c4d.Vector(matrix.a03, matrix.a13, matrix.a23)
            #m = c4d.Matrix(off, v1, v2, v3)
            #data.SetMatrix(paramId, m)
        if paramType == AI_TYPE_ENUM:
            paramEnum = AiParamGetEnum(pentry)
            paramVal = AiEnumGetString(paramEnum, AiNodeGetInt(shader.node, param))
            shaderNode.parm(param).set(paramVal)
            
    ##
    # shaders with custom import logic
    ##

    # ramp_float
    if nodeEntryName == "ramp_float":
        SetupRampFloat(shaderNode, shader)
    # ramp_rgb
    elif nodeEntryName == "ramp_rgb":
        SetupRampRgb(shaderNode, shader)

    return shaderNode

def SetupRampRgb(shaderNode, aishader):
    blin = hou.rampBasis.Linear
    bcon = hou.rampBasis.Constant
    bcat = hou.rampBasis.CatmullRom
    bbez = hou.rampBasis.Bezier
    bbsl = hou.rampBasis.BSpline
    
    colorArrayPtr = AiNodeGetArray(aishader.node, "color")
    positionArrayPtr = AiNodeGetArray(aishader.node, "position")
    if colorArrayPtr is None or positionArrayPtr is None:
        return

    colorArray = NullToNone(colorArrayPtr, POINTER(AtArray)).contents
    positionArray = NullToNone(positionArrayPtr, POINTER(AtArray)).contents
    
    colors = []
    positions = []
    for i in range(0, AiArrayGetNumElements(positionArray)):
        rgb = AiArrayGetRGB(colorArray, i)
        position = AiArrayGetFlt(positionArray, i)
        
        colors.append((rgb.r, rgb.g, rgb.b))
        positions.append(position)
        
    basis = (blin,) * len(positions)
    rampdata = hou.Ramp(basis, positions, colors)    

    parm = shaderNode.parm('ramp')
    parm.set(rampdata)

def SetupRampFloat(shaderNode, aishader):
    return
    
###
# Connects the given shaders.
###
def AddConnection(material, srcNode, dstNode, dstParamUniqueName):
    # the idea is we get the input index using the param name and then use that index
    # to set a connection
    #inputIndex = dstNode.setInput(dstParamUniqueName)
    #dstNode.setInput(inputIndex, srcNode)
    dstNode.setNamedInput(dstParamUniqueName, srcNode, 0)
    
###
# Creates connections in the shader network.
###
def CreateLinks(mat, shader, links, shaderMap):
    shaderLinks = links[shader]
    if not shaderLinks:
        return
    
    #The node entry name is the shader type, prefixing it with Arnold:: in houdini will create the proper vop node
    shaderNodeEntryName = shader.GetNodeEntryName()
    shaderNode = shaderMap.get(shader)

    linkedShaders = []
    
    for sindex, shaderLink in enumerate(shaderLinks):
        linkedShader = shaderLink.link
        if not linkedShader.IsValid(): continue
        linkedShaderType = linkedShader.GetNodeEntryName()
        linkedShaderName = linkedShader.GetName()

        # create linked shader
        linkedShaderNode = shaderMap.get(linkedShader)
        if linkedShaderNode is None:
            linkedShaderNode = CreateShader(mat, linkedShader)
            if not linkedShaderNode:
                print "Failed to create shader: %s (%s)", linkedShaderName, linkedShaderType
                continue
            shaderMap[linkedShader] = linkedShaderNode
            
            linkedShaders.append(linkedShader)

        # create connection
        AddConnection(mat, linkedShaderNode, shaderNode, shaderLink.param)


    # create links
    for linkedShader in linkedShaders:
        CreateLinks(mat, linkedShader, links, shaderMap)
        
###
# Creates Arnold Shader Network materials.
# Creates all beauty and displacement shaders in a network,
# sets all parameters and connects the shaders.
###
def CreateMaterials(rootShaders, displacements, links, mat_path):
    # {ArnoldNode: GvNode}
    shaderMap = {}

    for i, rootShader in enumerate(rootShaders):
        if not rootShader or not rootShader.IsValid(): continue
        rootShaderType = rootShader.GetNodeEntryName()
        rootShaderName = rootShader.GetName()
        
        # Houdini does not like the pipe or slash character, generally the last name after the split should be our
        # shader name
        node_name = rootShaderName.split('/')[-1]
        node_name = node_name.split('|')[-1] 
        
        # create arnold vop network
        mat = hou.node(mat_path).createNode("arnold_vopnet", node_name)
        
        # create root shader
        rootShaderNode = shaderMap.get(rootShader)
        if rootShaderNode is None:
            matChildren = mat.children()
            rootShaderNode = CreateShader(mat, rootShader)
            matChildren[0].setFirstInput(rootShaderNode)
            #rootShaderNode = matChildren[0].createInputNode(0, "arnold::" + rootShaderType)
            
            #rootShaderNode = hou.node(mat.path()).createNode("arnold::" + rootShaderType)

            if rootShaderNode is None:
                print "Failed to create shader %s (%s)" % (rootShaderName, rootShaderType)
                continue
            shaderMap[rootShader] = rootShaderNode
        
        # create links
        CreateLinks(mat, rootShader, links, shaderMap)
        
        # check if the root material is a c4d texture tag, if so delete it
        rootBeauty = mat.children()[0].inputs()[0]
        if rootBeauty:
            if rootBeauty.type().name() == 'arnold::c4d_texture_tag':
                rootBeauty.destroy()
            
        mat.layoutChildren()
            
###
# Collects shader links of the given Arnold node
# and stores them in the given map.
###
def CollectLinks(node, links):
    if not node.IsValid():
        return
    
    # skip when already processed
    if node in links:
        return
    
    # check parameters
    shaderLinks = []
    
    piter = AiNodeEntryGetParamIterator(node.GetNodeEntry())
    while not AiParamIteratorFinished(piter):
        pentry = AiParamIteratorGetNext(piter)
        param = AiParamGetName(pentry)
        if AiNodeIsLinked(node.node, param):
            link = ArnoldNode(AiNodeGetLink(node.node, param))
            if link.IsValid():
                shaderLinks.append(ShaderLink(param, link))
            
            # recursive call
            CollectLinks(link, links)
            
    links[node] = shaderLinks
        
###
# Collects all shader networks assigned to shapes.
###
def ReadShaderNetworks(assPath, rootShaders, displacements, links, shadernames):
    print "------------ReadShaderNetworks-----------"
    houNodeName = ""
    
    # read ass file
    AiASSLoad(assPath)

    aiNodeIterator = AiUniverseGetNodeIterator(AI_NODE_SHADER)
    while not AiNodeIteratorFinished(aiNodeIterator):
        node = AiNodeIteratorGetNext(aiNodeIterator)
                        
        # we'll use the split command again, if the first name is c4d then we know
        # the second name will be surface, displacement, or the actual shadername
        # if it's surface or displacement then it's a root shader
        nodeName = AiNodeGetName(node)
        
        # houdini uses the path to the shader, so the first character will be a slash, interestingly, C4DtoA 3.0.0
        # and up also uses the slash as the first character so with have to do a interesting check here
        if(nodeName[0] == "/"):
            # C4D names will have pipes, Houdini and Maya won't
            nameComponents = nodeName.split("/")
            if(nodeName.count('|') > 0):
                # for c4d the last component need to be split by '|' so we can get the name
                nameComponents = nameComponents[-1].split("|")
                houNodeName = nameComponents[-1]
            else:
                # for houdini the last component is the name
                houNodeName = nameComponents[-1]
        
        
        if houNodeName in shadernames:
            print "Root beauty found named: " + houNodeName
            # a beauty root shader will be a shader in the shadernames we passed in
            aShader = ArnoldNode(node)
            rootShaders.add(aShader)

            # links 
            CollectLinks(aShader, links)
                  
            """
            # displacement
            if nameComponents[2] == 'displacement':
                aShader = None
                aDisp = ArnoldNode(node)
                FindBeautyNode(nameComponents[1], aShader)
                if(aShader):
                    displacements[aShader] = aDisp

                    # links
                    CollectLinks(aDisp, links)
            """
    AiNodeIteratorDestroy(aiNodeIterator)
    
    print "-----------------------"

def FindBeautyNode(matname, shader):
    aiNodeIterator = AiUniverseGetNodeIterator(AI_NODE_SHADER)
    while not AiNodeIteratorFinished(aiNodeIterator):
        node = AiNodeIteratorGetNext(aiNodeIterator)
        # it's possible for some odd reason the node may not have the GetName attribute, we'll set it to something 
        # basic if that's the case
        try:
            nodeName = node.GetName()
        except AttributeError as error:
            nodeName = "c4d|ArnoldShader|shader"
        except Exception as exception:
            nodeName = "c4d|ArnoldShader|shader"
            
        nameComponents = nodeName.split("|")
        if nameComponents[2] == "beauty" and nameComponents[1] == matname:
            shader = ArnoldNode(node)
            
    shader = None
        
###
# Console logger.
###
def LogToConsole(mask, severity, message, tabs):
    severityStr = ""
    if severity == AI_SEVERITY_WARNING:
        severityStr = " WARNING"
    elif severity == AI_SEVERITY_ERROR:
        severityStr = "   ERROR"
    elif severity == AI_SEVERITY_FATAL:
        severityStr = "   FATAL"
   
    print "Arnold | %s %s" % (severityStr, message)
    
def arnold_material_import(fileName, mat_path, shadernames):
    if AiUniverseIsActive():
        PrintError("Arnold render is already runnning. Please stop the render first.", True)

    try:
        Begin()
        
        # setup logging
        # FIXME no messages displayed in the console
        logfn = AtMsgCallBack(LogToConsole)
        AiMsgSetCallback(logfn)
        AiMsgSetConsoleFlags(AI_LOG_WARNINGS | AI_LOG_ERRORS)
        
        path = os.getenv( 'ARNOLD_PLUGIN_PATH' )
        AiLoadPlugins(path)
        
        # read shader networks
        # set(ArnoldNode)
        rootShaders = set()
        
        # {ArnoldNode, ArnoldNode}
        displacements = {}
        
        # {ArnoldNode, [ShaderLink]}
        links = {}
        ReadShaderNetworks(fileName, rootShaders, displacements, links, shadernames)
    
        # build Houdini materials
        CreateMaterials(rootShaders, displacements, links, mat_path)
    finally:
        End()

def material_assign_import(node_path, mmat_path, gmat_path, fileName, usematpath):
    # creates a main and sub material node in the selected object's path using a file 
    # that holds each material and the objects and groups assigned to it
    
    # hold holds the shader names for use by shop creation later
    shaderNames = []
    
    # Grab the selected object
    #print hou.selectedNodes() #debug
    this = hou.node(node_path)
    prims = this.geometry().prims()
    mmat = hou.node(mmat_path)
    gmat = hou.node(gmat_path)
    
    # open the file
    f = open(fileName, 'r')
    
    data = json.load(f)  
    """
    # check to see if this object is in the override dict, if so we set it's overrides
    hnode = this.parent()
    objects = data['overrides']
    if hnode.name() in objects:
        value = data['overrides'][obj]
        if tag[C4DAIP_POLYMESH_SUBDIV_TYPE] != 0 :
            hnode.parm('/obj/geo1/ar_subdiv_type').set(value['subdiv_type'])
            hnode.parm('/obj/geo1/ar_disp_height').set(value['disp_height'])
            hnode.parm('/obj/geo1/ar_subdiv_iterations').set(value['subdiv_iterations'])
            hnode.parm('/obj/geo1/ar_disp_zero_value').set(value['disp_zero_value'])
            hnode.parm('/obj/geo1/ar_subdiv_adaptive_metric').set(value['subdiv_adaptive_metric'])
            hnode.parm('/obj/geo1/ar_disp_padding').set(value['disp_padding'])
            hnode.parm('/obj/geo1/ar_subdiv_adaptive_error').set(value['subdiv_adaptive_error'])
            hnode.parm('/obj/geo1/ar_subdiv_smooth_derivs').set(value['subdiv_smooth_derivs']) 
            hnode.parm('/obj/geo1/ar_subdiv_uv_smoothing').set(value['subdiv_uv_smoothing'])
            hnode.parm('/obj/geo1/ar_subdiv_adaptive_space').set(value['subdiv_adaptive_space'])
                
        hnode.parm('/obj/geo1/ar_opaque').set(value['opaque'])
        hnode.parm('/obj/geo1/ar_matte').set(value['matte'])
        hnode.parm('/obj/geo1/ar_disp_autobump').set(value['disp_autobump'])
        hnode.parm('/obj/geo1/ar_invert_normals').set(value['invert_normals'])
        hnode.parm('/obj/geo1/ar_receive_shadows').set(value['receive_shadows'])
        hnode.parm('/obj/geo1/ar_self_shadows').set(value['self_shadows'])
        hnode.parm('/obj/geo1/ar_sss_setname').set(value['sss_setname'])
        hnode.parm('/obj/geo1/ar_smoothing').set(value['smoothing'])                               
    """
    
    # read the shader assignments for the shader dict in the json
    geoMatCnt = 0
    pgrpMatCnt = 0
    
    shaders = data['shaders']
    for sname in shaders:
        shaderNames.append(sname)
        
        shader = data['shaders'][sname]
        if len(shader['geo']) > 0:
            geoMatCnt = geoMatCnt + 1
            mmat.parm('num_materials').set(geoMatCnt)
            if(usematpath):
                mmat.parm('shop_materialpath' + str(geoMatCnt)).setExpression('chs("../../mat_path")/materials/' + sname)
            else:
                mmat.parm('shop_materialpath' + str(geoMatCnt)).set("../materials/" + sname)
                
            # the geo dict contains objects where the material is applied as a whole
            grp_prims = ""
            idx = 0
            for geo in shader['geo']:
                objname = geo
                                
                # objname is going to be the object name, we need to find a path that has this name, that'll be
                # what set out group condition equal to
                for prim in prims:
                    path = prim.stringAttribValue('path')
                    if path.find(objname) != -1:
                        grp_prims = grp_prims + "@path=" + prim.stringAttribValue('path') + " "
            
            # set group equal to the found prims
            if(grp_prims != ""):
                mmat.parm('group' + str(geoMatCnt)).set(grp_prims)
        
        # next lets read the groups(facesets/polyselections)
        if len(shader['groups']) > 0:
            pgrpMatCnt = pgrpMatCnt + 1
            gmat.parm('num_materials').set(pgrpMatCnt)
            
            gmat.parm('shop_materialpath' + str(pgrpMatCnt)).set("../materials/" + sname)
            
            for pgrp in shader['groups']:
                assign_grps = ""
                
                assign_grps = assign_grps + pgrp + " "
                
            # set group equal to the found assignment groups
            gmat.parm('group' + str(pgrpMatCnt)).set(assign_grps)
    
    return shaderNames

def import_objects():            
    obj_path = ""
    obj_folder = None
    objsImported = []
    this = hou.node('.')
    
    use_mat_path = this.parm('use_mat_path')
    
    # if path is to a directory then we list everything in the directory
    # otherwise we'll create a list with one file
    is_dir = this.parm('is_dir')
    
    if(is_dir.eval() == True):   
        obj_path = this.evalParm('file_dir_path')
        obj_folder = os.listdir(obj_path)
    else:
        path_tokens = os.path.split(this.evalParm('file_dir_path'))
        obj_path = path_tokens[0] + "/"
        obj_folder = [path_tokens[1]]
    
    import_node = hou.node(this.evalParm('path_prefix')).createNode('subnet', this.evalParm('network_name'))
    mat_path = this.evalParm('mat_dir_path')
    
    # let's get the path for the instances set up
    pntsNodePath = ""
    
    processInstance = this.evalParm('enable_instances')
    unpackGeo = this.evalParm('unpack')
    
    if processInstance :
        if(this.evalParm('is_file') == False):
            pntsNodePath = this.evalParm('instance_pnts_obj')
    
    # create a scene object for copypnts style layout
    sceneNode = import_node.createNode('geo', 'scene')
    sceneNode.children()[-1].destroy() # delete the file node
    sceneNodeMerge = sceneNode.createNode('merge')
    
    # load up the objects
    for file in obj_folder:
        mmat = None
        main_node = None
        shaderNames = None
    
        if file.endswith(".abc") or file.endswith(".fbx") or file.endswith(".obj") or file.endswith(".bgeo"):
            filename = file.split('.')
    
            obj_node = import_node.createNode("geo", filename[0])
            
            obj_node.createNode("shopnet", "materials");
            
            isPntsNode = False
            
            # if the points node is a file we have to see if the node we're creating here is it
            if(processInstance):
                if(this.evalParm('is_file') == True):
                    path_tokens = os.path.split(this.evalParm('instance_pnts_file'))
                    pntsName = path_tokens[1].split('.')
                    if(pntsName[0] == obj_node.name()):
                        pntsNodePath = obj_node.path()
                        isPntsNode = True
                        obj_node.parm('vm_renderpoints').set(0) # turn off point rendering
            
            if(not isPntsNode):
                objsImported.append(obj_node)
                
            file_node = None
            
            print "Processing " + filename[0]
            
            # if the file is an abc node we'll create an alembic node instead of using the file node
            if file.endswith(".abc"):
                obj_node.node("file1").destroy()
            
                file_node = obj_node.createNode("alembic")
                file_node.parm("fileName").set(obj_path + file)
                
                # we can only do the material assignment stuff on abc files, because that's the only type of file that has paths
                xform = obj_node.createNode("xform")
                xform.setFirstInput(file_node)
                xform.parm('scale').set(this.parm('import_scale').eval())
                xform.setDisplayFlag(True)
                xform.setRenderFlag(True)
                
                geoNode = None
                if unpackGeo or isPntsNode:
                    unpack = obj_node.createNode("unpack")
                    unpack.setFirstInput(xform)
                    unpack.parm('transfer_attributes').set("path")
                    unpack.setDisplayFlag(True)
                    unpack.setRenderFlag(True)
                    geoNode = unpack
                else:
                    geoNode = xform
            
                # see if materials exist and if so load them
                matfile = mat_path + filename[0] + ".json"
                if os.path.isfile(matfile):
                    #print "Processing " + matfile
                    # Import material assignments
                    mmat = obj_node.createNode('material', 'geo_material')
                    gmat = obj_node.createNode('material', 'pgrp_material')
            
                    mmat.setFirstInput(geoNode)
                    gmat.setFirstInput(mmat)
                    shaderNames = material_assign_import(file_node.path(), mmat.path(), gmat.path(), matfile, use_mat_path)
                    gmat.setDisplayFlag(True)
                    gmat.setRenderFlag(True)            
            else:
                file_node = obj_node.node("file1")
                file_node.parm("file").set(obj_path + file)
                    
            obj_node.layoutChildren()
            
            # see if arnold materials exist and if so load them
            assfile = mat_path + filename[0] + ".ass"
            if os.path.isfile(assfile):
                #print "Processing " + assfile
                arnold_material_import(assfile, obj_node.path() + "/materials", shaderNames)
            
            hou.node(obj_node.path() + "/materials").layoutChildren()
            #print "Processed " + filename[0]
    
    # now that the objects are loaded we can actually run through creating instance nodes for them
    if processInstance:
        pntsNode = hou.node(pntsNodePath)
        
        # add our name loading and transform extract chain to the points network
        hou.copyNodesTo(hou.node(this.path() + "/pnts_node_chain").children(), pntsNode)
        hou.node(pntsNode.path() + "/attribwrangle2").setFirstInput(hou.node(pntsNode.path() + "/unpack1"))
            
        pntsNode.layoutChildren()
        
        # create the object merge used to bring in instanced points
        # for new style instances
        objMergePnts = sceneNode.createNode('object_merge', pntsNode.name())
        objMergePnts.parm('objpath1').set('../../' + pntsNode.name())
        objMergePnts.parm('xformtype').set(1) # into this object
        
        instanceObjs = []
        # loop through instance objects
        for obj in objsImported:
            obj.setDisplayFlag(False)
            
            # creates new style instances
            
            objMergeAsset = sceneNode.createNode('object_merge', obj.name())
            objMergeAsset.parm('objpath1').set('../../' + obj.name())
            objMergeAsset.parm('xformtype').set(1) # into this object
            
            pntsDelete = sceneNode.createNode("delete")
            pntsDelete.setFirstInput(objMergePnts)
            
            pntsDelete.parm('negate').set(1) # delete non selected
            pntsDelete.parm('entity').set(1) # points
            pntsDelete.parm('group').set('@name="' + obj.name() + '*"') # set group
            
            copyToPnts = sceneNode.createNode('copytopoints')
            copyToPnts.setFirstInput(objMergeAsset)
            copyToPnts.setNextInput(pntsDelete)
            sceneNodeMerge.setNextInput(copyToPnts)
                    
            # creates old style instances
            instance = import_node.createNode('instance', 'instance_' + obj.name())
            print instance.children()[-1]
            instance.children()[-1].destroy() # delete the add node
            
            instance.parm('ptinstance').set(2) # fast point instancing
            instance.parm('instancepath').set('../' + obj.name())
            
            instance_merge = instance.createNode('object_merge')
            instance_merge.parm('xformtype').set(1) # into this object
            instance_merge.parm('objpath1').set('../../' + pntsNode.name())
            
            instance_delete = instance.createNode("delete")
            instance_delete.setFirstInput(instance_merge)
            
            instance_delete.parm('negate').set(1) # delete non selected
            instance_delete.parm('entity').set(1) # points
            instance_delete.parm('group').set('@name="' + obj.name() + '*"') # set group
            instance_delete.setDisplayFlag(True)
            instance_delete.setRenderFlag(True)
            instance.layoutChildren()
            
            instanceObjs.append(instance)
        
        import_node.layoutChildren(instanceObjs)    
        instancesBox = import_node.createNetworkBox()
        instancesBox.setComment('Instances')
        for instance in instanceObjs:
            instancesBox.addNode(instance)
            instancesBox.fitAroundContents()
            
    import_node.layoutChildren()