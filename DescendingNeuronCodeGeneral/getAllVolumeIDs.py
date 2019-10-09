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
    
    #relevantDict = myData['entities']

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
    for i in myVols:
        if '_R' not in i and '_L' not in i:
            del myVols[i]
    return myVols

    
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
        
        
    
