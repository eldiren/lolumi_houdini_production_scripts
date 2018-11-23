# creates a main and sub material node in the selected object's path using a file 
# that holds each material and the objects and groups assigned to it

# Grab the selected object
#print hou.selectedNodes() #debug
this = hou.selectedNodes()[-1]
prims = this.geometry().prims()

# open the file
fileName = hou.ui.selectFile(None, "Select assignment file...", False, hou.fileType.Any, "*.txt")
fileName = hou.expandString(fileName) #string might contain a variable, we should expand it
f = open(fileName, 'r')

# the first line is the number of materials
line = f.readline()
maxMats = int(line)

parent = hou.node(this.parent().path())

mmat = parent.createNode('material', 'main_material')
smat = parent.createNode('material', 'sub_material')

# each line after is a material name and amount of objects followed by 
# names of the objects associated with it
line = f.readline()

idx = 1
objMatCnt = 0
subMatCnt = 0
    
while line:
    matname, objcntstr, grpcntstr = line.split(',')
    print "---" + matname + "|" + objcntstr + "|" + grpcntstr #debug
    
    objcnt = int(objcntstr)
    grpcnt = int(grpcntstr)
    
    # let's work on the main materials
    if objcnt > 0:
        objMatCnt = objMatCnt + 1
        mmat.parm('num_materials').set(objMatCnt)
    
        mmat.parm('shop_materialpath' + str(objMatCnt)).set("/shop/" + matname)
        print "shoppath: " + "/shop/" + matname
    
        grp_prims = ""
        for i in range(objcnt):
        
            line = f.readline()
            line = line.rstrip('\n')
            print "----Assigned object: " + line
            
            # line is going to be the object name, we need to find out what prim this
            # name is equal to
            for prim in prims:
                path = prim.stringAttribValue('path')
                if path.find(line) != -1:
                    print "-----Prim id: " + str(prim.number())
                    grp_prims = grp_prims + str(prim.number()) + " "
    
        # set group equal to the found prims
        mmat.parm('group' + str(objMatCnt)).set(grp_prims)
        print "----Prims groups: " + grp_prims
    
    # next lets read the groups, they get placed in the sub materials
    if grpcnt > 0:
        subMatCnt = subMatCnt + 1
        smat.parm('num_materials').set(subMatCnt)
    
        smat.parm('shop_materialpath' + str(subMatCnt)).set("/shop/" + matname)
        print "shoppath: " + "/shop/" + matname
        
        assign_grps = ""
        for i in range(grpcnt):
            line = f.readline()
            line = line.rstrip('\n')
            
            assign_grps = assign_grps + line + " "
        
        # set group equal to the found assignment groups
        smat.parm('group' + str(subMatCnt)).set(assign_grps)
        print "----Assigned groups: " + assign_grps
        
    idx = idx + 1
    line = f.readline()