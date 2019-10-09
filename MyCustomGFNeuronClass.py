
import requests
import json
import itertools
import GetLookUpTable
import GetAnnotationsRemoveExtraneousInfo
import GetListOfSkIDAndAnnotations
import GetGF1Connectivity
import getSkeletonNodesNew
import numpy as np
import config



class GFinputNeuron(object):
    """
    Custom object class for a single input neuron. This is called in the classSet builder. Most likely you won't have
    to do anything with this file, it becomes absolutely necessary to change the structure of the objects or if
    you  want to try to increase the efficiency/speed of building the instances
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    All of the attributes of the neuron object are listed below within init. Note that some of the attributes are
    automatically populated during the build, while others are typically populated by function calls to the
    customNeuronClassSet object. The decisions for which would be which were based upon speed, such that you don't
    always need all of the attributes and shouldn't have  to wait for some of the slower stuff to populate if you're not
    going to use it anyway.
    """

    def __init__(self, skeletonID):
        self.skeletonID = skeletonID
        self.GF1synapseCount = int()
        self.GF2synapseCount = int()
        self.annotations = []
        self.neuronName = ''
        self.percentTotalSynapse = 0       #total percent of GF1synapses
        self.percentCurrentGroup = 0       #percent of GF1synapses relative to other neurons in the current sub-group of GF1input neurons
        self.soma = None
        self.skeletonNodes = None
        self.classType = None
        #connectorIDs is all of this neuron's connectors, not just GFinput neurons, in order to get that info: run getAllGFINSynByBranch for the set and it will fill synLocation attribute
        self.connectorIDs = None
        self.numSynByBranch = None
        self.postsynapticToLC6 = 0
        self.postsynapticToLC4 = 0
        self.postsynapticToLPLC2 = 0
        self.postsynapticToLPLC1 = 0
        self.postsynapticToLPC1 = 0
        self.postsynapticToLC28 = 0
        self.postsynapticToLLPC1 = 0
        self.postsynapticToLPLC3 = 0
        self.postsynapticToJON = 0
        self.classification = None
        self.hemisphere = None
        self.numNodes = None
        self.synapsesByBranch = {}
        self.synLocation = {}
        self.GF1SynapticClusters = []
        self.quantile = None
        self.curColor = None
        self.subClusters = {'tempHolder': {'subCluster1': 0, 'subCluster2': 0, 'subCluster3': 0}}
        self.commissure = None
        self.cellBodyRind = None
        self.somaSide = None
        self.neuropils = {}
        self.distribution = None
        self.modality = None
        self.cluster = None
        self.groupNumber = None
        self.morphology = None

    
    def __repr__(self):
        return '{}'.format(self.neuronName)
    
    def __str__(self):
        return "{}: skeleton ID = {}, GF1 synapse count = {}, annotations = {} \n".format(self.neuronName, self.skeletonID, self.GF1synapseCount, self.annotations)

    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__") and 'percent' not in attr:
                yield attr
    '''
    def __getitem__(self, item):
        return self.item
    '''
    def getSkID(self):
        return self.skeletonID
    def getGF1synapse(self):
        return self.GF1synapseCount
    def getAnnotations(self):
        myAnnotations = GetListOfSkIDAndAnnotations.getMyAnnotations()
        y = self.skeletonID
        z = str(y)
        if z in myAnnotations:
            self.annotations = myAnnotations[z]
        return self.annotations
    def getNeuronName(self):
        y = self.skeletonID
        z = str(y)              
        myNames = GetAnnotationsRemoveExtraneousInfo.getLookUpTableSkID_Name()
        if y in myNames:
            self.neuronName = myNames[y]       
        return self.neuronName
    def getSomaNode(self):
        self.soma = getSkeletonNodesNew.getSoma(self)
        return self.soma
    def getSkeletonNodes(self):
        self.skeletonNodes = getSkeletonNodesNew.getAllNodes(self)
        return self.skeletonNodes

    #returns a dict with keys as connectorIDs and values as x,y,z coordinate points
    def getConnectorIDs(self):
        self.connectorIDs = getSkeletonNodesNew.getAllConnectors(skeletonID = self.skeletonID, polarity = 'presynaptic')
        return self.connectorIDs

    # gets the total number of nodes that make up a given skeleton
    def getNumNodes(self):
        if self.numNodes is None:
            self.getSkeletonNodes()
        numNodes = len(self.nodes)
        return numNodes


