import config

import requests
import json
import itertools
import GetLookUpTable
import GetAnnotationsRemoveExtraneousInfo
import GetListOfSkIDAndAnnotations
import GetGF1Connectivity
import getSkeletonNodesNew


class GFinputNeuron(object):
    
    def __init__(self, skeletonID):
        self.skeletonID = skeletonID
        self.GF1synapseCount = int()
        self.GF2synapseCount = int()
        self.annotations = []
        self.neuronName = ''
        self.percentTotalSynapse = 0       #total percent of GF1synapses
        self.percentCurrentGroup = 0        #percent of GF1synapses relative to other neurons in the current sub-group of GF1input neurons
        self.soma = None
        self.skeletonNodes = None
    
    def __repr__(self):
        return '{}: {}'.format(self.neuronName, self.GF1synapseCount)
    
    def __str__(self):
        return "{}: skeleton ID = {}, GF1 synapse count = {}, annotations = {} \n".format(self.neuronName, self.skeletonID, self.GF1synapseCount, self.annotations)
    
    def getSkID(self):
        return self.skeletonID
    def getGF1synapse(self):
        return self.GF1synapseCount
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

def builder(SKID = None):
    if SKID is None:
        #sets list of all skeleton IDs
        mySkels = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int()

        #creates dictionary with keys as str(skel IDs) and values as number of synapses with GF1 
        myGF1Connectivity = GetGF1Connectivity.removeExtra()

        #creates empty list to be filled with all instances
        myNeurons = []

        #creates list of of all instances while setting each instance's name and skeletonID to be an element from mySkls
        for i in mySkels:       
            x = GFinputNeuron(i)
            myNeurons.append(x)
    else:
        SKID = int(SKID)
        myNeurons = []
        x = GFinputNeuron(SKID)
        myNeurons.append(x)
        myGF1Connectivity = []       

    #creates dictionary with key-value pairs of str(skelID) and list of str(annotations)
    myAnnotations = GetListOfSkIDAndAnnotations.getMyAnnotations()

    #creates a dictionary with key-value pairs of int(skelID) and and str(neuron name)
    myNames = GetAnnotationsRemoveExtraneousInfo.getLookUpTableSkID_Name()        
        
    # converts skeletonID attribute to string for use as dictionary key then adds all available synapses from dictionary of synapses and all       available annotations from dictionary of annotations
    for elem in myNeurons:
        y = elem.skeletonID
        z = str(y)      
        if z in myGF1Connectivity:
            elem.GF1synapseCount = myGF1Connectivity[z]
        else:
            elem.GF1synapseCount = 0
        if z in myAnnotations:
            elem.annotations = myAnnotations[z]
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

    
