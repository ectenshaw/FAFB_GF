import requests
import json
import itertools
import GetLookUpTable
    #This Code Works - returns Dictionary with each key being a skelID and each value being a list of their annotation IDs
import config



token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id


def getVolumeIDs():
    response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/volumes/'.format(project_id), 
            auth = auth
    )

    myData = json.loads(response.content)

    volumeDict = {}
    
    for i in myData:
        currentName = i['name']
        currentID = i['id']
        volumeDict[currentID] = currentName
    return volumeDict

def getCondensedVolumeDict():
    volumeDict = getVolumeIDs()
    condensedVolumeDict={}
    
    for x in volumeDict:
        if 'v14' not in volumeDict[x]:
            if '_R' in volumeDict[x] or '_L' in volumeDict[x]:
                condensedVolumeDict[volumeDict[x]] = x
    
    
    return condensedVolumeDict


#returns list of strings of VOLume ids
def getVolumeIDintList():
    myVols = getVolumeIDs()
    volList = list(myVols.values())
    return volList

def getVolumeStringList():
    myVols = getVolumeIDs()
    volList = list(myVols.keys())
    return volList


#return dictionary containing only ITO nomenclature neuropils (with 1 of each neuropil)
def filterVolumes():
    myVols = getVolumeIDs()
    myVols = neuropilLookUp(myVols)
    filteredVols = {}
    for i in myVols:
        #if ('_R' in i or '_L' in i) and (len(i) <= 10) and ('v14' not in i):
        if ('_R' in i or '_L' in i or len(i)<5) and (len(i)<=10) and not('v14' in i):
            filteredVols[i] = myVols[i]
    return filteredVols

#reverse above dictionary, so as to have a means to look up neuropil name based upon volume id
def neuropilLookUp(myDict = None):
    if myDict is None:
        myDict = filterVolumes()
    myLookUp = {v: k for k, v in myDict.items()}
    return myLookUp


#returns list of int of VOLume ids
def getFilteredVolumeIDList():
    myVols = filterVolumes()
    volList = list(myVols.values())
    return volList

#returns dictionary with volume IDs as keys and min/max x,y,z as values ({'max': {'x': 349868.054, 'y': 286977.5893, 'z': 162232.8238}, 'min': {'x': 323114.8215, 'y': 255270.7114, 'z': 142607.9776}}
def getAllVolumeBoundaries():
    myVolumes = getFilteredVolumeIDList()
    myBounds = {}
    for i in myVolumes:

        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/volumes/{}'.format(project_id, i),
            auth=auth
        )
        myData = json.loads(response.content)
        tempBound = myData['bbox']
        myBounds[i] = tempBound
    return myBounds





#input should be a volume name with either _R or _L to specify hemisphere    
def getVolumeBoundary(volume):
    volList = getVolumeIDs()
    if '_R' not in volume and '_L' not in volume:
        volume += '_R'              #defaults to right hemisphere volume if not specified
    myVolID = volList[volume]
    response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/volumes/{}/'.format(myVolID), 
            auth = auth
    )

    myData = json.loads(response.content)
    return myData
    
    
    
#def getVolumeBoundaries():
 #   myVolumes = getVolumeIDs()
    
  #  myVolumeIDs = myVolumes.keys()
   # myBoundDict = {}
    
    
    #for i in myVolumeIDs:
     #   r = requests.get(
      #          'https://neuropil.janelia.org/tracing/fafb/v14/{}/volumes/{}/'.format(project_id, i), 
       #         auth = auth
        #)        
        
        
      
        #newData = json.loads(r.content)
        #thisBound = response['bbox']
    
        #myBoundDict[i] = thisBound
        
    
    #return myBoundDict
        
        
def getVolumePoints(volume_id):
    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/volume_detail'.format(project_id),
        auth=auth,
        data = (volume_id)
    )
    myData = json.loads(response.content)
    return myData

import numpy as np
def intersectPointVolume(volume_id, skeletonPoints):
    x = np.double(skeletonPoints[0])
    y = np.double(skeletonPoints[1])
    z = np.double(skeletonPoints[2])
    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/volumes/{}/intersect'.format(project_id, volume_id),
        auth=auth,
        data = { 'x': x, 'y': y, 'z': z}
    )
    myData = json.loads(response.content)
    return myData

