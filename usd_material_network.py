# Place this as a python script in a shelf tool and if your in a Material Library this
# Will create a Collect node with all the currently support hydra delegate shaders
# attached, ready for shading

def check_type(type): 
    for ntype in hou.vopNodeTypeCategory().nodeTypes().keys(): 
        if type == ntype: 
            return True 
            
    return False 
    
qpath = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.TreeView).pwd().path()

cat = str( hou.node(qpath).childTypeCategory() )
category = cat.split(' ')[-1].replace('>', '')

print category
if category == 'Vop':
    con = hou.node(qpath)
    collect = con.createNode('collect', 'newmat')
    
    if check_type('arnold_materialbuilder'):
        sub_con = con.createNode('arnold_materialbuilder')
        sub_con.setGenericFlag(hou.nodeFlag.Material, False)
        collect.setNextInput(sub_con)
        
        out = sub_con.children()[0]
        r_mat = sub_con.createNode('arnold::standard_surface')
        out.setInput( 0, r_mat, 0 )
    
        r_mat.setCurrent(True, clear_all_selected=True)
        sub_con.layoutChildren()
    
    if check_type('redshift_usd_material'):
        sub_con = con.createNode('redshift_usd_material')
        sub_con.setGenericFlag(hou.nodeFlag.Material, False)
        collect.setNextInput(sub_con)
    
        r_mat = con.createNode('redshift::Material')
        r_mat.setGenericFlag(hou.nodeFlag.Material, False)
        sub_con.setInput( 0, r_mat, 0 )
    
        r_mat.setCurrent(True, clear_all_selected=True)
    
    if check_type('pxrdisney'):
        sub_con = con.createNode('pxrdisney')
        sub_con.setGenericFlag(hou.nodeFlag.Material, False)
        collect.setNextInput(sub_con)
    
    sub_con = con.createNode('usdpreviewsurface')
    sub_con.setGenericFlag(hou.nodeFlag.Material, False)
    collect.setNextInput(sub_con)
    
    sub_con = con.createNode('principledshader::2.0')
    sub_con.setGenericFlag(hou.nodeFlag.Material, False)
    collect.setNextInput(sub_con)
    
    con.layoutChildren()