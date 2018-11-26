# These functions (light_rig_importer(), light_rig_exporter()) are normally attached to buttons in a digital asset
# most of the functionality here locally references parms in this digital asset for that reason, it's extracted
# here purely for archival, and ease of editing purposes.

import hou, json

def set_transform(light):
    hmatrix = hou.Matrix4()
    hmatrix.setAt(0, 0, light['matrix'][0]) 
    hmatrix.setAt(0, 1, light['matrix'][1])
    hmatrix.setAt(0, 2, light['matrix'][2])
    hmatrix.setAt(0, 3, light['matrix'][3])
    hmatrix.setAt(1, 0, light['matrix'][4])
    hmatrix.setAt(1, 1, light['matrix'][5])
    hmatrix.setAt(1, 2, light['matrix'][6])
    hmatrix.setAt(1, 3, light['matrix'][7])
    hmatrix.setAt(2, 0, light['matrix'][8])
    hmatrix.setAt(2, 1, light['matrix'][9])
    hmatrix.setAt(2, 2, light['matrix'][10])
    hmatrix.setAt(2, 3, light['matrix'][11])
    hmatrix.setAt(3, 0, light['matrix'][12])
    hmatrix.setAt(3, 1, light['matrix'][13])
    hmatrix.setAt(3, 2, light['matrix'][14])
    hmatrix.setAt(3, 3, light['matrix'][15])
    
    return hmatrix
    
def light_rig_importer():
    fileName = hou.parm('file_dir_path').eval()

    rigName = fileName.rsplit('.', 1)
    rigName = rigName[0].split('/')[-1]
    import_node = hou.node("/obj").createNode("subnet", rigName + "_light_rig")
    
    f = open(fileName, 'r')
    
    data = json.load(f)  
    for lname in data:
        print lname
        light = data[lname]

        if(hou.parm('renderer').eval() == 0): # Arnold
            light_node = import_node.createNode("arnold_light", lname)
            light_node.parmTuple('ar_color').set((light['color'][0], light['color'][1], light['color'][2]))
            light_node.parm('ar_intensity').set(light['intensity'])
            light_node.parm('ar_normalize').set(light['normalize'])
            light_node.parm('ar_spread').set(light['spread'])
            light_node.parm('ar_soft_edge').set(light['soft_edge'])
            
            light_node.setWorldTransform(set_transform(light))
                
            if light['type'] == 'point':
                light_prefix = "ar_point_"
            elif light['type'] == 'spot':
                light_prefix = "ar_spot_"
            elif light['type'] == 'quad':
                light_node.parm('ar_light_type').set(3)
                light_node.parm('ar_quad_sizex').set(light['width'])
                light_node.parm('ar_quad_sizey').set(light['height'])
                light_node.parm('ar_quad_roundness').set(light['roundness'])
            elif light['type'] == 'disk':
                light_prefix = "ar_disk_"            
            elif light['type'] == 'cylinder':
                light_prefix = "ar_cylinder_"
            elif light['type'] == 'skydome':
                light_node.parm('ar_light_type').set(6)
                
                if light['use_texture']:
                    light_node.parm('ar_light_color_type').set('1')
                    light_node.parm('ar_format').set(light['format'])
                    light_node.parm('ar_light_color_texture').set(light['texture'])
                    #light_node.parm('').set(light[''])
                    
        elif(hou.parm('renderer').eval() == 1): # Redshift            
            light_node.setWorldTransform(set_transform(light))
            
        elif(hou.parm('renderer').eval() == 2): # Octane
            if light['type'] == 'skydome': # in houdini the environment is in shading
                lightShop = import_node.createNode('shopnet', 'sky')
                light_node = lightShop.createNode('octane_rendertarget_dl', 'octane_rendertarget_dl')
                
                if light_node:     
                    light_node.parmTuple('rotation')[0].set(light['rotation'][0])
                    light_node.parmTuple('rotation')[1].set(light['rotation'][1])
                    
                    if light['use_texture']:
                        light_node.parm('parmEnvironment').set(1)
                        light_node.parm('power3').set(light['intensity'])
                        light_node.parm('A_FILENAME').set(light['texture'])
                    
            else: # normal lights
                light_node = import_node.createNode("octane_light", lname)
                light_node.setWorldTransform(set_transform(light))
                light_node.parm('octane_objprop_cameraVis').set(0)
                light_node.parm('NT_EMIS_BLACKBODY1_normalize').set(light['normalize'])
                
                if light['type'] == 'quad':
                    if light['use_texture']:
                        light_node.parm('switch').set(1)
                        light_node.parm('emission_text_switcher_switch').set(1)
                        light_node.parm('NT_TEX_IMAGE1_A_FILENAME').set(light['texture'])             
                        light_node.parm('NT_EMIS_TEXTURE1_power').set(light['intensity'])
                    else:
                        light_node.parm('NT_EMIS_BLACKBODY1_power').set(light['intensity'])
            
    import_node.layoutChildren()
    
    f.close()
    
