import LC6_neuronClass
import numpy as np
import scipy as sp
import collections
import statistics as stat
import jsonNeurons as JN
import colour
import GetAnnotationsRemoveExtraneousInfo
import getSkeletonNodesNew as GN
import GetDNrightConnectivity as GC
import pandas
import GetAnnotationsByID


class DNIN_set(object):

    def __init__(self, container=None):
        super().__init__()
        if container is None:
            self.container = []
        else:
            self.container = container

        self.AllDNrightSynapses = self._DNrightSynapses()
        self.percentTotalSynapses = self._setPercentTotalSynapses()
        self.numNeurons = self._getNumNeurons()
        self.groupName = None
        self.connectorInfo = None  # should be a dictionary with the branches as keys and connectorIDs as values
        self.numSynapsesByBranch = None
        self.allSynapseCoordinates = None  # will be filled with the coordinate points in format: {conID:x,y,z}
        self.varCheck = []
        self.myDN = None

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
        # returns subset of type DNIN_set
        elif isinstance(index, slice):
            x = DNIN_set(self.container[index])
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
        if isinstance(otherList, LC6_neuronClass.DNinputNeuron):
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
        if isinstance(otherList, LC6_neuronClass.DNinputNeuron):
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

    # Sets total DNright Synapse Count
    def _DNrightSynapses(self):
        curSyn = 0
        for item in self:
            curSyn += item.DNrightsynapseCount
        return curSyn

    # returns the number of neurons in the current group
    def _getNumNeurons(self):
        numNeurons = len(self)
        return numNeurons

    # returns the percentCount of any constructed DNIN_set (if not == 99.99%: probably a bug in code); also sets the initial percent total
    # synapses for each individual neuron object, and then checks whether or not their PTS is not zero, so as to avoid resetting to percent
    # synapses of current group
    def _setPercentTotalSynapses(self):
        percentCount = 0
        for item in self:
            if item.percentTotalSynapse != 0:
                item.percentCurrentGroup = item.DNrightsynapseCount / self.AllDNrightSynapses
                percentCount += item.percentTotalSynapse
            elif self.AllDNrightSynapses == 0:
                item.percentTotalSynapse = 0
                percentCount += item.percentTotalSynapse
            else:
                item.percentTotalSynapse = item.DNrightsynapseCount / self.AllDNrightSynapses
                percentCount += item.percentTotalSynapse
        return percentCount

    def avg(self):
        myAvgLst = []
        myAvg = 0
        for i in self:
            myAvgLst.append(i.DNrightsynapseCount)
        myAvg = stat.mean(myAvgLst)
        return myAvg

    def med(self):
        myMedLst = []
        myMed = 0
        for i in self:
            myMedLst.append(i.DNrightsynapseCount)
        myMed = stat.median(myMedLst)
        return myMed

    # provides all neurons in the set with a list of x,y,z coordinates for their respective soma attributes. not part of builder because it can be computationally heavy (i.e. many server requests so slow)
    def updateSomata(self):
        for i in self:
            if i.soma is None:
                i.soma = i.getSomaNode()
            else:
                continue
        self.varCheck.append('soma')
        return self

    # input is an object of type DNIN_set and result is population of the skeletonNodes attribute for each DNinput neuron in the set
    def updateSkeletonNodes(self):
        for i in self:
            if i.skeletonNodes is None:
                i.getSkeletonNodes()
            else:
                continue
        self.varCheck.append('skeletonNodes')
        return self

    def getConnectors(self):
        myBranches = ['lateral', 'medial', 'anterior', 'soma tract']
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
            if 'Postsynaptic to LPLC1' in neuron.annotations:
                myLPLC1List.append(str(neuron.skeletonID))
            if 'postsynaptic to LPC1' in neuron.annotations:
                myLPC1List.append(str(neuron.skeletonID))

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
                '''for item in c:
                    if item in myLPLC1List:
                        d[item] = b[item]['skids'][str(i.skeletonID)][4]
                        countOfLPLC1SynapsesOntoMyNeuron += d[item]
                i.postsynapticToLPLC1 = countOfLPLC1SynapsesOntoMyNeuron'''

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

            ''' #for item in c:
                  #  if item in myLPC1List:
                 #       d[item] = b[item]['skids'][str(i.skeletonID)][4]
                #        countOfLPC1SynapsesOntoMyNeuron += d[item]
               # i.postsynapticToLPC1 = countOfLPC1SynapsesOntoMyNeuron'''

        self.varCheck.append('partners')
        return self

    def makeJSONPlain(self):
        additionalInfo = outputAllInfo(self)
        JN.autoSaveJSONFlatColor(self, additionalInfo)
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

    def getAllDNINSynByBranch(self):
        if self.connectorInfo is None:
            self.getConnectors()
        branches = ['soma tract', 'medial', 'anterior', 'lateral']
        DNsynapses = self.connectorInfo
        tempCount = 0
        for i in self:
            i.getConnectorIDs()
            for item in branches:
                for x in i.connectorIDs:
                    if x in DNsynapses[item]:
                        tempCount += 1
                        i.synLocation[x] = i.connectorIDs[x]
                i.synapsesByBranch[item] = tempCount
                tempCount = 0

        self.varCheck.append('synByBranch')
        return self

    def combineAllSynLocations(self):
        mySet = self
        AllSyn = {}
        count = 0
        if bool(mySet[0].synLocation) == False:
            self.getAllDNINSynByBranch()
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
            df = pandas.read_csv('C:/Users/polskyj/myCode/RCode/newTest/{}.csv'.format(selection),
                                 converters={"connectorID": int, 'X': float, 'Y': float, 'Z': float, 'Cluster': int})
        else:
            df = pandas.read_csv('C:/Users/polskyj/myCode/RCode/newTest/AllDNrightSynapses8ClustersWithSKID.csv',
                                 converters={"connectorID": int, 'X': float, 'Y': float, 'Z': float, 'Cluster': int})
        for index, row in df.iterrows():
            self[int(row['skeletonID'])].DNrightSynapticClusters.append(row['Cluster'])
        self.organizeSynClusters()
        self.varCheck.append('clusters')
        return self

    # creates a dict to fill the DNrightSynapticClusters attribute of each neuron which has the possible cluster numbers as its keys and the count of synapses in those clusters as its values
    def organizeSynClusters(self):
        for i in self:
            myClusters = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}
            myClusterKeys = list(myClusters.keys())
            for item in i.DNrightSynapticClusters:
                myClusters[str(int(item))] += 1
            i.DNrightSynapticClusters = myClusters
        return self

    '''
    def importSubClusters(self):
        df=pandas.read_csv('C:/Users/polskyj/myCode/RCode/newTest/BothIDsAndBothClusters.csv',converters={"connectorID":int, 'X':float,'Y':float, 'Z':float, 'Cluster':int, 'subCluster':int})
        for index, row in df.iterrows():    
            self[int(row['skeletonID'])].DNrightSynapticClusters.append(row['Cluster'], row['subCluster'])
        #self.organizeSynClusters()
        return'''

    # returns a list of neurons that provide synaptic output in the given number of clusters
    def getAllNeuronsByNumClusters(self, numClusters):
        myClusterNeurons = self
        for i in self:
            clusterCount = 0
            for item in i.DNrightSynapticClusters:
                if i.DNrightSynapticClusters[item] > 0:
                    clusterCount += 1
            if clusterCount != numClusters:
                myClusterNeurons -= i
            clusterCount = 0
        myNewSet = subSetBuilder(myClusterNeurons)
        if self.groupName is not None:
            myNewSet.groupName = self.groupName + 'in{}DNsynapticClusters'.format(numClusters)
        else:
            myNewSet.groupName = 'in{}DNsynapticClusters'.format(numClusters)
        return myNewSet

        # takes as input a list of cluster numbers, for which all neurons with synapses in those clusters will be returned

    def chooseNeuronsBySynCluster(self, clusterList):
        newList = []
        for i in self:
            myVar = False
            for clusterNum in clusterList:
                if i.DNrightSynapticClusters[str(clusterNum)] != 0:
                    myVar = True
                    if myVar is True:
                        newList.append(i)
                        break
        myNeurons = subSetBuilder(newList)
        return myNeurons

    def importSubClusters(self, fileName=None):
        if 'clusters' not in self.varCheck:
            self.importClusters()
        if fileName is None:
            fileName = 'BothIDsAndBothClusters'
        fileAddress = 'C:/Users/polskyj/myCode/RCode/newTest/{}.csv'.format(fileName)
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
        mySetSynCount = self.AllDNrightSynapses
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
            qs[c]['average_synapse_count'] = tempVar.avg()
            qs[c]['median_synapse_count'] = tempVar.med()
            qs[c]['all_DNright_Synapses'] = tempVar.AllDNrightSynapses
            qs[c]['percent of all {} synapses on DNright'.format(self.groupName)] = (
                        tempVar.AllDNrightSynapses / mySetSynCount)

            tempVar = None
            c += 1
        tempVar = subBySynGT(myTempSet, a[c - 1])
        tempVar = sortBySynH2L(tempVar)
        c = 4
        for i in tempVar:
            i.quantile = qNames[c]
        qs[c]['synapse_Threshold'] = tempVar[0].DNrightsynapseCount
        qs[c]['number_Neurons'] = tempVar.numNeurons
        qs[c]['average_synapse_count'] = tempVar.avg()
        qs[c]['median_synapse_count'] = tempVar.med()
        qs[c]['all_DNright_Synapses'] = tempVar.AllDNrightSynapses
        qs[c]['percent of all {} synapses on DNright'.format(self.groupName)] = (
                    tempVar.AllDNrightSynapses / mySetSynCount)

        return qs



