import GetAnnotationsRemoveExtraneousInfo
import GetListOfSkIDAndAnnotations
import GetGF1Connectivity
import getSkeletonNodesNew
import requests
import jsonNeurons
import json
import config
import requests
import itertools

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id

# import NeuronSet as NS
# LC6 = NS.buildSingleCell(3123735)

class NeuronSet(object):

    def __init__(self, skeletonid):
        self.skeletonID = skeletonid
        self.synapseCount = self._syncount()
        self.neuronName = ''
        self.soma = None
        self.skeletonNodes = None
        self.connectorIDs = None
        self.connectorInfo = None


    def getSomaNode(self):
        self.soma = getSkeletonNodesNew.getSoma(self)
        return self.soma

    def getSkeletonNodes(self):
        self.skeletonNodes = getAllNodes(self)
        return self.skeletonNodes

    def getsynapseCount(self):
        return self.synapseCount

    def getConnectorIDs(self, polarity = 'presynaptic'):
        self.connectorIDs = getAllConnectors(skeletonID=self.skeletonID, polarity=polarity)
        return self.connectorIDs

    def getConnectorInfo(self, polarity = 'presynaptic'):
        self.connectorInfo = getAllConnectorInfo(skeletonID=self.skeletonID, polarity=polarity)
        return self.connectorInfo


    def _syncount(self):
        curSyn = 0
        for item in self:
            curSyn += item.syncount
        return curSyn



def getAllConnectors(skeletonID, polarity=None):
    if polarity is None:
        polarity = 'presynaptic'
    else:
        polarity = polarity
    connectorInfo = getAllConnectorInfo(skeletonID, polarity)

    myConnectors = {}
    myConnectorIDs = []
    # myConnectorCoordinates = []
    for item in connectorInfo['links']:
        # myConnectorIDs.append(item[1:5])
        myConnectors[item[1]] = item[2:5]
    # myConnectors['connectorID'] = myConnectorIDs

    return myConnectors

def getAllConnectorInfo(skeletonID=None, polarity=None):
    if skeletonID is None:
        mySkid = 4947529
    else:
        mySkid = skeletonID
    if polarity is None:
        relation_type = 'postsynaptic'
    else:
        relation_type = polarity

    # gets connector ID for all nodes in given skeleton (output: {links:[[skleton ID, Connector ID, X, Y, Z, Confidence, User ID, TNID, Date Created, Date Modified]], tags:[...]
    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/connectors/links/?skeleton_ids[0]={}&relation_type={}_to&with_tags=true'.format(
            project_id, mySkid, relation_type)  # ,
        # auth = auth,
        # data = {'skeleton_ids' : mySkid, 'relation_type' : 'postsynaptic_to'}
    )
    connectorInfo = json.loads(response.content)
    # print(connectorInfo)
    return connectorInfo

def getAllNodes(myNeuron):
    mySkid = myNeuron.skeletonID
    # mySkids = GAREI.getListOfSkID_int()

    # mySkid=str(mySkids[0])
    # mySkid = 4947529

    mySkid = str(mySkid)

    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/{}/compact-detail'.format(project_id, mySkid),
        auth=auth  # ,
        # data = {'skeleton_id' : mySkid}
    )

    skelInfo = json.loads(response.content)
    skelInfo = skelInfo[0]
    myCoordinates = {}
    # myCoordinates = []
    for i in skelInfo:
        # myNode = [i[3], i[4], i[5]]
        myCoordinates[i[1]] = [i[3], i[4], i[5]]

    # return newList
    return myCoordinates


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


def getLookUpTable():

    object_ids = [134]
    created_by = [134]
    annotated_with = [863792]

    headers = config.CatmaidApiTokenAuth(token)
    allAnnotations = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/'.format(project_id),
            auth = auth
    )
    someData = json.loads(allAnnotations.content)

    #print(someData)
    AnnotationLookUpTable = {}
    AnnotationLookUpTable = someData["annotations"]

    myLookUpTable = {}

    for d in AnnotationLookUpTable:
        myLookUpTable[d['id']] = d['name']

    return myLookUpTable


def getAnnotationID(myAnnotation):
    c = getLookUpTable()
    for i in c:
        if c[i] == str(myAnnotation):
            return i
    return

def getAllSkeletonInfo(annotation=None, notAnnotation = None):
    if annotation is None:
        annotation = 2119645
    elif type(annotation) is not int:
        annotation = int(getAnnotationID(str(annotation)))
    else:
        annotation = annotation
    data = {'annotated_with': annotation}
    if notAnnotation is not None:
        if type(notAnnotation) is not int:
            notAnnotation = int(getAnnotationID(str(notAnnotation)))
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


def getLookUpTableSkID_Name(annotation=None, notAnnotation=None):
    relevantDict = getAllSkeletonInfo(annotation, notAnnotation)
    SkIDLookUpNeuronName = {}

    # returns dictionary containing SkID : neuron name pairs
    for d in relevantDict:

        if d["type"] == 'neuron':
            SkIDLookUpNeuronName[((d['skeleton_ids'])[0])] = d['name']

    return SkIDLookUpNeuronName


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


# calls function above and returns single list of ints, each of which is a skid
def getListOfSkID_int(annotation=None):
    aList = getListOfSkeletonIDs(annotation)
    aNewList = []
    for i in aList:
        aNewList.append(i[0])

    return aNewList


# calls function above and returns list containing only lists (of length 1) of single int, each of which is a SKID
def getListOfSkeletonIDs(annotation=None):
    relevantDict = getAllSkeletonInfo(annotation)
    SkidList = []

    for d in relevantDict:
        if d['type'] == 'neuron':
            SkidList.append(d['skeleton_ids'])

    return SkidList


def buildSingleCell(SKID):
    aCell = NeuronSet(SKID)

    # sets annotations based on SKID
    aCell.annotations = setAnnotationLookUpTable(SKID)

    aCell.neuronName = getName(SKID)

    aCell.synapseCount = 0

    return aCell



def builder(SKID=None):
    if SKID is None:
        # sets list of all skeleton IDs
        mySkels = getListOfSkID_int()

        for i in mySkels:
            mySkelIDs.append(int(i))

        myNeurons = []

        for i in mySkels:
            x = NeuronSet(i)
            myNeurons.append(x)

    else:
        SKID = int(SKID)
        myNeurons = []
        x = NeuronSet(SKID)
        myNeurons.append(x)


    return myNeurons