def builder(SKID=None):
    if SKID is None:
        # sets list of all skeleton IDs
        mySkels = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int()

        # creates dictionary with keys as str(skel IDs) and values as number of synapses with GF1
        myGF1Connectivity = GetGF1Connectivity.removeExtra()
        myGF2Connectivity = GetGF1Connectivity.removeExtra(skeleton_id='291870')

        # creates empty list to be filled with all instances
        myNeurons = []

        # creates list of of all instances while setting each instance's name and skeletonID to be an element from
        # mySkls
        for i in mySkels:
            x = GFinputNeuron(i)
            myNeurons.append(x)
    else:
        SKID = int(SKID)
        myNeurons = []
        x = GFinputNeuron(SKID)
        myNeurons.append(x)
        myGF1Connectivity = []
        myGF2Connectivity = []

        # creates dictionary with key-value pairs of str(skelID) and list of str(annotations)
    myAnnotations = GetListOfSkIDAndAnnotations.getMyAnnotations()

    # creates a dictionary with key-value pairs of int(skelID) and and str(neuron name)
    myNames = GetAnnotationsRemoveExtraneousInfo.getLookUpTableSkID_Name()

    myCommissures = GetAnnotationsRemoveExtraneousInfo.queryByMetaAnnotation('commissure')

    myClassTypes = GetAnnotationsRemoveExtraneousInfo.queryByMetaAnnotation('classType')
    # converts skeletonID attribute to string for use as dictionary key then adds all available synapses from
    # dictionary of synapses and all       available annotations from dictionary of annotations
    for elem in myNeurons:
        y = elem.skeletonID
        z = str(y)
        if z in myGF1Connectivity:
            elem.GF1synapseCount = myGF1Connectivity[z]
        else:
            elem.GF1synapseCount = 0
        if z in myGF2Connectivity:
            elem.GF2synapseCount = myGF2Connectivity[z]
        else:
            elem.GF2synapseCount = 0
        if z in myAnnotations:
            elem.annotations = myAnnotations[z]
            p = elem.annotations
            for abc in p:
                if (
                        'Unclassified' in abc or 'LC4' in abc or 'LPLC2' in abc or 'JONeuron' in abc or 'GCI' in abc
                        or 'putative DN' in abc) and 'synaptic' not in abc and 'andGFN' not in \
                        abc and 'HK' not in abc and 'Exploration' not in abc and 'type 37' not in abc and 'type 38' \
                        not in abc and 'type 44' not in abc and 'type 48' not in abc and 'miscellaneous' not in abc \
                        and "Ascending" not in abc and "Descending" not in abc and "shared" not in abc:
                    elem.classification = abc
                if 'RIGHT' in abc or 'LEFT' in abc or 'midLine' in abc:
                    if elem.hemisphere is None:
                        elem.hemisphere = abc
                        elem.somaSide = abc
                if "JON" in abc and "synaptic" not in abc:
                    elem.classification = abc
                if elem.commissure is None:
                    if abc in myCommissures:
                        elem.commissure = abc
                if elem.classType is None:
                    if abc in myClassTypes:
                        elem.classType = abc
                if elem.cellBodyRind is None:
                    if 'CBR' in abc and len(abc) == 4:
                        elem.cellBodyRind = abc
        if "JONeuron" in elem.annotations:
            elem.identification = 'JONeuron'
        if elem.hemisphere is None:
            elem.hemisphere = "RIGHT HEMISPHERE"
            elem.somaSide = "RIGHT HEMISPHERE"
        if elem.commissure is None and 'Bilateral' not in elem.annotations:
            elem.commissure = 'unilateral'
        if y in myNames:
            elem.neuronName = myNames[y]
    return myNeurons