# call this to build a DNIN_set from all DNright input neurons
def builder():
    mySet = DNIN_set(np.array(LC6_neuronClass.builder()))
    #mySet.myDN = GetAnnotationsByID.getDNType(SKID)
    return mySet


def buildFromSkidList(myList):
    mySet = DNIN_set(np.array(LC6_neuronClass.buildFromSkidList(myList)))
    return mySet


# sorts neurons from low to high synapse counts
def sortBySynL2H(mySet):
    L2H = sorted(mySet, key=LC6_neuronClass.DNinputNeuron.getDNrightsynapse)
    mySortedList = subSetBuilder(L2H)
    if mySet.groupName != None:
        mySortedList.groupName = mySet.groupName
    return mySortedList


# sorts neurons from low to high synapse counts
def sortBySynH2L(mySet):
    H2L = sorted(mySet, key=LC6_neuronClass.DNinputNeuron.getDNrightsynapse, reverse=True)
    mySortedList = subSetBuilder(H2L)
    if mySet.groupName != None:
        mySortedList.groupName = mySet.groupName
    return mySortedList


# returns a subset based upon annotation: mySet = DNIN_set instance, annotation = string annotation, annotation can also be a list of annotation strings
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
    if mySet.myDN is not None:
        a.myDN = mySet.myDN
    print("There are {} neurons with annotation {}: \n".format(len(a), a.groupName))
    return a


