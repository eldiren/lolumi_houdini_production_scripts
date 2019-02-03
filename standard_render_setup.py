# this script creates cameras, lights, rops, targets, and aovs for Arnold, 
# Redshift, Mantra, and Octane if they are installed for quick start on rendering 
# a scene, best place to put it is in a shelf tool

import os, sys, ctypes, string, getopt, glob

import hou
from arnold import *

import htoa
from htoa.universe import HaUniverse
from htoa.node.node import pullHouParms, houdiniParmGet, arnoldParmSet
from htoa.node.parms import *

def check_type(type):
    for ntype in hou.ropNodeTypeCategory().nodeTypes().keys():
        if type == ntype:
            return True
            
    return False

vcam_node = hou.node('/obj/view_cam')
if not vcam_node:
    vcam_node = hou.node('/obj').createNode('cam', 'view_cam')
    hou.parmTuple('/obj/view_cam/res')[0].set(640)
    hou.parmTuple('/obj/view_cam/res')[1].set(360)

rop_node = hou.node('/obj/std_render_settings')

if not rop_node:
    rop_node = hou.node('/obj').createNode('ropnet', 'std_render_settings')

shop_node = hou.node('/obj/aovs_targets')
if not shop_node:
    shop_node = rop_node.createNode('shopnet', 'aovs_targets')

if(check_type('Octane_ROP')): # check if octane rop exists
    oct_rt = shop_node.createNode('octane_rendertarget_dl', 'octane_rendertarget')
    oct_rt.parm('parmEnvironment').set(1)
    
    oct_rop = rop_node.createNode('Octane_ROP', 'Octane')
    oct_rop.parm('HO_renderTarget').set('/obj/std_render_settings/aovs_targets/octane_rendertarget')
    oct_rop.parm('HO_renderCamera').set('/obj/view_cam')
    oct_rop.parm('HO_iprCamera').set('/obj/view_cam')

if(check_type('arnold')): #check if arnold rop exists
    ar_envlight = hou.node('/obj').createNode('arnold_light', 'arn_env_light')
    ar_envlight.parm('ar_light_type').set(6) #skydome
    ar_envlight.parm('ar_light_color_type').set(1)

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

if(check_type('Redshift_ROP')): #check if Redshift rop exists    
    rs_rop_final_node = rop_node.createNode('Redshift_ROP', 'rs_rop')
    rs_rop_final_node.parm('RS_renderCamera').set('/obj/view_cam')
    
    rs_ipr_final_node = rop_node.createNode('Redshift_IPR', 'rs_ipr')

shop_node.layoutChildren()
rop_node.layoutChildren()
hou.node('/obj').layoutChildren()