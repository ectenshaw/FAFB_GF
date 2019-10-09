'''anteriorDict = {}
lateralDict = {}
medialDict = {}
for obj in bpy.data.scenes['Scene'].objects:
    if obj.layers[1] == True:
        anteriorDict[obj] = obj
for obj in bpy.data.scenes['Scene'].objects:
    if obj.layers[2] == True:
        if obj not in anteriorDict:
            lateralDict[obj] = obj
for obj in bpy.data.scenes['Scene'].objects:
    if obj.layers[3] == True:
        if (obj not in anteriorDict and obj not in lateralDict):
            lateralDict[obj] = obj'''


'''neuronDict = {}
for obj in bpy.data.scenes['Scene'].objects:
    if obj.layers[1] == True:
        neuronDict[obj] = 'anterior'
    elif obj.layers[2] == True:
        neuronDict[obj] = 'lateral'
    elif obj.layers[3] == True:
        neuronDict[obj] = 'medial'
    elif obj.layers[4] == True:
        neuronDict[obj] = 'somaTract'


for i in neuronDict:
    if neuronDict[i] == 'anterior':
        i.layers[1] = True
        i.layers[2] = False
        i.layers[3] = False
        i.layers[4] = False
    if neuronDict[i] == 'lateral':
        i.layers[1] = False
        i.layers[2] = True
        i.layers[3] = False
        i.layers[4] = False
    if neuronDict[i] == 'medial':
        i.layers[1] = False
        i.layers[2] = False
        i.layers[3] = True
        i.layers[4] = False
    if neuronDict[i] == 'somaTract':
        i.layers[1] = False
        i.layers[2] = False
        i.layers[3] = False
        i.layers[4] = True


myObjects = bpy.data.scenes['Scene'].objects
count = 1
for i in myObjects:
    if i[0:10] == myObjects[count][0:10]:
        myObjects[count].layers[2] = False
    count +=1
    if count == len(myObjects-1):
        break'''

for obj in bpy.data.scenes['Scene'].objects:
    if '.000' in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)