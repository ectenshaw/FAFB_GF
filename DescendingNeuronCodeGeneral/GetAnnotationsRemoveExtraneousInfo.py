
# coding: utf-8

# In[6]:

#Corresponds to part 4?

import requests
import json
import itertools
import GetLookUpTable
import config
    #This Code Works - returns Dictionary with each key being a skelID and each value being a list of their annotation IDs



token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id
object_ids = [134]
created_by = [134]
annotated_with = [863792]    



#returns Dictionary containing: SkID, neuron name, type, and neuron ID
def getAllSkeletonInfo(annotation = None):
    if annotation is None:
        annotation = 863792
    elif type(annotation) is not int:
        annotation = int(GetLookUpTable.getAnnotationID(str(annotation)))
    else:
        annotation = annotation
        
    response = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id), 
            auth = auth,
            data={'annotated_with': annotation}

    )

    myData = json.loads(response.content)

    relevantDict = {}
    relevantDict = myData['entities']
    
    return relevantDict
    
    
#calls function above and returns list containing only lists (of length 1) of single int, each of which is a SKID
def getListOfSkeletonIDs(annotation = None):
    
    relevantDict = getAllSkeletonInfo(annotation)
    SkidList = []


    for d in relevantDict:
        if d['type'] == 'neuron':
            SkidList.append(d['skeleton_ids'])
            
    return SkidList

#calls function above and returns single list of ints, each of which is a skid
def getListOfSkID_int(annotation = None):
    aList = getListOfSkeletonIDs(annotation)
    aNewList = []
    for i in aList:
        aNewList.append(i[0])
        
    return aNewList
    
    
#returns dictionary with each key being a skelID and each value being a list of their annotation IDs   
def getDictOfNeuronsWithIDs():

    SkidList = getListOfSkeletonIDs()

    newResponse = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id), 
            auth = auth,
            data={'skeleton_ids': SkidList}
    )
    #print(type(newResponse))
    #print(newResponse.text)

    thisData = json.loads(newResponse.content)

    Annotations4ThisNeuron = {}
    myNeurons = {}
    myNeurons = thisData['skeletons']
    tempList = []

    #print(myNeurons)

    for i in myNeurons:
        for d in myNeurons[i]:
            tempList.append(d['id'])
        Annotations4ThisNeuron[i] = tempList
        tempList = []


    return Annotations4ThisNeuron


#returns dictionary with each key being a skelID and each value being a list of annotation Strings
def convertID2String():
    
    myDict = getDictOfNeuronsWithIDs()
    AnnotationLookUpTable = GetLookUpTable.getLookUpTable()
    myNewDict = {}
    ListOfAnnotations = []
    
    for i in myDict:
        for e in myDict[i]:
            ListOfAnnotations.append(AnnotationLookUpTable[e])
            #e = AnnotationLookUpTable[e]
            #print(e)
        myNewDict[i] = ListOfAnnotations
        ListOfAnnotations = []
            
    return myNewDict

#print(convertID2String())


def getLookUpTableSkID_Name(annotation = None):

    relevantDict = getAllSkeletonInfo(annotation)
    SkIDLookUpNeuronName = {}

    #returns dictionary containing SkID : neuron name pairs
    for d in relevantDict:

        if d["type"] == 'neuron':
            SkIDLookUpNeuronName[((d['skeleton_ids'])[0])] = d['name']
            
    return SkIDLookUpNeuronName


def setAnnotationLookUpTable(SKID):
   
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id),
        auth = auth,
        data={'skeleton_ids[0]': SKID}
    )
    myData = json.loads(response.content)
    myAnnotations = myData['annotations']
    
    
    a = []
    for i in myAnnotations:
        a.append(myAnnotations[i])
    return a

def getName(SKID):
    a = setAnnotationLookUpTable(SKID)
    b = str(a[0])
    
    c = getLookUpTableSkID_Name(b)
    myName = c[SKID]
    return myName

def getMyAnnotations():
    myNeuronswithAnnotations = convertID2String()

    return myNeuronswithAnnotations
    