def light_rig_exporter():
    filePath = hou.parm('export_path').eval()
    paths = filePath.rsplit('.', 1)
    
    filePath = paths[0]
    
    f = open(filePath + '.json', 'w')
    
    objs = hou.parm('lights_export').eval().split(' ')
    
    data = {}
    print objs
    for objPath in objs:
        obj = hou.node(objPath)
        
        value = {}
        guiType = 0
        value['use_texture'] = 0
        
        #print obj.Geometry().intrinsicNames()
        value['matrix'] = obj.worldTransform().asTuple()        
        
        if obj.type().name() == 'arnold_light': # dealing with Arnold                
            if obj.parm('ar_light_type').eval() == 0:
                value['type'] = 'point'
                
                value['color'] = (obj[C4DAIP_POINT_LIGHT_COLOR].x, obj[C4DAIP_POINT_LIGHT_COLOR].y, obj[C4DAIP_POINT_LIGHT_COLOR].z)
                
                value['radius'] = obj[C4DAIP_POINT_LIGHT_RADIUS]
                value['normalize'] = obj[C4DAIP_POINT_LIGHT_NORMALIZE]
                value['intensity'] = obj[C4DAIP_POINT_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_POINT_LIGHT_EXPOSURE] 
            if obj.parm('ar_light_type').eval() == 2:
                value['type'] = 'spot'
                
                value['color'] = (obj[C4DAIP_POINT_LIGHT_COLOR].x, obj[C4DAIP_POINT_LIGHT_COLOR].y, obj[C4DAIP_POINT_LIGHT_COLOR].z)
                
                value['radius'] = obj[C4DAIP_POINT_LIGHT_RADIUS]
                value['normalize'] = obj[C4DAIP_POINT_LIGHT_NORMALIZE]
                value['intensity'] = obj[C4DAIP_POINT_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_POINT_LIGHT_EXPOSURE] 

            if obj.parm('ar_light_type').eval() == 3:
                value['type'] = 'quad'

                color, use_texture, texture = ReadShaderLinkGui(obj, C4DAIP_QUAD_LIGHT_COLOR)
               
                if use_texture:
                    value['use_texture'] = use_texture
                    value['texture'] = texture
                else:    
                    value['color'] = color
                
                value['intensity'] = obj[67722820] * 2 ** obj[1655166224] 
                value['normalize'] = obj[1502846298]
                value['width'] = obj[2034436501] * c4dScale
                value['height'] = obj[2120286158] * c4dScale
                value['roundness'] = obj[1641633270]
                value['soft_edge'] = obj[1632353189]
                value['spread'] = obj[1730825676]
            
            if obj.parm('ar_light_type').eval() == 4:
                value['type'] = 'disk'
                
                value['color'] = (obj[C4DAIP_POINT_LIGHT_COLOR].x, obj[C4DAIP_POINT_LIGHT_COLOR].y, obj[C4DAIP_POINT_LIGHT_COLOR].z)
                
                value['radius'] = obj[C4DAIP_POINT_LIGHT_RADIUS]
                value['normalize'] = obj[C4DAIP_POINT_LIGHT_NORMALIZE]
                value['intensity'] = obj[C4DAIP_POINT_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_POINT_LIGHT_EXPOSURE] 
                
            if obj.parm('ar_light_type').eval() == 5:
                value['type'] = 'cylinder'
                
                value['color'] = (obj[C4DAIP_POINT_LIGHT_COLOR].x, obj[C4DAIP_POINT_LIGHT_COLOR].y, obj[C4DAIP_POINT_LIGHT_COLOR].z)
                
                value['radius'] = obj[C4DAIP_POINT_LIGHT_RADIUS]
                value['normalize'] = obj[C4DAIP_POINT_LIGHT_NORMALIZE]
                value['intensity'] = obj[C4DAIP_POINT_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_POINT_LIGHT_EXPOSURE] 

            if obj.parm('ar_light_type').eval() == 6:
                value['type'] = 'skydome'
                
                color, use_texture, texture = ReadShaderLinkGui(obj, C4DAIP_SKYDOME_LIGHT_COLOR)
               
                if use_texture:
                    value['use_texture'] = use_texture
                    value['texture'] = texture
                else:    
                    value['color'] = color
                    
                value['format'] = obj[C4DAIP_SKYDOME_LIGHT_FORMAT]
                value['intensity'] = obj[C4DAIP_SKYDOME_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_SKYDOME_LIGHT_EXPOSURE] 
                value['normalize'] = obj[C4DAIP_SKYDOME_LIGHT_NORMALIZE]                   

            data[obj.name()] = value
            
        if obj.type().name() == 'rslight': # dealing with Redshift
            if obj.parm('light_type').eval() == 0:
                value['type'] = 'distant'
                
                value['color'] = (obj.parmTuple('light_color')[0], obj.parmTuple('light_color')[1], obj.parmTuple('light_color')[2])
                
                value['normalize'] = 0
                value['intensity'] = obj.parm('RSL_intensityMultiplier') 
            if obj.parm('light_type').eval() == 1:
                value['type'] = 'point'
                
                value['color'] = (obj.parmTuple('light_color')[0], obj.parmTuple('light_color')[1], obj.parmTuple('light_color')[2])
                
                value['radius'] = 1
                value['normalize'] = 0
                value['intensity'] = obj.parm('RSL_intensityMultiplier')  

            if obj.parm('light_type').eval() == 2:
                value['type'] = 'spot'
                
                value['color'] = (obj.parmTuple('light_color')[0], obj.parmTuple('light_color')[1], obj.parmTuple('light_color')[2])
                
                value['radius'] = obj[C4DAIP_POINT_LIGHT_RADIUS]
                value['normalize'] = obj[C4DAIP_POINT_LIGHT_NORMALIZE]
                value['intensity'] = obj[C4DAIP_POINT_LIGHT_INTENSITY] * 2 ** obj[C4DAIP_POINT_LIGHT_EXPOSURE] 

            if obj.parm('light_type').eval() == 3:
                # Redshift area lights can have subtypes
                if obj.parm('RSL_areaShape').eval() == 0:
                    value['type'] = 'quad'
                        
                    if obj.parm('RSColorLayer1_layer1_enable').eval():
                        value['use_texture'] = 1
                        value['texture'] = obj.parm('TextureSampler1_tex0').eval()
                    else:    
                        value['color'] = (obj.parmTuple('light_color')[0].eval(), obj.parmTuple('light_color')[1].eval(), obj.parmTuple('light_color')[2].eval())
                    
                    value['intensity'] = obj.parm('RSL_intensityMultiplier').eval() 
                    value['normalize'] = obj.parm('RSL_normalize').eval()
                    value['width'] = obj.parmTuple('areasize')[0].eval()
                    value['height'] = obj.parmTuple('areasize')[1].eval()
                    value['roundness'] = 0
                    value['soft_edge'] = 0
                    value['spread'] = 1      
            
            data[obj.name()] = value
        
    json.dump(data, f, indent=2)
    
    f.close()