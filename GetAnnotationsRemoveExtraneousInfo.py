import config

# coding: utf-8

# In[6]:

#Corresponds to part 4?

import requests
import json
import itertools
import GetLookUpTable
    #This Code Works - returns Dictionary with each key being a skelID and each value being a list of their annotation IDs



token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id
object_ids = [134]
created_by = [134]
annotated_with = [863792]
#3169164 for postsynaptic to lc6
    
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

    myData = json.loads(response.content.decode('utf-8'))

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

    thisData = json.loads(newResponse.content.decode('utf-8'))

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

#annotation should be a string meta annotation
def queryByMetaAnnotation(annotation):
    #annotation = 'testMetaAnnotation'
    myAnnotationList = []
    if type(annotation) is not int:
        annotation = int(GetLookUpTable.getAnnotationID(str(annotation)))
    else:
        annotation = annotation

    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id),
        auth=auth,
        data={'annotated_with': annotation, 'with_annotations': True, 'types': ['neuron', 'annotation']}

    )

    myData = json.loads(response.content.decode('utf-8'))

    myInfo = myData['entities']

    #myInfo is a list of dicts with annotation id, name, and type as key, value pairs - this loop returns list of annotation names
    for i in myInfo:
        myAnnotationList.append(i['name'])

    return myAnnotationList

def continuedMetaAnnotation():
    '''
        myAnnotations = {}
        for i in myInfo:
            myAnnotations[i['id']] = i['name']

        myAnnotationIDs = list(myAnnotations.keys())
        myNeurons = {}
        for i in myAnnotationIDs:
            newResponse = requests.post(
                'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id),
                auth=auth,
                data={'annotated_with': myAnnotationIDs[i], 'with_annotations': True, 'types': ['neuron', 'annotation']}
            )
            myNewData = json.loads(newResponse.content)
            theseNeurons = myNewData['entities']
            #myNeurons[]
        return myNewData
        #myResults = myNewData['entities']
        #return myResults
    '''
    pass

#
def getMetaAnnotationList(mySet):
    '''

    :param mySet: obj of type GFIN_Set
    :return: myMetaAnnotationList: list of annotationsIds for all of GF1 input neuron meta annotations
    '''
    user = 134
    #annotation = 'testMetaAnnotation'
    mySkeletons = []
    for i in mySet:
        mySkeletons.append(i.skeletonID)
    myMetaAnnotationList = []

    metaTest = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeleton/annotationlist'.format(project_id),
        auth=auth,
        data={'metaannotations': 1, 'skeleton_ids[]': mySkeletons}
    )

    metaTestResults = json.loads(metaTest.content)

    myInfo= metaTestResults['metaannotations']

    #myMetaAnnotationList is a list of annotation id for all meta annotations
    for i in myInfo:
        for item in myInfo[i]['annotations']:
            myMetaAnnotationList.append(item['id'])
    return myMetaAnnotationList

def getAnnotationsByMeta(mySet, metaAnnotationList = None):
    '''

    :param mySet: obj of type GFIN_Set
    :param metaAnnotationList: array of int (meta annotation ids) - leave as none
    :return: myDict: dictionary in format - {'metaAnnotationName': {'annotations': [{'name', 'id', 'users':[]}]}}
    '''
    allAnnotations = GetLookUpTable.getLookUpTable()
    if metaAnnotationList is None:
        metaAnnotationList = getMetaAnnotationList(mySet)

    myDict = {}
    for i in metaAnnotationList:
        aResponse = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/annotations/',
            auth=auth,
            data={'annotates[]': i}
        )
        theData = json.loads(aResponse.content)
        if i in allAnnotations:
            annotationName = allAnnotations[i]
        myDict[annotationName] = theData


    return myDict

def getAllGFINannotations():
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/annotations/',
        auth=auth,
        data={'user_id': [134]}
    )

    ourAnnotations = json.loads(response.content)
    theAnnotations = ourAnnotations['annotations']
    ourGFannotations = []
    for i in theAnnotations:
        if 'CBR' in i['name']:
            ourGFannotations.append(i)


    results = []
    return results


#Visual Neurons = ['LC4', 'LC6', 'LPLC2', 'LPLC1', 'LPC1', 'LLPC1', 'LC28', 'DNp10_Input_cluster1', 'LLPC2', 'DNp10_input_cluster2', 'LPLC4', 'DNp10_input_cluster4', 'LPLC3']





