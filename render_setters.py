# used in a hda, these functions allow you to get the properties for a ROPs based on parms
# from an HDA, this is useful in workflows involving use of multiple renderers, or use of one
# renderer that has multiple outputs and lighting setups for a specific asset

def setOctaneSettings(node):
    this = hou.node('.')
    
    if node:
        if(this.parm('bake_texture').eval()):
            node.parm('HO_renderTarget').set(this.parm('oct_bake_path').eval())
        else:
            node.parm('HO_renderTarget').set(this.parm('oct_target_path').eval())
        
        node.parm('HO_renderCamera').set(this.parm('render_cam').eval())
        node.parm('HO_iprCamera').set(this.parm('render_cam').eval())
        node.parmTuple('HO_overrideRes')[0].set(this.parmTuple('res_override')[0].eval())
        node.parmTuple('HO_overrideRes')[1].set(this.parmTuple('res_override')[1].eval())
        node.parm('HO_overrideCameraRes').set(1)
        node.parm('HO_objects_force').set(this.path() + ' ' + this.parm('alights').eval())
        node.parm('HO_img_fileName').set(this.parm('render_file').eval())
    
    return True
    
def octaneIPR():
    octROP = hou.node('/obj/ropnet1/Octane_ROP')
    success = setOctaneSettings(octROP)
    if success:
        octROP.parm('HO_IPR').pressButton()
        
def octaneRender():
    octROP = hou.node('/obj/ropnet1/Octane_ROP')
    success = setOctaneSettings(octROP)
    if success:
        octROP.parm('HO_overrideCameraRes').set(0)
        octROP.parm('HO_img_enable').set(1)
        
        octROP.parm('execute').pressButton()
        
def mantraMPlay():
    this = hou.node('.')
    
    if(this.parm('bake_texture').eval()):
        bakeROP = hou.node('/obj/ropnet1/baketexture1')
        bakeROP.parm('camera').set(this.parm('render_cam').eval())
        bakeROP.parmTuple('vm_uvunwrapres')[0].set(this.parmTuple('res_override')[0].eval())
        bakeROP.parmTuple('vm_uvunwrapres')[1].set(this.parmTuple('res_override')[1].eval())
        bakeROP.parm('vm_uvobject1').set(this.path())
        bakeROP.parm('vobject').set(this.path())
        bakeROP.parm('alights').set(this.parm('alights').eval())
        bakeROP.parm('vm_uvoutputpicture1').set(this.parm('render_file').eval())
        bakeROP.parm('renderpreview').pressButton()
    else:
        mantraROP = hou.node('/obj/ropnet1/mantra1')
        mantraROP.parm('camera').set(this.parm('render_cam').eval())
        mantraROP.parm('override_camerares').set(1)
        mantraROP.parm('res_fraction').set('specific')
        mantraROP.parmTuple('res_override')[0].set(this.parmTuple('res_override')[0].eval())
        mantraROP.parmTuple('res_override')[1].set(this.parmTuple('res_override')[1].eval())
        mantraROP.parm('vobject').set(this.path())
        mantraROP.parm('alights').set(this.parm('alights').eval())
        
        mantraROP.parm('renderpreview').pressButton() 