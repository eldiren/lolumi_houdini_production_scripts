import os, sys, ctypes, string, getopt, glob

import hou
from arnold import *

import htoa
from htoa.universe import HaUniverse
from htoa.node.node import pullHouParms, houdiniParmGet, arnoldParmSet
from htoa.node.parms import *

rop_node = hou.node('/obj').createNode('ropnet', 'std_render_settings')

shop_node = rop_node.createNode('shopnet', 'aovs')

ar_aovs = shop_node.createNode('arnold_vopnet', 'arnold_aovs')
ar_aovs.children()[0].destroy() # arnold vopnet come with an OUT_material by defualt

out_aov = ar_aovs.createNode('arnold_aov', 'OUT_aov')
crypto_node = ar_aovs.createNode('arnold::cryptomatte', 'cryptomatte')
out_aov.setFirstInput(crypto_node)
ar_aovs.layoutChildren()

arn_test_node = rop_node.createNode('arnold', 'arnold_test')
arn_test_node.parm('camera').set('/obj/view_cam')
arn_test_node.parm('ar_bucket_size').set(16)
arn_test_node.parm('ar_force_threads').set(1)
arn_test_node.parm('ar_threads').set(-3)
arn_test_node.parm('ar_aov_shaders').set('../aovs/arnold_aovs')

arn_final_node = rop_node.createNode('arnold', 'arnold_final')
arn_final_node.parm('ar_aov_shaders').set('../aovs/arnold_aovs')
arn_final_node.parm('ar_progressive').set(0)
arn_final_node.parm('ar_force_threads').set(1)
arn_final_node.parm('ar_threads').set(-3)
arn_final_node.parm('ar_aovs').set(16)
arn_final_node.parm('ar_aov_label1').set('crypto_asset')
arn_final_node.parm('ar_aov_label2').set('crypto_object')
arn_final_node.parm('ar_aov_label3').set('crypto_material')
arn_final_node.parm('ar_aov_label4').set('diffuse_direct')
arn_final_node.parm('ar_aov_label5').set('diffuse_indirect')
arn_final_node.parm('ar_aov_label6').set('specular_direct')
arn_final_node.parm('ar_aov_label7').set('specular_indirect')
arn_final_node.parm('ar_aov_label8').set('transmission_direct')
arn_final_node.parm('ar_aov_label9').set('transmission_indirect')
arn_final_node.parm('ar_aov_label10').set('transmission_indirect')
arn_final_node.parm('ar_aov_label11').set('sss_direct')
arn_final_node.parm('ar_aov_label12').set('sss_indirect')
arn_final_node.parm('ar_aov_label13').set('volume_direct')
arn_final_node.parm('ar_aov_label14').set('volume_indirect')
arn_final_node.parm('ar_aov_label15').set('volume_opacity')
arn_final_node.parm('ar_aov_label16').set('Z')

rs_rop_final_node = rop_node.createNode('Redshift_ROP', 'rs_rop')
rs_rop_final_node.parm('RS_renderCamera').set('/obj/view_cam')

rs_ipr_final_node = rop_node.createNode('Redshift_IPR', 'rs_ipr')

rop_node.layoutChildren()