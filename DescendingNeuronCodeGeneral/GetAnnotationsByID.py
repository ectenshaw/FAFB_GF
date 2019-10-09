import requests
import json
import itertools
import GetLookUpTable
import config
#Returns Dictionary of SKID keys and annotation values


token = config.token
project_id = config.project_id
auth = config.CatmaidApiTokenAuth(token)

object_ids = [134]
created_by = [134]


def getAllSkeletonInfo(annotation=None, notAnnotation = None):
    if annotation is None:
        annotation = 2119645
    elif type(annotation) is not int:
        annotation = int(GetLookUpTable.getAnnotationID(str(annotation)))
    else:
        annotation = annotation
    data = {'annotated_with': annotation}
    if notAnnotation is not None:
        if type(notAnnotation) is not int:
            notAnnotation = int(GetLookUpTable.getAnnotationID(str(notAnnotation)))
        data['not_annotated_with'] = notAnnotation
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id),
        auth=auth,
        data=data

    )

    myData = json.loads(response.content)

    relevantDict = {}
    relevantDict = myData['entities']

    return relevantDict

#SKIDS should be a list of string SKIDS
def getMyAnnotationsStart(SKIDS):

    newResponse = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id),
            auth = auth,
            data={'skeleton_ids': SKIDS}
    )

    thisData = json.loads(newResponse.content)

    Annotations4ThisNeuron = {}
    myNeurons = {}
    myNeurons = thisData['skeletons']
    tempList = []

    # print(myNeurons)

    for i in myNeurons:
        for d in myNeurons[i]:
            tempList.append(d['id'])
        Annotations4ThisNeuron[i] = tempList
        tempList = []

    return Annotations4ThisNeuron


# returns dictionary with each key being a skelID and each value being a list of annotation Strings
def convertID2String(SKIDS):
    myDict = getMyAnnotationsStart(SKIDS)
    AnnotationLookUpTable = GetLookUpTable.getLookUpTable()
    myNewDict = {}
    ListOfAnnotations = []

    for i in myDict:
        for e in myDict[i]:
            ListOfAnnotations.append(AnnotationLookUpTable[e])
        myNewDict[i] = ListOfAnnotations
        ListOfAnnotations = []

    return myNewDict

def getLookUpTableSkID_Name(annotation=None, notAnnotation=None):
    relevantDict = getAllSkeletonInfo(annotation, notAnnotation)
    SkIDLookUpNeuronName = {}

    # returns dictionary containing SkID : neuron name pairs
    for d in relevantDict:

        if d["type"] == 'neuron':
            SkIDLookUpNeuronName[((d['skeleton_ids'])[0])] = d['name']

    return SkIDLookUpNeuronName


def setAnnotationLookUpTable(SKIDS):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id),
        auth=config.CatmaidApiTokenAuth(token),
        data={'skeleton_ids[0]': SKIDS}
    )
    myData = json.loads(response.content)
    myAnnotations = myData['annotations']

    a = []
    for i in myAnnotations:
        a.append(myAnnotations[i])
    return a


def getName(SKIDS):
    a = setAnnotationLookUpTable(SKIDS)
    b = str(a[0])

    c = getLookUpTableSkID_Name(b)
    d = getLookUpTableSkID_Name('CardLab-collaborating', notAnnotation='CardLab')
    #print(d)
    for i in d:
        c[i] = d[i]
    myName = c[SKIDS]
    return myName


def getMyAnnotations(SKIDS):
    myNeuronswithAnnotations = convertID2String(SKIDS)

    return myNeuronswithAnnotations

def getDNInfo(SKID):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id),
        auth=config.CatmaidApiTokenAuth(token),
        data={'skeleton_ids[0]': SKID}
    )
    myData = json.loads(response.content)
    myAnnotations = myData['annotations']

    a = []
    for i in myAnnotations:
        a.append(myAnnotations[i])
    return a

def getDNType(SKID):
    a = getDNInfo(SKID)
    for item in a:
        if 'putative DN' in item:
            myType = item
            return myType
    myType = None
    return myType

