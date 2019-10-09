import MyCustomGFNeuronClass
import numpy as np
import scipy as sp
import collections
import statistics as stat
import jsonNeurons as JN
import colour
import GetAnnotationsRemoveExtraneousInfo
import getSkeletonNodesNew as GN
import GetGF1Connectivity as GC
import pandas
import config
import exportToCSV as E2C
import clusteringAlgorithms
import csv
import requests
import json
import itertools
from requests.auth import AuthBase
from collections import defaultdict
from copy import copy, deepcopy

token = config.token
project_id = config.project_id


class CatmaidApiTokenAuth(AuthBase):
    """Attaches HTTP X-Authorization Token headers to the given Request."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['X-Authorization'] = 'Token {}'.format(self.token)
        return r


class GFIN_set(object):

    def __init__(self, container=None):
        super().__init__()
        if container is None:
            self.container = []
        else:
            self.container = container

        self.skeletonID = 4947529
        self.AllGF1Synapses = self._GF1Synapses()
        self.AllGF2Synapses = self._GF2Synapses()
        self.percentTotalSynapses = self._setPercentTotalSynapses()
        self.numNeurons = self._getNumNeurons()
        self.groupName = None
        # self.averageSyn = self._avgSyn()
        self.medianSyn = None
        self.minSyn = None
        self.maxSyn = None
        self.connectorInfo = None  # should be a dictionary with the branches as keys and connectorIDs as values
        self.numSynapsesByBranch = None
        self.allSynapseCoordinates = None  # will be filled with the coordinate points in format: {conID:x,y,z}
        self.allAnnotations = self._setAllAnnotations()
        self.varCheck = []
        self.allConnectorInfo = None
        self.branchCoordinates = None
        self.neuroDistroAdvanced = []
        self.modality = None
        self.BiUni = None
        self.IpsiContraMid = None
        self.groupNumber = None
        self.morphology = None

    def __len__(self):
        return len(self.container)

    # allows for indexing/slicing using either the index (nums lessthan 10,000) or the skid(nums greater than 10,000)
    def __getitem__(self, index):
        if isinstance(index, int):
            if index < 10000:
                return self.container[index]
            else:
                for i in self:
                    if i.skeletonID == index:
                        return i
        # returns subset of type GFIN_set
        elif isinstance(index, slice):
            x = GFIN_set(self.container[index])
            return x
        else:
            raise TypeError

    def __setitem__(self, index, value):
        if index <= len(self.container):
            self.container[index] = value
        else:
            raise IndexError()

    def __getslice__(self, i, j):
        return self.container[max(0, i):max(0, j):]

    def __contains__(self, value):
        return value in self.container

    def __repr__(self):
        return str(self.container)

    def __add__(self, otherList):
        myList = []
        for i in self.container:
            myList.append(i)
        if isinstance(otherList, MyCustomGFNeuronClass.GFinputNeuron):
            myList.append(otherList)
            added = subSetBuilder(myList)
            for i in vars(self).keys():
                if i is not 'numNeurons' and i is not 'container' and i is not 'percentTotalSynapses':
                    setattr(added, i, getattr(self, i))
            return added
        else:
            for i in otherList.container:
                myList.append(i)
            added = subSetBuilder(myList)
            for i in vars(self).keys():
                if i is not 'numNeurons' and i is not 'container' and 'percent' not in i:
                    setattr(added, i, getattr(self, i))
            if self.groupName != None:
                if otherList.groupName != None:
                    added.groupName = str(self.groupName) + str(otherList.groupName)
                    return added
                else:
                    added.groupName = str(self.groupName)
                    return added
            elif otherList.groupName != None:
                added.groupName = str(otherList.groupName)
                return added

        return added

    def __sub__(self, otherList):
        myList = []
        for i in self.container:
            myList.append(i)
        if isinstance(otherList, MyCustomGFNeuronClass.GFinputNeuron):
            myList.remove(otherList)
        else:
            for i in otherList.container:
                myList.remove(i)
        subtracted = subSetBuilder(myList)
        return subtracted

    '''def append(self, argument):
        if isinstance(argument, int):
            self += argument
        elif isinstance(argument, slice):
            pass
        pass'''

    # input should be skeletonID of neuron of interest, function returns the index that can be called on neuron set to get info about that
    # neuron
    def index(self, skeletonID):
        count = 0
        for i in self:
            if i.skeletonID == skeletonID:
                return count
            elif not isinstance(skeletonID, int):
                print("Index only for integers")
                break
            else:
                count += 1

    def __str__(self):
        this = ""
        for item in self:
            this += str(item)
            this += "\n"
        return this

    '''def __str__(self.connectorInfo):
        anteriorCount = len(self.ConnectorInfo['anterior'])
        medialCount = len(self.ConnectorInfo['medial'])
        lateralCount = len(self.ConnectorInfo['lateral'])
        somaTractCount = len(self.ConnectorInfo['soma tact'])
        
        myString = 'Anterior Synapse Count: {}, medial Synapse count: {}, lateral Synapse Count: {}, soma synapse Count: {}'.format(anteriorCount, medialCount, lateralCount, somaTractCount)
        return myString'''

    # Sets total GF1 Synapse Count
    def _GF1Synapses(self):
        curSyn = 0
        for item in self:
            curSyn += item.GF1synapseCount
        return curSyn

    # Sets total GF2 Synapse Count
    def _GF2Synapses(self):
        curSyn = 0
        for item in self:
            curSyn += item.GF2synapseCount
        return curSyn

    # returns the number of neurons in the current group
    def _getNumNeurons(self):
        numNeurons = len(self)
        return numNeurons

    # returns the percentCount of any constructed GFIN_set (if not == 99.99%: probably a bug in code); also sets the initial percent total
    # synapses for each individual neuron object, and then checks whether or not their PTS is not zero, so as to avoid resetting to percent
    # synapses of current group
    def _setPercentTotalSynapses(self):
        percentCount = 0
        for item in self:
            if item.percentTotalSynapse != 0:
                item.percentCurrentGroup = item.GF1synapseCount / self.AllGF1Synapses
                percentCount += item.percentTotalSynapse
            elif self.AllGF1Synapses == 0:
                item.percentTotalSynapse = 0
                percentCount += item.percentTotalSynapse
            else:
                item.percentTotalSynapse = item.GF1synapseCount / self.AllGF1Synapses
                percentCount += item.percentTotalSynapse
        return percentCount

    def _avgSyn(self):
        myAvgLst = []
        myAvg = 0
        for i in self:
            myAvgLst.append(i.GF1synapseCount)
        myAvg = stat.mean(myAvgLst)
        # self.averageSyn = myAvg
        return myAvg

    def _medSyn(self):
        myMedLst = []
        myMed = 0
        for i in self:
            myMedLst.append(i.GF1synapseCount)
        myMed = stat.median(myMedLst)
        self.medianSyn = myMed
        return myMed

    def _setAllAnnotations(self):
        annotationList = []
        for neuron in self:
            for annotation in neuron.annotations:
                if annotation not in annotationList and 'type' not in annotation:
                    annotationList.append(annotation)
        return annotationList

    def minMax(self):
        myOrderedList = sortBySynH2L(self)
        self.minSyn = myOrderedList[-1].GF1synapseCount
        self.maxSyn = myOrderedList[0].GF1synapseCount
        return self

    # provides all neurons in the set with a list of x,y,z coordinates for their respective soma attributes. not part of builder because it can be computationally heavy (i.e. many server requests so slow)
    def updateSomata(self):
        for i in self:
            if i.soma is None:
                i.soma = i.getSomaNode()
            else:
                continue
        self.varCheck.append('soma')
        return self

    # input is an object of type GFIN_set and result is population of the skeletonNodes attribute for each GFinput neuron in the set
    def updateSkeletonNodes(self):
        for i in self:
            if i.skeletonNodes is None:
                i.getSkeletonNodes()
            else:
                continue
        self.varCheck.append('skeletonNodes')
        return self

    def getConnectors(self):
        myBranches = ['lateral', 'medial', 'anterior', 'soma tract', 'descending tract']
        myConnectors = {}
        myConCount = {}
        connectorInfo = GN.getAllConnectorInfo()
        while len(myBranches) is not 0:
            branch = myBranches.pop()
            myConnectors[branch] = GN.getConnectorsByBranch(branch=branch, connectorInfo=connectorInfo)
            myConCount[branch] = len(myConnectors[branch])
        self.connectorInfo = myConnectors
        self.numSynapsesByBranch = myConCount
        self.varCheck.append('connectors')
        return self


    def getConnectorInfo(self, polarity='postsynaptic'):
        self.allConnectorInfo = getAllConnectorInfo(skeletonID=self.skeletonID, polarity=polarity)
        return self.allConnectorInfo

    def getBranchCoordinates(self):
        self.branchCoordinates = findBranchCoordinates(self)
        return self.branchCoordinates



    def getNumPartnersBySkid(self):
        myLC4List = []
        myLPLC2List = []
        myLPC1List = []
        myLPLC1List = []

        for neuron in self:
            if 'putative LC4 neuron' in neuron.annotations:
                myLC4List.append(str(neuron.skeletonID))
            if 'LPLC2' in neuron.annotations:
                myLPLC2List.append(str(neuron.skeletonID))
            # if 'Postsynaptic to LPLC1' in neuron.annotations:
            # myLPLC1List.append(str(neuron.skeletonID))
            # if 'postsynaptic to LPC1' in neuron.annotations:
            # myLPC1List.append(str(neuron.skeletonID))

        for i in self:
            a = None
            b = None
            c = None
            d = None
            if 'postsynaptic to LC6' in i.annotations:
                countOfLC6SynapsesOntoMyNeuron = 0
                d = {}
                a = GC.getSkeletonPartners(int(i.skeletonID))
                b = a['incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses]
                c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron
                listOfLC6 = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation=3489456)
                strListOfLC6 = []
                for x in listOfLC6:
                    strListOfLC6.append(str(x))

                for item in c:
                    if item in strListOfLC6:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLC6SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLC6 = countOfLC6SynapsesOntoMyNeuron

            if 'Postsynaptic to LC4' in i.annotations:
                countOfLC4SynapsesOntoMyNeuron = 0
                if a is None:
                    a = GC.getSkeletonPartners(int(i.skeletonID))
                    b = a[
                        'incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses]
                    c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron
                d = {}
                for item in c:
                    if item in myLC4List:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLC4SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLC4 = countOfLC4SynapsesOntoMyNeuron
            if 'Postsynaptic to LPLC2' in i.annotations:
                countOfLPLC2SynapsesOntoMyNeuron = 0
                if a is None:
                    a = GC.getSkeletonPartners(int(i.skeletonID))
                    b = a[
                        'incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses]
                    c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron
                d = {}
                for item in c:
                    if item in myLPLC2List:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLPLC2SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLPLC2 = countOfLPLC2SynapsesOntoMyNeuron

            # putative LPLC1 = 6022624
            if 'Postsynaptic to LPLC1' in i.annotations:
                countOfLPLC1SynapsesOntoMyNeuron = 0
                if a is None:
                    a = GC.getSkeletonPartners(int(i.skeletonID))
                    b = a[
                        'incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses]
                    c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron
                d = {}
                listOfLPLC1 = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation=6022624)
                strListOfLPLC1 = []
                for x in listOfLPLC1:
                    strListOfLPLC1.append(str(x))
                for item in c:
                    if item in strListOfLPLC1:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLPLC1SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLPLC1 = countOfLPLC1SynapsesOntoMyNeuron

            # putative LPC1 = 2894936
            if 'postsynaptic to LPC1' in i.annotations:
                countOfLPC1SynapsesOntoMyNeuron = 0
                if a is None:
                    a = GC.getSkeletonPartners(int(i.skeletonID))
                    b = a[
                        'incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses]
                    c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron

                listOfLPC1 = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation=2894936)
                strListOfLPC1 = []
                for x in listOfLPC1:
                    strListOfLPC1.append(str(x))
                d = {}
                for item in c:
                    if item in strListOfLPC1:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLPC1SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLPC1 = countOfLPC1SynapsesOntoMyNeuron

            if 'Postsynaptic to LC28' in i.annotations:
                countOfLC28SynapsesOntoMyNeuron = 0
                if a is None:
                    a = GC.getSkeletonPartners(int(i.skeletonID))
                    b = a[
                        'incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses] 
                    c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron

                listOfLC28 = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation=2894936)
                strListOfLC28 = []
                for x in listOfLC28:
                    strListOfLC28.append(str(x))
                d = {}
                for item in c:
                    if item in strListOfLC28:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLC28SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLC28 = countOfLC28SynapsesOntoMyNeuron

            if 'postsynaptic to LLPC1' in i.annotations:
                countOfLLPC1SynapsesOntoMyNeuron = 0
                if a is None:
                    a = GC.getSkeletonPartners(int(i.skeletonID))
                    b = a[
                        'incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses] 
                    c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron

                listOfLLPC1 = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation=2894936)
                strListOfLLPC1 = []
                for x in listOfLLPC1:
                    strListOfLLPC1.append(str(x))
                d = {}
                for item in c:
                    if item in strListOfLLPC1:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLLPC1SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLLPC1 = countOfLLPC1SynapsesOntoMyNeuron

            if 'Postsynaptic to LPLC3' in i.annotations:
                countOfLPLC3SynapsesOntoMyNeuron = 0
                if a is None:
                    a = GC.getSkeletonPartners(int(i.skeletonID))
                    b = a[
                        'incoming']  # dict of key = SKID that is presynaptic : value = myNeuronSkid:[0,0,0,0,#synapses] 
                    c = list(b.keys())  # list of skeletonIDs that are presynaptic to neuron

                listOfLPLC3 = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation=2894936)
                strListOfLPLC3 = []
                for x in listOfLPLC3:
                    strListOfLPLC3.append(str(x))
                d = {}
                for item in c:
                    if item in strListOfLPLC3:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLPLC3SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLPLC3 = countOfLPLC3SynapsesOntoMyNeuron

        self.varCheck.append('partners')
        return self

    def makeJSONPlain(self):
        additionalInfo = outputAllInfo(self)
        JN.autoSaveJSONFlatColor(self, additionalInfo=additionalInfo)
        return

    def getAllSkeletonNodes(self):
        for i in self:
            i.getSkeletonNodes()
        self.varCheck.append('skeletonNodes')
        return self

    def LPLC2_LP_Filter(self):
        # myGroup = createGroupByAnnotation(self, 'LPLC2')

        # gets all skeletonNodes for each skeleton in the set
        self.getAllSkeletonNodes()

        LPnodesAvg = {}

        for i in self:
            if i.curColor is None:
                JN.autoSaveJSONColorGrad(self)

        # tests each node in a given skeleton for whether or not it is within the LP (based on a curve built from the points: (191994, 239560), (218895, 239680), (286360,230800), (318592,216920), (332166,209480) run through "mycurvefit.com"
        for x in self:
            LPnodes = []
            for i in x.skeletonNodes:
                if -16938980000 + (332993.6 + 16938980000) / (1.0 + (i[2] / 379562.8) ** 25.65271) <= i[1]:
                    LPnodes.append(i)
            xCount = 0
            yCount = 0
            zCount = 0
            divisor = len(LPnodes)
            if divisor == 0:
                print(x.skeletonID)
                divisor = 1
            for i in LPnodes:
                xCount += i[0]
                yCount += i[1]
                zCount += i[2]
            xAvg = xCount / divisor
            yAvg = yCount / divisor
            zAvg = zCount / divisor
            LPnodesAvg[x.skeletonID] = [xAvg, yAvg, zAvg, x.curColor]
        return LPnodesAvg

    def colorByType(self):
        for i in self:
            if 'LC4' in i.classification:
                i.curColor = 'cyan'
            elif "LPLC2" in i.classification:
                i.curColor = 'yellow'
        return

    def colorByGradient(self):
        for i in self:
            if i.curColor is None:
                JN.autoSaveJSONColorGrad(self)
        return

    def getAllGFINSynByBranch(self):
        if self.connectorInfo is None:
            self.getConnectors()
        branches = ['soma tract', 'medial', 'anterior', 'lateral', 'descending tract']
        GFsynapses = self.connectorInfo
        tempCount = 0
        for i in self:
            i.getConnectorIDs()
            for item in branches:
                for x in i.connectorIDs:
                    if x in GFsynapses[item]:
                        tempCount += 1
                        i.synLocation[x] = i.connectorIDs[x]
                i.synapsesByBranch[item] = tempCount
                tempCount = 0

        self.varCheck.append('synByBranch')
        return self

    def findNeuropils(self):
        myNeuropils = ['AL_L', 'AL_R', 'AME_L', 'AME_R', 'AMMC_L', 'AMMC_R', 'AOTU_L', 'AOTU_R', 'ATL_L', 'ATL_R',
                       'AVLP_L', 'AVLP_R', 'BU_L', 'BU_R', 'CAN_L', 'CAN_R', 'CRE_L', 'CRE_R', 'EB', 'EPA_L', 'EPA_R',
                       'FB', 'FLA_L',
                       'FLA_R', 'GA_L', 'GA_R', 'GNG', 'GOR_L', 'GOR_R', 'IB_L', 'IB_R', 'ICL_L', 'ICL_R', 'IPS_L',
                       'IPS_R',
                       'LAL_L', 'LAL_R', 'LH_L', 'LH_R', 'LO_L', 'LO_R', 'LOP_L', 'LOP_R', 'MB_CA_L', 'MB_CA_R',
                       'MB_LAC_L', 'MB_LAC_R', 'MB_ML_L', 'MB_ML_R', 'MB_PED_L', 'MB_PED_R', 'MB_VL_L', 'MB_VL_R',
                       'MB_whole_L',
                       'MB_whole_R', 'ME_L', 'ME_R', 'NO', 'PB', 'PLP_L', 'PLP_R', 'PRW', 'PVLP_L', 'PVLP_R', 'SAD',
                       'SCL_L', 'SCL_R', 'SIP_L', 'SIP_R', 'SLP_L', 'SLP_R', 'SMP_L', 'SMP_R', 'SPS_L', 'SPS_R',
                       'VES_L', 'VES_R', 'WED_L', 'WED_R']
        for i in self:
            for abc in myNeuropils:
                if abc in i.annotations:
                    i.neuropils.update({abc: 1})
                else:
                    i.neuropils.update({abc: 0})
        return self

    def findNeuropilsByDistribution(self):
        neuropils = {'AL_L': 0, 'AL_R': 0, 'AME_L': 0, 'AME_R': 0, 'AMMC_L': 0, 'AMMC_R': 0, 'AOTU_L': 0, 'AOTU_R': 0,
                     'ATL_L': 0, 'ATL_R': 0,
                     'AVLP_L': 0, 'AVLP_R': 0, 'BU_L': 0, 'BU_R': 0, 'CAN_L': 0, 'CAN_R': 0, 'CRE_L': 0, 'CRE_R': 0,
                     'EB': 0, 'EPA_L': 0, 'EPA_R': 0,
                     'FB': 0, 'FLA_L': 0,
                     'FLA_R': 0, 'GA_L': 0, 'GA_R': 0, 'GNG': 0, 'GOR_L': 0, 'GOR_R': 0, 'IB_L': 0, 'IB_R': 0,
                     'ICL_L': 0,
                     'ICL_R': 0, 'IPS_L': 0,
                     'IPS_R': 0,
                     'LAL_L': 0, 'LAL_R': 0, 'LH_L': 0, 'LH_R': 0, 'LO_L': 0, 'LO_R': 0, 'LOP_L': 0, 'LOP_R': 0,
                     'MB_CA_L': 0, 'MB_CA_R': 0,
                     'MB_LAC_L': 0, 'MB_LAC_R': 0, 'MB_ML_L': 0, 'MB_ML_R': 0, 'MB_PED_L': 0, 'MB_PED_R': 0,
                     'MB_VL_L': 0,
                     'MB_VL_R': 0,
                     'MB_whole_L': 0,
                     'MB_whole_R': 0, 'ME_L': 0, 'ME_R': 0, 'NO': 0, 'PB': 0, 'PLP_L': 0, 'PLP_R': 0, 'PRW': 0,
                     'PVLP_L': 0,
                     'PVLP_R': 0, 'SAD': 0,
                     'SCL_L': 0, 'SCL_R': 0, 'SIP_L': 0, 'SIP_R': 0, 'SLP_L': 0, 'SLP_R': 0, 'SMP_L': 0, 'SMP_R': 0,
                     'SPS_L': 0, 'SPS_R': 0,
                     'VES_L': 0, 'VES_R': 0, 'WED_L': 0, 'WED_R': 0}

        myNeuropils = ['AL_L', 'AL_R', 'AME_L', 'AME_R', 'AMMC_L', 'AMMC_R', 'AOTU_L', 'AOTU_R', 'ATL_L', 'ATL_R',
                       'AVLP_L', 'AVLP_R', 'BU_L', 'BU_R', 'CAN_L', 'CAN_R', 'CRE_L', 'CRE_R', 'EB', 'EPA_L', 'EPA_R',
                       'FB', 'FLA_L',
                       'FLA_R', 'GA_L', 'GA_R', 'GNG', 'GOR_L', 'GOR_R', 'IB_L', 'IB_R', 'ICL_L', 'ICL_R', 'IPS_L',
                       'IPS_R',
                       'LAL_L', 'LAL_R', 'LH_L', 'LH_R', 'LO_L', 'LO_R', 'LOP_L', 'LOP_R', 'MB_CA_L', 'MB_CA_R',
                       'MB_LAC_L', 'MB_LAC_R', 'MB_ML_L', 'MB_ML_R', 'MB_PED_L', 'MB_PED_R', 'MB_VL_L', 'MB_VL_R',
                       'MB_whole_L',
                       'MB_whole_R', 'ME_L', 'ME_R', 'NO', 'PB', 'PLP_L', 'PLP_R', 'PRW', 'PVLP_L', 'PVLP_R', 'SAD',
                       'SCL_L', 'SCL_R', 'SIP_L', 'SIP_R', 'SLP_L', 'SLP_R', 'SMP_L', 'SMP_R', 'SPS_L', 'SPS_R',
                       'VES_L', 'VES_R', 'WED_L', 'WED_R']
        distributions = {'Anterior': neuropils, 'Medial': neuropils, 'Lateral': neuropils, 'Descending': neuropils,
                         'Soma': neuropils, 'AnteriorMedial': neuropils, 'AnteriorLateral': neuropils,
                         'AnteriorSoma': neuropils, 'AnteriorDescending': neuropils, 'MedialLateral': neuropils,
                         'MedialSoma': neuropils, 'MedialDescending': neuropils,
                         'LateralSoma': neuropils, 'LateralDescending': neuropils, 'SomaDescending': neuropils,
                         'AnteriorMedialLateral': neuropils, 'AnteriorMedialSoma': neuropils,
                         'AnteriorMedialDescending': neuropils,
                         'AnteriorLateralSoma': neuropils, 'AnteriorLateralDescending': neuropils,
                         'AnteriorSomaDescending': neuropils,
                         'MedialLateralSoma': neuropils, 'MedialLateralDescending': neuropils,
                         'MedialSomaDescending': neuropils,
                         'LateralSomaDescending': neuropils,
                         'AnteriorMedialLateralSoma': neuropils, 'AnteriorMedialLateralDescending': neuropils,
                         'AnteriorMedialSomaDescending': neuropils,
                         'AnteriorLateralSomaDescending': neuropils, 'MedialLateralSomaDescending': neuropils,
                         'AllBranches': neuropils}

        for key in distributions.keys():
            distributions[key] = distributions['Anterior'].copy()

        for neuron in self:
            for abc in neuron.annotations:
                if abc in myNeuropils:
                    distributions[neuron.distribution][abc] += 1

        self.neuroDistroAdvanced = distributions
        return

    '''def findBranchDistributions(self):

        distributions = ['Anterior', 'Medial', 'Lateral', 'Descending', 'Soma', 'AnteriorMedial', 'AnteriorLateral',
                         'AnteriorSoma', 'AnteriorDescending', 'MedialLateral', 'MedialSoma', 'MedialDescending',
                         'LateralSoma', 'LateralDescending', 'SomaDescending',

                         'AnteriorMedialLateral', 'AnteriorMedialSoma', 'AnteriorMedialDescending',
                         'AnteriorLateralSoma', 'AnteriorLateralDescending', 'AnteriorSomaDescending',
                         'MedialLateralSoma', 'MedialLateralDescending', 'MedialSomaDescending',
                         'LateralSomaDescending',

                         'AnteriorMedialLateralSoma', 'AnteriorMedialLateralDescending', 'AnteriorMedialSomaDescending',
                         'AnteriorLateralSomaDescending', 'MedialLateralSomaDescending', 'AllBranches']


        for i in self:
            if 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'Anterior'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'Medial'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'Lateral'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'Soma'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'Descending'

            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'AnteriorMedial'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'AnteriorLateral'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'AnteriorSoma'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AnteriorDescending'

            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'MedialLateral'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'MedialSoma'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'MedialDescending'

            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'LateralSoma'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'LateralDescending'

            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'SomaDescending'

            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'AnteriorMedialLateral'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'AnteriorMedialSoma'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AnteriorMedialDescending'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'AnteriorLateralSoma'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AnteriorLateralDescending'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AnteriorSomaDescending'

            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'MedialLateralSoma'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'MedialLateralDescending'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'MedialSomaDescending'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'LateralSomaDescending'

            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' not in i.annotations:
                i.distribution = 'AnteriorMedialLateralSoma'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' not in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AnteriorMedialLateralDescending'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' not in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AnteriorMedialSomaDescending'
            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' not in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AnteriorLateralSomaDescending'
            elif 'Input to GF1 anterior' not in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'MedialLateralSomaDescending'

            elif 'Input to GF1 anterior' in i.annotations and 'Input to GF1 medial' in i.annotations and 'Input to GF1 lateral' in i.annotations and 'Input to GF1 soma tract' in i.annotations and 'Input to GF1 descending tract' in i.annotations:
                i.distribution = 'AllBranches'

        return'''

    def findBranchDistributions(self):

        for neuron in self:
            neuron.synapsesByBranch['medial']
            neuron.synapsesByBranch['lateral']
            neuron.synapsesByBranch['descending tract']
            neuron.synapsesByBranch['soma tract']
            neuron.synapsesByBranch['anterior']

        for neuron in self:
            if neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Medial'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Anterior'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Descending'
            if neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'Lateral'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'Soma'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedial'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorLateral'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorSoma'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'MedialLateral'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'MedialDescending'

            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'LateralSoma'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'LateralDescending'

            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'SomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedialLateral'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorMedialSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedialDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorLateralSoma'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorLateralDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorSomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialLateralSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'MedialLateralDescending'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialSomaDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'LateralSomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] is 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorMedialLateralSoma'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] is 0:
                neuron.distribution = 'AnteriorMedialLateralDescending'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] is 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorMedialSomaDescending'
            elif neuron.synapsesByBranch['medial'] is 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AnteriorLateralSomaDescending'
            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] is 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'MedialLateralSomaDescending'

            elif neuron.synapsesByBranch['medial'] > 0 and neuron.synapsesByBranch['anterior'] > 0 and \
                    neuron.synapsesByBranch['descending tract'] > 0 and neuron.synapsesByBranch['lateral'] > 0 and \
                    neuron.synapsesByBranch['soma tract'] > 0:
                neuron.distribution = 'AllBranches'

        return



    # will update value of your set's allSynapseCoordinates, which contains in dict form: {connectorID: [x,y,z],...}
    # only run this if you have already run getAllGFINSynByBranch()

    def findModality(self):
        for i in self:
            if "Descending Neuron" in i.annotations:
                i.modality = "Descending Neuron"

            elif "Ascending Neuron" in i.annotations:
                i.modality = "Ascending Neuron"

            elif "Visual" in i.annotations:
                i.modality = "VPN"

            elif "JONeuron" in i.annotations:
                i.modality = "JONeuron"

            elif "Other Visual" in i.annotations:
                i.modality = "Other Visual"

            elif "Non-Visual_Interneuron" in i.annotations:
                i.modality = "Non-Visual Interneuron"

            elif "Visual_Interneuron" in i.annotations:
                i.modality = "Visual Interneuron"

            elif "Mechanosensory Interneuron" in i.annotations:
                i.modality = "Mechanosensory Interneuron"

            elif "Neuron Fragment" in i.annotations:
                i.modality = "Unknown"
            else:
                i.modality = "Unknown"
        return

    def findMorphology(self):
        for neuron in self:
            if "Unclassified GF input neuron - Fragment" in neuron.annotations:
                neuron.morphology = "Fragment"
            elif "Bilateral" in neuron.annotations:
                if "Ipsilateral" in neuron.annotations:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiIpsiProject"
                    elif "local neuron" in neuron.annotations:
                        neuron.morphology = "BiIpsiLocal"
                elif "contralateral" in neuron.annotations:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiContraProject"
                elif "midLine" in neuron.annotations:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiMidProject"
                    elif "local neuron" in neuron.annotations:
                        neuron.morphology = "BiMidLocal"
                else:
                    if "projection neuron" in neuron.annotations:
                        neuron.morphology = "BiProject"
                    elif "local neuron" in neuron.annotations:
                        neuron.morphology = "BiLocal"
            elif "Unilateral" in neuron.annotations:
                if "projection neuron" in neuron.annotations:
                    neuron.morphology = "UniProject"
                elif "local neuron" in neuron.annotations:
                    neuron.morphology = "UniLocal"
        return


    def getGroupNumber(self):
        classes = defaultdict(list)
        indexed = defaultdict(list)
        num = 1
        for neuron in self:
            classes[neuron.classification].append(neuron)

        for type in classes.values():
            for neuron in type:
                neuron.groupNumber = num
            num = num + 1
        return





    def findBiUni(self):
        for i in self:
            if "Bilateral" in i.annotations:
                i.BiUni = "Bilateral"
            elif "Unclassified GF input neuron - Fragment" in i.annotations:
                i.BiUni = "Fragment"
            else:
                i.BiUni = "Unilateral"
        return

    def findIpsiContraMid(self):
        for i in self:
            if "Ipsilateral" in i.annotations:
                i.IpsiContraMid = "Ipsilateral"
            elif "contralateral" in i.annotations:
                i.IpsiContraMid = "Contralateral"
            elif "midLine" in i.annotations:
                i.IpsiContraMid = "MidLine"
            else:
                i.IpsiContraMid = "No Soma"
        return

    def combineAllSynLocations(self):
        mySet = self
        AllSyn = {}
        count = 0
        if bool(mySet[0].synLocation) == False:
            self.getAllGFINSynByBranch()
        for i in mySet:
            for z in i.synLocation:
                x = z
                while x in AllSyn:
                    x = str(z)
                    x += str(count)
                    x = int(x)
                    count += 1
                AllSyn[x] = i.synLocation[z]
        self.allSynapseCoordinates = AllSyn
        self.varCheck.append('synLocation')
        return self

    def importClusters(self, selection=None):
        if selection is not None:
            df = pandas.read_csv('C:/Users/tenshawe/Desktop/RCode/newTest/{}.csv'.format(selection),
                                 converters={"connectorID": int, 'X': float, 'Y': float, 'Z': float, 'Cluster': int})
        else:
            df = pandas.read_csv('C:/Users/tenshawe/Desktop/RCode/newTest/AllGF1Synapses8ClustersWithSKID.csv',
                                 converters={"connectorID": int, 'X': float, 'Y': float, 'Z': float, 'Cluster': int})
        for index, row in df.iterrows():
            self[int(row['skeletonID'])].GF1SynapticClusters.append(row['Cluster'])
        self.organizeSynClusters()
        self.varCheck.append('clusters')
        return self

    # creates a dict to fill the GF1SynapticClusters attribute of each neuron which has the possible cluster numbers as its keys and the count of synapses in those clusters as its values
    def organizeSynClusters(self):
        if 'clustersOrganized' in self.varCheck:
            return
        for i in self:
            myClusters = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}
            myClusterKeys = list(myClusters.keys())
            for item in i.GF1SynapticClusters:
                myClusters[str(int(item))] = myClusters[str(int(item))] + 1
            i.GF1SynapticClusters = myClusters
        self.varCheck.append("clustersOrganized")
        return self

    '''
    def importSubClusters(self):
        df=pandas.read_csv('C:/Users/polskyj/myCode/RCode/newTest/BothIDsAndBothClusters.csv',converters={"connectorID":int, 'X':float,'Y':float, 'Z':float, 'Cluster':int, 'subCluster':int})
        for index, row in df.iterrows():    
            self[int(row['skeletonID'])].GF1SynapticClusters.append(row['Cluster'], row['subCluster'])
        #self.organizeSynClusters()
        return'''

    # returns a list of neurons that provide synaptic output in the given number of clusters
    def getAllNeuronsByNumClusters(self, numClusters):
        myClusterNeurons = self
        for i in self:
            clusterCount = 0
            for item in i.GF1SynapticClusters:
                if i.GF1SynapticClusters[item] > 0:
                    clusterCount += 1
            if clusterCount != numClusters:
                myClusterNeurons -= i
            clusterCount = 0
        myNewSet = subSetBuilder(myClusterNeurons)
        if self.groupName is not None:
            myNewSet.groupName = self.groupName + 'in{}GFsynapticClusters'.format(numClusters)
        else:
            myNewSet.groupName = 'in{}GFsynapticClusters'.format(numClusters)
        return myNewSet

        # takes as input a list of cluster numbers, for which all neurons with synapses in those clusters will be returned

    def chooseNeuronsBySynCluster(self, clusterList):
        newList = []
        for i in self:
            myVar = False
            for clusterNum in clusterList:
                if i.GF1SynapticClusters[str(clusterNum)] != 0:
                    myVar = True
                    if myVar is True:
                        newList.append(i)
                        break
        myNeurons = subSetBuilder(newList)
        return myNeurons

    def importSubClusters(self, fileName=None):
        # if 'clusters' not in self.varCheck:
        #   self.importClusters()
        if fileName is None:
            fileName = 'BothIDsAndBothClusters'
        fileAddress = 'C:/Users/tenshawe/Desktop/RCode/newTest/{}.csv'.format(fileName)
        df = pandas.read_csv(fileAddress,
                             converters={"connectorID": int, 'X': float, 'Y': float, 'Z': float, 'Cluster': int,
                                         'subCluster': int})
        for index, row in df.iterrows():
            if 'tempHolder' in self[int(row['skeletonID'])].subClusters:
                self[int(row['skeletonID'])].subClusters[str(row['Cluster'])] = \
                self[int(row['skeletonID'])].subClusters['tempHolder']
                del self[int(row['skeletonID'])].subClusters['tempHolder']
            if row['subCluster'] == 1:
                self[int(row['skeletonID'])].subClusters[str(row['Cluster'])]['subCluster1'] += 1
            elif row['subCluster'] == 2:
                self[int(row['skeletonID'])].subClusters[str(row['Cluster'])]['subCluster2'] += 1
            elif row['subCluster'] == 3:
                self[int(row['skeletonID'])].subClusters[str(row['Cluster'])]['subCluster3'] += 1
        return self

    # returns a list of dictionaries - each dictionary should contain all relevant quantile information
    def makeQuantiles(self):
        mySetSynCount = self.AllGF1Synapses
        q1 = {}
        q2 = {}
        q3 = {}
        q4 = {}
        q5 = {}
        qs = [q1, q2, q3, q4, q5]
        qNames = ['q1', 'q2', 'q3', 'q4', 'q5']

        a = quantiles(self)
        a = np.delete(a, 2)
        myAdditionalInfo = outputAllInfo(self)
        c = 0
        myTempSet = self
        while (c <= 3):
            tempVar = subBySynLT(myTempSet, a[c])
            myTempSet -= tempVar
            for i in tempVar:
                i.quantile = qNames[c]
            qs[c]['synapse_Threshold'] = a[c]
            qs[c]['number_Neurons'] = tempVar.numNeurons
            qs[c]['average_synapse_count'] = tempVar.averageSyn
            qs[c]['median_synapse_count'] = tempVar.medianSyn
            qs[c]['all_GF1_Synapses'] = tempVar.AllGF1Synapses
            qs[c]['percent of all {} synapses on GF1'.format(self.groupName)] = (tempVar.AllGF1Synapses / mySetSynCount)

            tempVar = None
            c += 1
        tempVar = subBySynGT(myTempSet, a[c - 1])
        tempVar = sortBySynH2L(tempVar)
        c = 4
        for i in tempVar:
            i.quantile = qNames[c]
        qs[c]['synapse_Threshold'] = tempVar[0].GF1synapseCount
        qs[c]['number_Neurons'] = tempVar.numNeurons
        qs[c]['average_synapse_count'] = tempVar.averageSyn
        qs[c]['median_synapse_count'] = tempVar.medianSyn
        qs[c]['all_GF1_Synapses'] = tempVar.AllGF1Synapses
        qs[c]['percent of all {} synapses on GF1'.format(self.groupName)] = (tempVar.AllGF1Synapses / mySetSynCount)

        return qs

    def e2c(self):
        if 'soma' not in self.varCheck:
            self.updateSomata()
        if 'partners' not in self.varCheck:
            self.getNumPartnersBySkid()
        if 'synByBranch' not in self.varCheck:
            self.getAllGFINSynByBranch()
        E2C.makeCSV(self, 'saveWithSomaAndBranches')
        return

    def createSummary(self):
        mySet = self
        myClassList = []
        # for i in mySet:
        while len(mySet) > 0:
            # if i.classification not in myClassList[i.classification]:
            # myClassList[i.classification] = 1
            tempGroup = createGroupByClassification(mySet, mySet[0].classification)
            tempGroup.minMax()
            tempGroup._medSyn()
            tempGroup._avgSyn()
            myClassList.append(tempGroup)
            myNewSet = []
            for item in mySet:
                if item.classification != mySet[0].classification:
                    myNewSet.append(item)
            a = subSetBuilder(myNewSet)
            mySet = a

            # for item in tempGroup:
            #   mySet -= item
            # print(len(mySet))
            # else:
            #   myClassList[i.i.classification] += 1
        # for item in myClassList:
        #     #print(item.numNeurons, type(item.numNeurons))
        #     if item.numNeurons == 0:
        #         myClassList.remove(item)
        #         #print('yes')
        #     else:
        #         print(item, ': no')
        #     if item.numNeurons is None:
        #         myClassList.remove(item)
        return myClassList

    # note that the api endpoint in use here requires entity ids which equals neuron id, not skeleton ID
    # LEFT HEMISPHERE == 1223085
    def correctAnnotations(self):
        mySet = clusteringAlgorithms.removeSomaless(self)
        rightHem = []
        leftHem = []
        for item in mySet:
            if item.soma[0] < 500000:
                rightHem.append(item.skeletonID + 1)
            elif item.soma[0] > 550000:
                leftHem.append(item.skeletonID + 1)
        responseOne = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/remove'.format(project_id),
            auth=config.CatmaidApiTokenAuth(token),
            data={'entity_ids': rightHem, 'annotation_ids': [1223085]}
        )
        responseOne = json.loads(responseOne.content)
        print(responseOne)
        responseTwo = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/remove'.format(project_id),
            auth=config.CatmaidApiTokenAuth(token),
            data={'entity_ids': leftHem, 'annotation_ids': [1167304]}
        )
        responseTwo = json.loads(responseTwo.content)
        print(responseTwo)
        return

    def addAnnotation(self, newAnnotation, addToSkeletons=True, metaAnnotations=None):
        """

        :param newAnnotation: array of string - to be added to catmaid annotation of neurons (if looking for bulk annotations: set from GFIN objects
        :param addToSkeletons: default is true - if false, will create annotation and annotate it with a meta_annotation
        :param metaAnnotations: default is none - should be array[string] if desired
        :return: print out:  success or error (with error message), annotations added (name and id), neuron ids, and list of any new annotations
        """
        if addToSkeletons is True:
            mySkids = []
            for item in self:
                mySkids.append(item.skeletonID)

            response = requests.post(
                'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/add'.format(project_id),
                auth=config.CatmaidApiTokenAuth(token),
                data={'skeleton_ids': mySkids, 'annotations': newAnnotation}
            )
        else:
            response = requests.post(
                'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/add'.format(project_id),
                auth=config.CatmaidApiTokenAuth(token),
                data={'annotations': newAnnotation, 'meta_annotations': metaAnnotations}
            )

        myResults = json.loads(response.content)
        print(myResults)
        return

    '''
    def makeDataFrame(self):
        myDataFrame = {}
        myAttributeNames = ['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'GF2 Synapse Count', 'percent total synapses',
                   'classification', 'hemisphere', 'cellBodyRind', 'somaHemisphere', 'commissure', 'numLC4Syn',
                   'numLPLC2Syn',
                   'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'numLC28Syn', 'numLLPC1Syn', 'numLPLC3Syn',
                   'lateral branch',
                   'medial branch', 'anterior branch', 'soma tract', 'descending tract']
        myAttributes = [globals()neuronName, skeletonID, GF1synapseCount, GF2synapseCount, percentTotalSynapse, classification, hemisphere, cellBodyRind, somaSide, commissure, postsynapticToLC4, postsynapticToLPLC2, postsynapticToLC6, postsynapticToLPLC1, postsynapticToLPC1, postsynapticToLC28, postsynapticToLLPC1, postsynapticToLPLC3, synapsesByBranch['lateral'], synapsesByBranch['medial'], synapsesByBranch['anterior'], synapsesByBranch['soma tract'], synapsesByBranch['descending tract']]
        for attribute in myAttributeNames:
            myDataFrame[attribute] = []
        for neuron in self:
            for attribute in myAttributeNames:
                myDataFrame[attribute].append()
        return myDataFrame
    '''

    def makeDataFrame(self):

        myWriter = csv.writer()
        myRows0 = ['Neuron Name', 'skeletonID', 'GF1 Synapse Count', 'GF2 Synapse Count', 'percent total synapses',
                   'classification', 'hemisphere', 'cellBodyRind', 'somaHemisphere', 'commissure', 'numLC4Syn',
                   'numLPLC2Syn', 'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'numLC28Syn', 'numLLPC1Syn',
                   'numLPLC3Syn', 'lateral branch', 'medial branch', 'anterior branch', 'soma tract',
                   'descending tract']
        myRows = myRows0 + mySet.allAnnotations
        myWriter.writerow(myRows)
        for item in self:
            theseAnnotations = []
            for annotation in self.allAnnotations:
                if annotation in item.annotations:
                    theseAnnotations.append(1)
                else:
                    theseAnnotations.append(0)
            curRow = [item.neuronName, item.skeletonID, item.GF1synapseCount, item.GF2synapseCount,
                      item.percentTotalSynapse, item.classification, item.hemisphere, item.cellBodyRind,
                      item.somaSide, item.commissure, item.postsynapticToLC4, item.postsynapticToLPLC2,
                      item.postsynapticToLC6, item.postsynapticToLPLC1, item.postsynapticToLPC1,
                      item.postsynapticToLC28, item.postsynapticToLLPC1, item.postsynapticToLPLC3,
                      item.synapsesByBranch['lateral'], item.synapsesByBranch['medial'],
                      item.synapsesByBranch['anterior'], item.synapsesByBranch['soma tract'],
                      item.synapsesByBranch['descending tract']]
            fullRow = curRow + theseAnnotations
        myWriter.writerow(fullRow)

        return myWriter

    def allMyVars(self):
        allVars = dir(self)
        allSigVars = []
        for i in allVars:
            if "__" not in i:
                allSigVars.append(i)
        return allSigVars

    # Needs to be run before getAllGFINSynByBranch()
    def getJOPartnerNumbers(self):
        with open('KnownJONeuronsRIGHTHEMISPHERE.json') as myJONfile:
            myJO = json.load(myJONfile)

        JOskids = []
        for i in myJO:
            JOskids.append(i['skeleton_id'])

        joConnectorInfo = GC.getConnectorsStep1(JOskids, "presynaptic_to", False)
        joConnectorIDs = []
        for i in joConnectorInfo['connectors']:
            joConnectorIDs.append(i[0])

        if self[0].connectorIDs is None:
            for i in self:
                i.getConnectorIDs(polarity='postsynaptic')
        for i in self:
            for item in i.connectorIDs:
                if item in joConnectorIDs:
                    i.postsynapticToJON += 1
        self.varCheck.append("JO_partners")
        return self


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



#takes list of connectors and returns partner info
#parameter should be above function call, returns same as above with a list of postsynaptic partner skids apended to end
#takes long time to run but time varies on number of synapses
def getConnectedPartners(connectorIDArray):
    newDict = {}
    for connectorID in connectorIDArray:
        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/{}/'.format(connectorID)
        )
        myR = json.loads(response.content)
        #print(myR)
        newDict[connectorID] = myR
    return newDict

#returns SKID of presynaptic partners of a synapse from a dict from 'getConnectorPartners'
def getConnectedPartnersSKIDOnly(connectorIDArray):
    newDict = getConnectedPartners(connectorIDArray)
    partners = []
    skelIDs = []
    id = []
    for i in newDict.items():
        partners.append(i)
        part = i[1].get('partners')
        id = part[1].get('skeleton_id')
        skelIDs.append(id)
    return skelIDs



# call this to build a GFIN_set from all GF1 input neurons
def builder():
    mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
    mySet._avgSyn()
    mySet._medSyn()
    mySet.minMax()
    return mySet



def buildFromSkidList(myList):
    mySet = GFIN_set(np.array(MyCustomGFNeuronClass.buildFromSkidList(myList)))
    return mySet


# sorts neurons from low to high synapse counts
def sortBySynL2H(mySet):
    L2H = sorted(mySet, key=MyCustomGFNeuronClass.GFinputNeuron.getGF1synapse)
    mySortedList = subSetBuilder(L2H)
    if mySet.groupName != None:
        mySortedList.groupName = mySet.groupName
    return mySortedList


# sorts neurons from low to high synapse counts
def sortBySynH2L(mySet):
    H2L = sorted(mySet, key=MyCustomGFNeuronClass.GFinputNeuron.getGF1synapse, reverse=True)
    mySortedList = subSetBuilder(H2L)
    if mySet.groupName != None:
        mySortedList.groupName = mySet.groupName
    return mySortedList


# returns a subset based upon annotation: mySet = GFIN_set instance, annotation = string annotation, annotation can also be a list of annotation strings
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
                    if item not in myNewSet:
                        myNewSet.append(item)
                        # continue
    a = subSetBuilder(myNewSet)
    if type(annotation) == list:
        tempName = ', '.join(annotation)
        annotation = tempName
    if mySet.groupName is None:
        a.groupName = annotation
    elif mySet.groupName == "None":
        a.groupName = annotation

    else:
        a.groupName = mySet.groupName + "_" + annotation
    print("There are {} neurons with annotation {}: \n".format(len(a), a.groupName))
    return a


# returns a subset based upon classification: mySet = GFIN_set instance, classification = string classification
def createGroupByClassification(mySet, classification):
    myNewSet = []
    for item in mySet:
        if item.classification == classification:
            myNewSet.append(item)
    a = subSetBuilder(myNewSet)
    # print(a.numNeurons)

    if mySet.groupName is None or mySet.groupName is 'GF1 Input Neurons':
        a.groupName = classification
    elif mySet.groupName == "None" or mySet.groupName == 'GF1 Input Neurons':
        a.groupName = classification

    else:
        a.groupName = mySet.groupName + "_" + classification
    # print(a.groupName, ":", len(a), "/n")

    # print("There are {} neurons with classification {}: \n".format(len(a), a.groupName))
    return a


# returns a subset based upon annotation that neurons do NOT have: mySet = GFIN_set instance, annotation = string annotation
def createGroupByNotAnnotation(mySet, annotation):
    myNewSet = mySet
    for item in mySet:
        if annotation in item.annotations:
            myNewSet -= item
            continue
    a = subSetBuilder(myNewSet)
    if myNewSet.groupName is not None:
        myNewSet.groupName += 'not' + str(annotation)
    else:
        myNewSet.groupName = 'not' + str(annotation)

    print("There are {} neurons left without annotation {}: \n".format(len(myNewSet), annotation))
    return a


# returns a subset based upon synCount: mySet = GFIN_set instance, synNumber = Number of Synapses(or less) that you want results to have
def subBySynLT(mySet, synNumber):
    myNewSet = []
    for item in mySet:
        if item.GF1synapseCount <= synNumber:
            myNewSet.append(item)
            continue
    x = subSetBuilder(myNewSet)
    if mySet.groupName != None:
        x.groupName = str(mySet.groupName) + "with" + str(synNumber) + "synapses"
    print("{} of these neurons have {} or less synapses \n".format(len(myNewSet), synNumber))
    return x


# returns a subset based upon synCount: mySet = GFIN_set instance, synNumber = Number of Synapses(or greater) that you want results to have
def subBySynGT(mySet, synNumber):
    myNewSet = []
    for item in mySet:
        if item.GF1synapseCount >= synNumber:
            myNewSet.append(item)
            continue
    x = subSetBuilder(myNewSet)
    if mySet.groupName != None:
        x.groupName = str(mySet.groupName) + "with" + str(synNumber) + "synapses"
    print("{} of these neurons have {} or more synapses \n".format(len(myNewSet), synNumber))
    return x


# used by other functions to transform resulting data types into GFIN_set type
'''def subSetBuilder(fullSet, oldSet = None):
    mySubSet = GFIN_set(np.array(fullSet))
    if isinstance(oldSet, GFIN_set):
        for i in vars(oldSet):
            myI = getattr(oldSet, i)
            if myI is not None:
                setattr(mySubSet, i, myI)                        
        return mySubSet
    else:
        return mySubSet'''
'''def subSetBuilder(fullSet, oldSet = None):
    mySubSet = GFIN_set(np.array(fullSet))
    if isinstance(oldSet, GFIN_set):
        myVars = vars(oldSet)
        myVarsKeys = vars(oldSet).keys()
        #print(myVars)
        #myVarsList = list(myVars)
        #myVarsList -= 'container'
        #myVarsList -= 'numNeurons'
        #myVarsList -= 'percentTotalSynapses'
        del myVars['container']
        del myVars['numNeurons']
        del myVars['percentTotalSynapses']

        for i in myVars:
            print(i)
            #myI = getattr(fullSet, i)
            myI = myVars[i]
            if myI is not None:
                setattr(mySubSet, i, myI)                        
        return mySubSet
    else:
        return mySubSet'''


def subSetBuilder(fullSet):
    mySubSet = GFIN_set(np.array(fullSet))
    if isinstance(fullSet, GFIN_set):
        if fullSet.groupName != None:
            mySubSet.groupName = fullSet.groupName
        if mySubSet.allSynapseCoordinates is not None:
            mySubSet.combineAllSynLocations()
        if mySubSet.numSynapsesByBranch is not None:
            mySubSet.numSynapsesByBranch = {}
            branches = ['soma tract', 'medial', 'anterior', 'lateral', 'descending tract']
            for x in branches:
                if x not in mySubSet.numSynapsesByBranch:
                    mySubSet.numSynapsesByBranch[x] = 0
                for i in mySubSet:
                    mySubSet.numSynapsesByBranch[x] += i.synapsesByBranch[x]
        return mySubSet
    else:
        return mySubSet


# use to fix add
def subSetBuilderNew(fullSet):
    mySubSet = GFIN_set(np.array(fullSet))
    for i in fullSet:
        for item in i:
            setattr(mySubSet[i.skeletonID], item, (getattr(i, item)))
    return mySubSet
    # old codethat was formerly part of subSetBuilder


# unusued consider deleting
def sliceBuilder(aSet):
    print(aSet)
    newSet = GFIN_set(np.array(aSet))
    return newSet


# Unused - consider deleting
def _getSynCount(self):
    mySynCount = 0
    for item in self:
        print("item", item)
        mySynCount += self[item].GF1synapseCount
        return mySynCount


def totalSynapseCount(neurons):
    totalSynapseCount = int()
    for i in neurons:
        totalSynapseCount += neurons[i].GF1synapseCount
    return totalSynapseCount


from scipy.stats.mstats import mquantiles


def quantiles(mySet):
    mySyns = []
    for i in mySet:
        mySyns.append(i.GF1synapseCount)
    myQuant = mquantiles(mySyns, prob=[0.2, 0.4, 0.5, 0.6, 0.8])
    return myQuant


from sklearn.cluster import KMeans


def getMyKMeans(mySet):
    mySyns = []
    for i in mySet:
        mySyns.append(i.GF1synapseCount)
    arrayMySyns = np.asarray(mySyns)
    kmeans = KMeans(n_clusters=4).fit(arrayMySyns)
    return (kmeans)


def makeDistributedGroups(mySet):
    a = quantiles(mySet)
    for i in a:
        if i == a[2]:
            continue
        elif i == a[0]:
            b = subBySynLT(mySet, i)
            lastI = i
            JN.makeJsonFile(b)
        elif i == a[4]:
            b = subBySynGT(mySet, i)
            JN.makeJsonFile(b)
        else:
            r = subBySynLT(mySet, i)
            z = subBySynGT(r, lastI)
            lastI = i
            JN.makeJsonFile(z)
    return


def makeDistributedGroupsByColor(mySet):
    mySetSynCount = mySet.AllGF1Synapses
    a = quantiles(mySet)
    a = np.delete(a, 2)
    myAdditionalInfo = outputAllInfo(mySet)
    myBigSet = [None] * 5
    c = 0
    myTempSet = mySet
    while (c <= 3):
        tempVar = subBySynLT(myTempSet, a[c])
        myBigSet[c] = tempVar
        myTempSet -= tempVar
        myAdditionalInfo += "\n quantile with <= {} synapses onto GF:  \n      - {} neurons in this quantile \n     -average number of synapses: {} \n     -median number of synapses: {} \n      - total number of synapses onto GF in this quantile: {} \n     - % of all {} synapses onto GF: {} \n".format(
            a[c], tempVar.numNeurons, tempVar.averageSyn, tempVar.medianSyn, tempVar.AllGF1Synapses, mySet.groupName,
            (tempVar.AllGF1Synapses / mySetSynCount))
        tempVar = None
        c += 1
    tempVar = subBySynGT(myTempSet, a[c - 1])
    myBigSet[c] = tempVar
    myAdditionalInfo += "\n quantile with > {} synapses onto GF:  \n      - {} neurons in this quantile \n     -average number of synapses: {} \n     -median number of synapses: {} \n      - total number of synapses onto GF in this quantile: {} \n     - % of all {} synapses onto GF: {}".format(
        a[c - 1], tempVar.numNeurons, tempVar.averageSyn, tempVar.medianSyn, tempVar.AllGF1Synapses, mySet.groupName,
        (tempVar.AllGF1Synapses / mySetSynCount))
    for i in myBigSet:
        i.groupName = mySet.groupName
        # myAdditionalInfo += "\n quantile {} synapses or less: \n      - {} neurons in this quantile \n     -average number of synapses: {} \n     -median number of synapses: {} \n      - %LPLC2 synapses: {}".format(a[myBigSet.index(i)], i.numNeurons, i.avg, i.med)
    JN.autoSaveJSONFlatColor(myBigSet, additionalInfo=myAdditionalInfo)
    return myBigSet


def outputAllInfo(mySet):
    myInfo = ""
    myInfo += str(mySet.groupName) + '\n'
    myInfo += "number: " + str(mySet.numNeurons) + '\n'
    myInfo += "GF synapse count: " + str(mySet.AllGF1Synapses) + '\n'
    myInfo += "%total GF synapses: " + str(mySet.percentTotalSynapses) + '\n'
    myInfo += "quantiles used: " + str(quantiles(mySet)) + '\n'
    return myInfo


def appendNonGFIN(mySet, annotation):
    testList = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation)
    curSKIDs = []
    for i in mySet:
        curSKIDs.append(i.skeletonID)
    for item in testList:
        if item not in curSKIDs:
            myNeuron = MyCustomGFNeuronClass.buildSingleCell(int(item))
            mySet += myNeuron
    return mySet


def appendNonGFIN2(mySet, annotation):
    testList = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation)
    curSKIDs = []
    for i in mySet:
        curSKIDs.append(i.skeletonID)
    for item in testList:
        if item not in curSKIDs:
            myNeuron = MyCustomGFNeuronClass.buildSingleCellQuick(int(item))
            mySet += myNeuron
    return mySet


def appendLC6partners(mySet, annotation):
    testList = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation)
    curSKIDs = []
    for i in mySet:
        curSKIDs.append(i.skeletonID)
    for item in testList:
        if item not in curSKIDs:
            myNeuron = MyCustomGFNeuronClass.buildSingleCellLC6partners(int(item))
            mySet += myNeuron
    return mySet


def findBranchCoordinates(mySet):
    # get list of coordinates by synapse id
    mySet.combineAllSynLocations()
    # get list of synapse id by branch
    mySet.getAllGFINSynByBranch()

    descend = mySet.connectorInfo.get('descending tract')
    descend_coords = []
    soma = mySet.connectorInfo.get('soma tract')
    soma_coords = []
    anterior = mySet.connectorInfo.get('anterior')
    anterior_coords = []
    medial = mySet.connectorInfo.get('medial')
    medial_coords = []
    lateral = mySet.connectorInfo.get('lateral')
    lateral_coords = []

    all_coords = list(mySet.allConnectorInfo.values())

    for i in all_coords[0]:
        if i[1] in descend:
            descend_coords.append(i)
    for i in all_coords[0]:
        if i[1] in soma:
            soma_coords.append(i)
    for i in all_coords[0]:
        if i[1] in anterior:
            anterior_coords.append(i)
    for i in all_coords[0]:
        if i[1] in medial:
            medial_coords.append(i)
    for i in all_coords[0]:
        if i[1] in lateral:
            lateral_coords.append(i)

    return mySet




