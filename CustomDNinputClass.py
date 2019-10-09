import requests
import json
import itertools
import GetLookUpTable
import GetAnnotationsRemoveExtraneousInfo
import GetListOfSkIDAndAnnotations
import GetDNrightConnectivity
import getSkeletonNodesNew
import config

class DNinputNeuron(object):
    
    def __init__(self, skeletonID):
        self.skeletonID = skeletonID
        self.DNright = int()
        self.DNleft = int()
        self.annotations = []
        self.neuronName = ''
        self.percentTotalSynapse = 0       #total percent of DNrightsynapses
        self.percentCurrentGroup = 0       #percent of DNrightsynapses relative to other neurons in the current sub-group of DNrightinput neurons
        self.soma = None
        self.skeletonNodes = None

        #connectorIDs is all of this neuron's connectors, not just DNinput neurons, in order to get that info: run getAllDNINSynByBranch for the set and it will fill synLocation attribute
        self.connectorIDs = None
        self.numSynByBranch = None
        self.postsynapticToLC6 = 0
        self.postsynapticToLC4 = 0
        self.postsynapticToLPLC2 = 0
        self.postsynapticToLPLC1 = 0
        self.postsynapticToLPC1 = 0
        self.classification = None
        self.hemisphere = None
        self.numNodes = None
        self.synapsesByBranch = {}
        self.synLocation = {}
        self.DNrightSynapticClusters = []
        self.quantile = None
        self.curColor = None
        self.subClusters = {'tempHolder': {'subCluster1': 0, 'subCluster2': 0, 'subCluster3': 0}}
    
    def __repr__(self):
        return '{}'.format(self.neuronName)
    
    def __str__(self):
        return "{}: skeleton ID = {}, DNright synapse count = {}, annotations = {} \n".format(self.neuronName, self.skeletonID, self.DNrightsynapseCount, self.annotations)
    
    def getSkID(self):
        return self.skeletonID
    def getDNrightsynapse(self):
        return self.DNrightsynapseCount
    def getAnnotations(self):
        myAnnotations = GetListOfSkIDAndAnnotations.getMyAnnotations()
        y = elem.skeletonID
        z = str(y)
        if z in myAnnotations:
            self.annotations = myAnnotations[z]
        return self.annotations
    def getNeuronName(self):
        y = elem.skeletonID
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
        

def builder(SKID = None):
    if SKID is None:
        #sets list of all skeleton IDs
        mySkels = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int()

        #creates dictionary with keys as str(skel IDs) and values as number of synapses with DNright 
        myDNrightConnectivity = GetDNrightConnectivity.removeExtra()

        #creates empty list to be filled with all instances
        myNeurons = []

        #creates list of of all instances while setting each instance's name and skeletonID to be an element from mySkls
        for i in mySkels:       
            x = DNinputNeuron(i)
            myNeurons.append(x)
    else:
        SKID = int(SKID)
        myNeurons = []
        x = DNinputNeuron(SKID)
        myNeurons.append(x)
        myDNrightConnectivity = []       

    #creates dictionary with key-value pairs of str(skelID) and list of str(annotations)
    myAnnotations = GetListOfSkIDAndAnnotations.getMyAnnotations()

    #creates a dictionary with key-value pairs of int(skelID) and and str(neuron name)
    myNames = GetAnnotationsRemoveExtraneousInfo.getLookUpTableSkID_Name()        
        
    # converts skeletonID attribute to string for use as dictionary key then adds all available synapses from dictionary of synapses and all       available annotations from dictionary of annotations
    for elem in myNeurons:
        y = elem.skeletonID
        z = str(y)      
        if z in myDNrightConnectivity:
            elem.DNrightsynapseCount = myDNrightConnectivity[z]
        else:
            elem.DNrightsynapseCount = 0
        if z in myAnnotations:
            elem.annotations = myAnnotations[z]
            p = elem.annotations
            for abc in p:
                if ('Unclassified'in abc or 'LC4' in abc or 'LPLC2' in abc or 'JO' in abc or 'B1' in abc or 'GCI' in abc or 'Halted' in abc or 'Neuron Fragment' in abc or 'Hampel' in abc or 'incomplete neuron' in abc or 'DN' in abc) and 'synaptic' not in abc:
                    elem.classification = abc
                #if ('type 37' in abc or 'type 38' in abc or 'type 44' in abc or 'JO' in abc:
                 #   elem.classification = 'JO'
                if elem.classification is None:
                    elem.classification = "Other"                    
                if "Descending" in abc or 'Ascending' in abc:                    
                    if 'Unclassified' in elem.classification and 'type' not in elem.classification:
                        elem.classification = "Unclassified {} DN input neuron".format(abc)
                if 'RIGHT' in abc or 'LEFT' in abc:
                    if elem.hemisphere is None:
                        elem.hemisphere = abc
                if 'Bilateral' in abc:
                    elem.hemisphere = abc
        if elem.hemisphere is None:
            elem.hemisphere = "RIGHT HEMISPHERE"

        if y in myNames:
            elem.neuronName = myNames[y]
    
    return myNeurons

def buildFromSkidList(myList):
    #sets list of all skeleton IDs
    mySkels = myList


    #creates dictionary with keys as str(skel IDs) and values as number of synapses with DNright 
    myDNrightConnectivity = GetDNrightConnectivity.removeExtra()
    

    #creates dictionary with key-value pairs of str(skelID) and list of str(annotations)
    myAnnotations = GetListOfSkIDAndAnnotations.getMyAnnotations()

    #creates a dictionary with key-value pairs of int(skelID) and and str(neuron name)
    myNames = GetAnnotationsRemoveExtraneousInfo.getLookUpTableSkID_Name()
    
    #creates empty list to be filled with all instances
    myNeurons = []

    #creates list of of all instances while setting each instance's name and skeletonID to be an element from mySkls
    for i in mySkels:       
        x = DNinputNeuron(i)
        myNeurons.append(x)

    # converts skeletonID attribute to string for use as dictionary key then adds all available synapses from dictionary of synapses and all       available annotations from dictionary of annotations
    for elem in myNeurons:
        y = elem.skeletonID
        z = str(y)      
        if z in myDNrightConnectivity:
            elem.DNrightsynapseCount = myDNrightConnectivity[z]
        if z in myAnnotations:
            elem.annotations = myAnnotations[z]
            p = elem.annotations
        if y in myNames:
            elem.neuronName = myNames[y]
    
    return myNeurons
    
def buildSingleCell(SKID):
    
    aCell = DNinputNeuron(SKID)
    
    #sets annotations based on SKID
    aCell.annotations = GetAnnotationsRemoveExtraneousInfo.setAnnotationLookUpTable(SKID)
    
    aCell.neuronName = GetAnnotationsRemoveExtraneousInfo.getName(SKID)
    
    aCell.DNrightsynapseCount = 0  

    
    return aCell

def buildSingleCellQuick(SKID):
    
    aCell = DNinputNeuron(SKID)
        
    aCell.DNrightsynapseCount = 0  

    
    return aCell    






