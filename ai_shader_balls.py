import hou

# creates two shader balls at the origin with a size of 14 cm, one has a 50% grey materials and the other has a mirror chrome

shaderBallsNode = hou.node('/obj').createNode('geo', 'shader_balls')
shaderBallsNode.children()[0].destroy() # file node

cBall = shaderBallsNode.createNode('sphere', 'chrome_ball')
cBall.parmTuple('rad').set((.14,.14,.14))
gBall = shaderBallsNode.createNode('sphere', 'grey_ball')
gBall.parmTuple('rad').set((.14,.14,.14))

merge = shaderBallsNode.createNode('merge')

xform = shaderBallsNode.createNode('xform')
xform.parm('tx').set(-.19)
xform.setFirstInput(cBall)

matassign = shaderBallsNode.createNode('material')
matassign.parm('shop_materialpath1').set('../materials/chrome_arn_mat')
matassign.setFirstInput(xform)

merge.setFirstInput(matassign)

xform = shaderBallsNode.createNode('xform')
xform.parm('tx').set(.19)
xform.setFirstInput(gBall)

matassign = shaderBallsNode.createNode('material')
matassign.parm('shop_materialpath1').set('../materials/grey_arn_mat')
matassign.setFirstInput(xform)

merge.setNextInput(matassign)

merge.setDisplayFlag(True)
merge.setRenderFlag(True)

matNode = shaderBallsNode.createNode('shopnet', 'materials')

cmat = matNode.createNode('arnold_vopnet', 'chrome_arn_mat')
sshader = cmat.createNode('arnold::standard_surface')
sshader.parm('base').set(0)
sshader.parm('specular').set(1)
sshader.parm('specular_roughness').set(0)
cmat.children()[0].setFirstInput(sshader)
cmat.layoutChildren()

gmat = matNode.createNode('arnold_vopnet', 'grey_arn_mat')
sshader = gmat.createNode('arnold::standard_surface')
sshader.parm('base').set(1)
sshader.parmTuple('base_color').set((.5,.5,.5))
sshader.parm('specular').set(0)
gmat.children()[0].setFirstInput(sshader)
gmat.layoutChildren()

matNode.layoutChildren()

shaderBallsNode.layoutChildren()
