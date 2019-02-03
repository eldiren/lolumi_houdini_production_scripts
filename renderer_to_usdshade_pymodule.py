# normally used in the Scripts section of a digital asset as a PythonModule
# this script takes a directory path, a filename, and associated external
# renderer materials, and writes USD PBR(USDPreviewSurface) information 
# write_preview_shading() is implemented in such a way that it works nicely
# in a usd rop post script, you likely use set_usd_filename() as a callback 
# on a HDA button

import os, sys, ctypes, string, getopt, glob, json
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdUtils

import hou
from arnold import *

import htoa
from htoa.universe import HaUniverse
from htoa.node.node import pullHouParms, houdiniParmGet, arnoldParmSet
from htoa.node.parms import *
    
# creates rop filenames dynamically from an HDA dirpath and filename field
def set_usd_filename():
    this = hou.node('.')
    rObj = hou.node(this.parm('obj').eval())
    
    rawDir = rObj.parm('model_dir').eval()
    rawFile = rObj.parm('model_file').eval()
    
    hou.node('./abc_export').parm('filename').set(rawDir+'alembic/'+rawFile+'.abc')
    hou.node('./usdrop1').parm('usdfile').set(rawDir+'usd/'+rawFile+'.usda')
    hou.node('./rop_gltf1').parm('file').set(rawDir+'gltf/'+rawFile+'.glb')
    
# should create a new material with passed in properties
def newMaterial(stage, path, dclr, roughness, metallic, eclr=(0,0,0), opacity=1.0, ior=1.5, clearcoat=0.0, clearroug=0.0, occlusion=0.0):
    # TODO: keep adding more support, missing textures for now
    material = UsdShade.Material.Define(stage, path)
    pbrShader = UsdShade.Shader.Define(stage, path + '/PBRShader')

    pbrShader.CreateIdAttr("UsdPreviewSurface")
    pbrShader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(dclr)
    pbrShader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
    pbrShader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(metallic)
    pbrShader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).Set(eclr)
    pbrShader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(opacity)
    pbrShader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(ior)
    pbrShader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(clearcoat)
    pbrShader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(clearroug)

    material.CreateSurfaceOutput().ConnectToSource(pbrShader, "surface")

    return

def newMaterialViaShop(shopshader, stage, path):
    diffSet = False
    material = UsdShade.Material.Define(stage, path)
    uvInput = material.CreateInput('frame:stPrimvarName', Sdf.ValueTypeNames.Token)
    uvInput.Set('st')

    pbrShader = UsdShade.Shader.Define(stage, path + '/PBRShader')
    pbrShader.CreateIdAttr('UsdPreviewSurface')
    
    uvReader = UsdShade.Shader.Define(stage, path + '/uvReader')
    uvReader.CreateIdAttr('UsdPrimvarReader_float2')
    uvReader.CreateInput('varname', Sdf.ValueTypeNames.Token).ConnectToSource(uvInput)
    uvReader.CreateOutput('result', Sdf.ValueTypeNames.Float2)

    inputs = shopshader.inputConnections()
    for nodeInput in inputs:
        if nodeInput.outputName() == 'diffuseColor':
            inNode = nodeInput.inputNode()
            # create texture sampler node
            textureSampler = UsdShade.Shader.Define(stage, path + '/diffuseTexture')
            textureSampler.CreateIdAttr('UsdUVTexture')
            textureSampler.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(inNode.parm('file').eval())
            textureSampler.CreateInput('uv', Sdf.ValueTypeNames.Float2).ConnectToSource(uvReader, 'result')
            textureSampler.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
        
            pbrShader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).ConnectToSource(textureSampler, 'rgb')
            
            diffSet = True
            
    if not diffSet:
        dclr = Gf.Vec3f(shopshader.parmTuple('diffuseColor')[0].eval(), shopshader.parmTuple('diffuseColor')[1].eval(), shopshader.parmTuple('diffuseColor')[2].eval())
        pbrShader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(dclr)
        
    roughness = shopshader.parm('roughness').eval()
    metallic = shopshader.parm('metallic').eval()
    eclr = Gf.Vec3f(shopshader.parmTuple('emissiveColor')[0].eval(), shopshader.parmTuple('emissiveColor')[1].eval(), shopshader.parmTuple('emissiveColor')[2].eval())
    opacity = shopshader.parmTuple('opacity')[0].eval()
    ior = shopshader.parm('ior').eval()
    clearcoat = shopshader.parm('clearcoat').eval()
    clearroug = shopshader.parm('clearcoatRoughness').eval()
    occlusion = shopshader.parm('occlusion').eval()

    pbrShader.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(roughness)
    pbrShader.CreateInput('metallic', Sdf.ValueTypeNames.Float).Set(metallic)
    pbrShader.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f).Set(eclr)
    pbrShader.CreateInput('opacity', Sdf.ValueTypeNames.Float).Set(opacity)
    pbrShader.CreateInput('ior', Sdf.ValueTypeNames.Float).Set(ior)
    pbrShader.CreateInput('clearcoat', Sdf.ValueTypeNames.Float).Set(clearcoat)
    pbrShader.CreateInput('clearcoatRoughness', Sdf.ValueTypeNames.Float).Set(clearroug)
    pbrShader.CreateInput('occlusion', Sdf.ValueTypeNames.Float).Set(occlusion)
    
    material.CreateSurfaceOutput().ConnectToSource(pbrShader, 'surface')

    return
    