# returns a subset based upon annotation that neurons do NOT have: mySet = DNIN_set instance, annotation = string annotation
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


# returns a subset based upon synCount: mySet = DNIN_set instance, synNumber = Number of Synapses(or less) that you want results to have
def subBySynLT(mySet, synNumber):
    myNewSet = []
    for item in mySet:
        if item.DNrightsynapseCount <= synNumber:
            myNewSet.append(item)
            continue
    x = subSetBuilder(myNewSet)
    if mySet.groupName != None:
        x.groupName = str(mySet.groupName) + "with" + str(synNumber) + "synapses"
    print("{} of these neurons have {} or less synapses \n".format(len(myNewSet), synNumber))
    return x


# returns a subset based upon synCount: mySet = DNIN_set instance, synNumber = Number of Synapses(or greater) that you want results to have
def subBySynGT(mySet, synNumber):
    myNewSet = []
    for item in mySet:
        if item.DNrightsynapseCount >= synNumber:
            myNewSet.append(item)
            continue
    x = subSetBuilder(myNewSet)
    if mySet.groupName != None:
        x.groupName = str(mySet.groupName) + "with" + str(synNumber) + "synapses"
    print("{} of these neurons have {} or more synapses \n".format(len(myNewSet), synNumber))
    return x


# used by other functions to transform resulting data types into DNIN_set type
'''def subSetBuilder(fullSet, oldSet = None):
    mySubSet = DNIN_set(np.array(fullSet))
    if isinstance(oldSet, DNIN_set):
        for i in vars(oldSet):
            myI = getattr(oldSet, i)
            if myI is not None:
                setattr(mySubSet, i, myI)                        
        return mySubSet
    else:
        return mySubSet'''