def buildFromSkidList(myList):
    #sets list of all skeleton IDs
    mySkels = myList


    #creates dictionary with keys as str(skel IDs) and values as number of synapses with GF1 
    myGF1Connectivity = GetGF1Connectivity.removeExtra()
    

    #creates dictionary with key-value pairs of str(skelID) and list of str(annotations)
    myAnnotations = GetListOfSkIDAndAnnotations.getMyAnnotations()

    #creates a dictionary with key-value pairs of int(skelID) and and str(neuron name)
    myNames = GetAnnotationsRemoveExtraneousInfo.getLookUpTableSkID_Name()
    
    #creates empty list to be filled with all instances
    myNeurons = []

    #creates list of of all instances while setting each instance's name and skeletonID to be an element from mySkls
    for i in mySkels:       
        x = GFinputNeuron(i)
        myNeurons.append(x)

    # converts skeletonID attribute to string for use as dictionary key then adds all available synapses from dictionary of synapses and all       available annotations from dictionary of annotations
    for elem in myNeurons:
        y = elem.skeletonID
        z = str(y)      
        if z in myGF1Connectivity:
            elem.GF1synapseCount = myGF1Connectivity[z]
        if z in myAnnotations:
            elem.annotations = myAnnotations[z]
            p = elem.annotations
        if y in myNames:
            elem.neuronName = myNames[y]
    
    return myNeurons
    
def buildSingleCell(SKID):
    
    aCell = GFinputNeuron(SKID)
    
    #sets annotations based on SKID
    aCell.annotations = GetAnnotationsRemoveExtraneousInfo.setAnnotationLookUpTable(SKID)
    
    aCell.neuronName = GetAnnotationsRemoveExtraneousInfo.getName(SKID)
    
    aCell.GF1synapseCount = 0
    
    return aCell

def buildSingleCellQuick(SKID):
    
    aCell = GFinputNeuron(SKID)
        
    aCell.GF1synapseCount = 0  

    
    return aCell


def buildSingleCellLC6partners(SKID):
    aCell = GFinputNeuron(SKID)

    # sets annotations based on SKID
    aCell.annotations = GetAnnotationsRemoveExtraneousInfo.setAnnotationLookUpTable(SKID)

    aCell.neuronName = GetAnnotationsRemoveExtraneousInfo.getName(SKID)

    aCell.GF1synapseCount = 0

    for i in aCell.annotations:
        if 'cluster' in i:
            aCell.classification = i
    return aCell

# returns a subset based upon annsotation: mySet = DNIN_set instance, annotation = string annotation, annotation can also be a list of annotation strings
def createGroupByAnnotation(mySet, annotation):
    myNewSet = []
    if isinstance(annotation, str):
        for item in mySet:
            for i in item.annotations:
                if i == annotation:
                    myNewSet.append(item)
                    continue
    elif isinstance(annotation, list):
        for item in mySet:
            for i in item.annotations:
                if i in annotation:
                    myNewSet.append(item)
                    continue
    a = subSetBuilder(myNewSet)
    if mySet.groupName is None:
        a.groupName = annotation
    elif mySet.groupName == "None":
        a.groupName = annotation

    else:
        a.groupName = mySet.groupName + "_" + annotation
    if mySet.groupName is not None:
        a.groupName = mySet.groupName
    print("There are {} neurons with annotation {}: \n".format(5, a.groupName))
    return a




def subSetBuilder(fullSet):
    mySubSet = GFinputNeuron(np.array(fullSet))
    if isinstancemodality(fullSet, GFinputNeuron):
        if fullSet.groupName != None:
            mySubSet.groupName = fullSet.groupName
        if mySubSet.allSynapseCoordinates is not None:
            mySubSet.combineAllSynLocations()
        if mySubSet.numSynapsesByBranch is not None:
            mySubSet.numSynapsesByBranch = {}
            branches = ['soma tract', 'medial', 'anterior', 'lateral']
            for x in branches:
                if x not in mySubSet.numSynapsesByBranch:
                    mySubSet.numSynapsesByBranch[x] = 0
                for i in mySubSet:
                    mySubSet.numSynapsesByBranch[x] += i.synapsesByBranch[x]
        return mySubSet
    else:
        return mySubSet