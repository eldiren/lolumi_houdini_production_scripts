# used in a hda, these functions allow you to get the properties for a ROPs based on parms
# from an HDA, this is useful in workflows involving use of multiple renderers, or use of one
# renderer that has multiple outputs and lighting setups for a specific asset

# normally used in the Scripts section of a digital asset as a PythonModule
# this script take render parameters and sets Arnold, Octane, Redshift, and Mantra
# ROPs based of the values, it then launches disk, IPR, or MPlay renders

def setRenderSettings(node):
    this = hou.node('.')
    rObj = hou.node(this.parm('obj').eval())
    renderer = this.parm('renderer').eval()

    if node:
        if renderer == 0: # mantra
            if(this.parm('bake_texture').eval()):
                bakeROP = hou.node('/obj/ropnet1/baketexture1')
                bakeROP.parm('camera').set(this.parm('render_cam').eval())
                bakeROP.parmTuple('vm_uvunwrapres')[0].set(rObj.parmTuple('res_override')[0].eval())
                bakeROP.parmTuple('vm_uvunwrapres')[1].set(rObj.parmTuple('res_override')[1].eval())
                bakeROP.parm('vm_uvobject1').set(this.path())
                bakeROP.parm('vobject').set(this.path())
                bakeROP.parm('alights').set(rObj.parm('alights').eval())
                bakeROP.parm('vm_uvoutputpicture1').set(rObj.parm('render_file').eval())
            else:
                mantraROP = hou.node('/obj/ropnet1/mantra1')
                mantraROP.parm('camera').set(rObj.parm('render_cam').eval())
                mantraROP.parm('override_camerares').set(1)
                mantraROP.parm('res_fraction').set('specific')
                mantraROP.parmTuple('res_override')[0].set(rObj.parmTuple('res_override')[0].eval())
                mantraROP.parmTuple('res_override')[1].set(rObj.parmTuple('res_override')[1].eval())
                mantraROP.parm('vobject').set(this.path())
                mantraROP.parm('alights').set(rObj.parm('alights').eval())
        elif renderer == 1: # octane
            if(rObj.parm('bake_texture').eval()):
                node.parm('HO_renderTarget').set(rObj.parm('oct_bake_path').eval())
            else:
                node.parm('HO_renderTarget').set(rObj.parm('oct_target_path').eval())
            
            node.parm('HO_img_fileName').set(rObj.parm('render_file').eval())
            node.parm('HO_renderCamera').set(rObj.parm('render_cam').eval())
            node.parm('HO_iprCamera').set(rObj.parm('render_cam').eval())
            node.parmTuple('HO_overrideRes')[0].set(rObj.parmTuple('res_override')[0].eval())
            node.parmTuple('HO_overrideRes')[1].set(rObj.parmTuple('res_override')[1].eval())
            node.parm('HO_overrideCameraRes').set(1)
            node.parm('HO_objects_force').set(this.path() + ' ' + rObj.parm('alights').eval())
        elif renderer == 2: # arnold
            pass
        elif renderer == 3: # redshift
            pass
    
        return True
    
    return False
    
def octaneIPR():
    octROP = hou.node('/obj/ropnet1/Octane_ROP')
    success = setRenderSettings(octROP)
    if success:
        octROP.parm('HO_IPR').pressButton()
        
def octaneToDisk():
    octROP = hou.node('/obj/ropnet1/Octane_ROP')
    success = setRenderSettings(octROP)
    if success:
        octROP.parm('HO_overrideCameraRes').set(0)
        octROP.parm('execute').pressButton() 

def mantraToDisk():
    this = hou.node('.')
    rObj = hou.node(this.parm('obj').eval())
    
    mantraROP = None
    if(rObj.parm('bake_texture').eval()):
        mantraROP = hou.node('/obj/ropnet1/baketexture1')
    else:
        mantraROP = hou.node('/obj/ropnet1/mantra1')
        
    success = setRenderSettings(mantraROP)
    if success:
        if(mantraROP.parm('override_camerares')):
            mantraROP.parm('override_camerares').set(0)
        mantraROP.parm('execute').pressButton() 
        
def mantraMPlay():
    this = hou.node('.')
    rObj = hou.node(this.parm('obj').eval())
    
    ROPNode = None
    if(rObj.parm('bake_texture').eval()):
        ROPNode = hou.node('/obj/ropnet1/baketexture1')
    else:
        ROPNode = hou.node('/obj/ropnet1/mantra1')
        
    if ROPNode:
        success = setRenderSettings(ROPNode)
        
        if success:
            ROPNode.parm('renderpreview').pressButton()

def mantraIPR():
    this = hou.node('.')
    rObj = hou.node(this.parm('obj').eval())
    
    ROPNode = None
    if(rObj.parm('bake_texture').eval()):
        ROPNode = hou.node('/obj/ropnet1/baketexture1')
    else:
        ROPNode = hou.node('/obj/ropnet1/mantra1')
        
    if ROPNode:
        success = setRenderSettings(ROPNode)
        
        if success:
            iprViewer = hou.ui.paneTabOfType(hou.paneTabType.IPRViewer)
            if(iprViewer):
                iprViewer.setRopNode(ROPNode)
                iprViewer.startRender()
            
def renderMPlay():
    this = hou.node('.')
    renderer = this.parm('renderer').eval()
    octROP = hou.node('/obj/ropnet1/Octane_ROP')
    
    if renderer == 0: # mantra
        mantraMPlay()
    elif renderer == 1: # octane
        octROP.parm('HO_renderToMPlay').set(1)
        octaneToDisk()
    elif renderer == 2: # arnold
        pass
    elif renderer == 3: # redshift
        pass

def renderIPR():
    this = hou.node('.')
    renderer = this.parm('renderer').eval()
    
    if renderer == 0: # mantra
        mantraIPR()
    elif renderer == 1: # octane
        octaneIPR()
    elif renderer == 2: # arnold
        pass
    elif renderer == 3: # redshift
        pass
        
def renderDisk():
    this = hou.node('.')
    octROP = hou.node('/obj/ropnet1/Octane_ROP')
    
    renderer = this.parm('renderer').eval()
    
    if renderer == 0: # mantra
        mantraToDisk()
    elif renderer == 1: # octane
        octROP.parm('HO_renderToMPlay').set(0)
        octaneToDisk()
    elif renderer == 2: # arnold
        pass
    elif renderer == 3: # redshift
        pass
        