'''def subSetBuilder(fullSet, oldSet = None):
    mySubSet = DNIN_set(np.array(fullSet))
    if isinstance(oldSet, DNIN_set):
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
    mySubSet = DNIN_set(np.array(fullSet))
    if isinstance(fullSet, DNIN_set):
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

    # old codethat was formerly part of subSetBuilder


# unusued consider deleting
def sliceBuilder(aSet):
    print(aSet)
    newSet = DNIN_set(np.array(aSet))
    return newSet


# Unused - consider deleting
def _getSynCount(self):
    mySynCount = 0
    for item in self:
        print("item", item)
        mySynCount += self[item].DNrightsynapseCount
        return mySynCount


def totalSynapseCount(neurons):
    totalSynapseCount = int()
    for i in neurons:
        totalSynapseCount += neurons[i].DNrightsynapseCount
    return totalSynapseCount


from scipy.stats.mstats import mquantiles


def quantiles(mySet):
    mySyns = []
    for i in mySet:
        mySyns.append(i.DNrightsynapseCount)
    myQuant = mquantiles(mySyns, prob=[0.2, 0.4, 0.5, 0.6, 0.8])
    return myQuant


from sklearn.cluster import KMeans


def getMyKMeans(mySet):
    mySyns = []
    for i in mySet:
        mySyns.append(i.DNrightsynapseCount)
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
    mySetSynCount = mySet.AllDNrightSynapses
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
        myAdditionalInfo += "\n quantile with <= {} synapses onto DN:  \n      - {} neurons in this quantile \n     -average number of synapses: {} \n     -median number of synapses: {} \n      - total number of synapses onto DN in this quantile: {} \n     - % of all {} synapses onto DN: {} \n".format(
            a[c], tempVar.numNeurons, tempVar.avg(), tempVar.med(), tempVar.AllDNrightSynapses, mySet.groupName,
            (tempVar.AllDNrightSynapses / mySetSynCount))
        tempVar = None
        c += 1
    tempVar = subBySynGT(myTempSet, a[c - 1])
    myBigSet[c] = tempVar
    myAdditionalInfo += "\n quantile with > {} synapses onto DN:  \n      - {} neurons in this quantile \n     -average number of synapses: {} \n     -median number of synapses: {} \n      - total number of synapses onto DN in this quantile: {} \n     - % of all {} synapses onto DN: {}".format(
        a[c - 1], tempVar.numNeurons, tempVar.avg(), tempVar.med(), tempVar.AllDNrightSynapses, mySet.groupName,
        (tempVar.AllDNrightSynapses / mySetSynCount))
    for i in myBigSet:
        i.groupName = mySet.groupName
        # myAdditionalInfo += "\n quantile {} synapses or less: \n      - {} neurons in this quantile \n     -average number of synapses: {} \n     -median number of synapses: {} \n      - %LPLC2 synapses: {}".format(a[myBigSet.index(i)], i.numNeurons, i.avg, i.med)
    JN.autoSaveJSONFlatColor(myBigSet, myAdditionalInfo)
    return myBigSet


def outputAllInfo(mySet):
    myInfo = ""
    myInfo += str(mySet.groupName) + '\n'
    myInfo += "number: " + str(mySet.numNeurons) + '\n'
    myInfo += "DN synapse count: " + str(mySet.AllDNrightSynapses) + '\n'
    myInfo += "%total DN synapses: " + str(mySet.percentTotalSynapses) + '\n'
    myInfo += "quantiles used: " + str(quantiles(mySet)) + '\n'
    return myInfo


def appendNonDNIN(mySet, annotation):
    testList = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation)
    curSKIDs = []
    for i in mySet:
        curSKIDs.append(i.skeletonID)
    for item in testList:
        if item not in curSKIDs:
            myNeuron = LC6_neuronClass.buildSingleCell(int(item))
            mySet += myNeuron
    return mySet


def appendNonDNIN2(mySet, annotation):
    testList = GetAnnotationsRemoveExtraneousInfo.getListOfSkID_int(annotation)
    curSKIDs = []
    for i in mySet:
        curSKIDs.append(i.skeletonID)
    for item in testList:
        if item not in curSKIDs:
            myNeuron = LC6_neuronClass.buildSingleCellQuick(int(item))
            mySet += myNeuron
    return mySet