def editMaterial(stage, matpath, dclr, roughness, metallic):
    
    #material = stage.GetPrimAtPath(matpath)
    material = UsdShade.Material.Get(stage, matpath)
    pbrShader = UsdShade.Shader.Define(stage, matpath + '/PBRShader')
    pbrShader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(dclr)
    pbrShader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
    pbrShader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(metallic)
    pbrShader.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).Set(eclr)
    pbrShader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(opacity)
    pbrShader.CreateInput("ior", Sdf.ValueTypeNames.Float).Set(ior)
    pbrShader.CreateInput("clearcoat", Sdf.ValueTypeNames.Float).Set(clearcoat)
    pbrShader.CreateInput("clearcoatRoughness", Sdf.ValueTypeNames.Float).Set(clearroug)

    material.CreateSurfaceOutput().ConnectToSource(pbrShader, "surface")
    

def bindMaterial(stage, geopath, matpath):
    geo = stage.GetPrimAtPath(geopath)
    material = UsdShade.Material.Get(stage, matpath)
    UsdShade.MaterialBindingAPI(geo).Bind(material)

# As a post script after a USD ROP this will write shading information to the usda and
# then delete it leaving you with a clean usdz
def write_preview_shading():
    geoPaths = []
    this = hou.node('../')
    rObj = hou.node(this.parm('obj').eval())
    pxrMatPaths = []

    rawDir = rObj.parm('model_dir').eval()
    rawFile = rObj.parm('model_file').eval()
        
    if(rawFile != None):
        filename = rawDir +'usd/' + rawFile
        # we get all the unique paths as these are the prim paths in our USD file
        # if we find a unique path we also try to grab the shopmaterialpath, we'll
        # create and bind materials from these
        packNode = this.node('PACK_FOR_SHADERS')
        
        for prim in packNode.geometry().prims():
            gpath = prim.attribValue('path')
            if gpath is not '':
                if gpath not in geoPaths:
                    gmat = prim.attribValue('shop_materialpath')
                    geoPaths.append((gpath,gmat))
        
        # now we follow the material links building up shaders, if we've already built
        # the shader then we bind the existing one
        stage = Usd.Stage.Open(filename + '.usda')
        for gpath in geoPaths:
            matName = gpath[1].rsplit('/')[-1]
            if matName is not '':
                sshader = hou.node(gpath[1])
                
                if sshader:        
                    matPath = '/Materials/' + matName
                    if matPath not in pxrMatPaths:
                        pxrMatPaths.append(matPath)
                        #newMaterial(shopShader, stage, matPath, Gf.Vec3f(0.73938,0.742392,0.72749), 0.336918, 0)
                        newMaterialViaShop(sshader, stage, matPath)
                        bindMaterial(stage, gpath[0], matPath)
                    else:
                        bindMaterial(stage, gpath[0], matPath)
        
        #editMaterial(stage, '/Materials/white_veneer')        

    # CreateNewARKitUsdzPackage works with relative pathing, so we need to change our directory path to
    # the exported shaded usd path to sucessfully pull this together
    stage.Export(filename + '.usda')
    os.chdir(rawDir + '/usd')
    UsdUtils.CreateNewARKitUsdzPackage(rawFile + '.usda', rawFile + '.usdz')
    os.remove(rawFile + '.usda')