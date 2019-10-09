import MyCustomDNNeuronClass as CC
import CustomNeuronClassSet as CS
import os
import csv
import datetime

now = datetime.datetime.now()


def makeCSV(mySet, formatType='saveGeneral'):
    formatTypeDict = {'saveClassSummary': saveClassSummary, 'saveSummary': saveSummary, 'saveGeneral': saveGeneral,
                      'saveGeneralSpecificAnnotations': saveGeneralSpecificAnnotations, 'saveWithSoma': saveWithSoma,
                      'saveWithSomaAndBranches': saveWithSomaAndBranches, 'saveWithSynLocation': saveWithSynLocation,
                      'saveSKIDwithXYZ': saveSKIDwithXYZ, 'saveSKIDWithSynClusters': saveSKIDWithSynClusters,
                      'saveLPLC2Quantiles': saveLPLC2Quantiles, 'saveGeneralWithQuantiles': saveGeneralWithQuantiles,
                      'saveSKIDwithXYZandColor': saveSKIDwithXYZandColor, 'saveDNp020411': saveDNp020411,
                      'saveSKIDwithColor': saveSKIDwithColor}
    copyNumber = 0
    if mySet.myDN is not None:
        nameVar = str(mySet.myDN)
        nameVar += formatType
        myFileName = str(nameVar)
    elif mySet.groupName is None:
        nameVar = formatType
        nameVar += 'AllDNrightinputNeurons'
        myFileName = str(nameVar)
    elif mySet.groupName is 'None':
        nameVar = formatType
        nameVar += 'AllDNrightinputNeurons'
        myFileName = str(nameVar)

    else:
        nameVar = ''
        myFileName = formatType
        myFileName += str(mySet.groupName)
    saveCount = 0
    DNvar = None
    pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/CSV"
    if mySet.myDN is not None:
        DNvar = mySet.myDN
        pathVar += "/{}".format(str(DNvar))
    myPath = "{}/{}/".format(pathVar, str(nameVar))
    myPath = os.path.normpath(myPath)

    if not os.path.isdir(myPath):
        os.makedirs(myPath)

    fileName = str(now.year) + str(now.month) + str(now.day)
    fileName += myFileName
    finalFileName = os.path.join(myPath, fileName)

    myFile = str(finalFileName)
    myFileCheck = myFile + ".csv"
    myBaseFile = myFile
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFileCheck = myFile + "_" + str(copyNumber)
        myBaseFile = myFileCheck
        myFileCheck += '.csv'
    myFile = myFileCheck
    args = [myFile, mySet]

    '''if formatType is 'saveGeneral':
        saveGeneral(args)
    else:
        #saveGeneralSpecificAnnotations(args)
        formatType(args)'''
    # formatType(args)
    formatTypeDict[formatType](args)

    return


def saveGeneral(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'annotations', 'percent total synapses'])
        for item in mySet:
            myWriter.writerow([item.neuronName, item.skeletonID, item.DNrightsynapseCount, item.annotations,
                               item.percentTotalSynapse])
    return


def saveSummary(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'classification'])
        for item in mySet:
            tempClass = None
            for i in item.annotations:
                if "putative" in i:
                    tempClass = i
            if tempClass is None:
                tempClass = "putative LPLC4 neuron"
            myWriter.writerow([item.neuronName, item.skeletonID, item.DNrightsynapseCount, tempClass])
    return


def saveClassSummary(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Classification', 'Number of Neurons', 'Number of GF1 Synapses', 'Percent Total GF1 Synapses',
             'Minimum Synapses', 'Maximum Synapses', 'Average Synapses', 'Median Synapses'])
        for i in mySet:
            myWriter.writerow(
                [i.classification, i.numNeurons, i.AllGF1Synapses, i.percentTotalSynapses, i.minSyn, i.maxSyn,
                 i.averageSyn, i.medianSyn])
    return


def saveGeneralSpecificAnnotations(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'percent total synapses', 'classification',
             'hemisphere', 'numLC4Syn', 'numLPLC2Syn', 'numLC6Syn'])
        for item in mySet:
            myWriter.writerow([item.neuronName, item.skeletonID, item.DNrightsynapseCount, item.percentTotalSynapse,
                               item.classification, item.hemisphere, item.postsynapticToLC4, item.postsynapticToLPLC2,
                               item.postsynapticToLC6])
    return


def saveWithSoma(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'percent total synapses', 'classification',
             'hemisphere', 'numLC4Syn', 'numLPLC2Syn', 'numLC6Syn', 'soma_X', 'soma_Y', 'soma_Z'])
        for item in mySet:
            myWriter.writerow([item.neuronName, item.skeletonID, item.DNrightsynapseCount, item.percentTotalSynapse,
                               item.classification, item.hemisphere, item.postsynapticToLC4, item.postsynapticToLPLC2,
                               item.postsynapticToLC6, item.soma[0], item.soma[1], item.soma[2]])
    return


def saveWithSomaAndBranches(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'percent total synapses', 'classification',
             'hemisphere', 'numLC4Syn', 'numLPLC2Syn', 'numLC6Syn', 'numLPLC1Syn', 'numLPC1Syn', 'lateral branch',
             'medial branch', 'anterior branch', 'soma tract', 'soma_X', 'soma_Y', 'soma_Z'])
        for item in mySet:
            myWriter.writerow([item.neuronName, item.skeletonID, item.DNrightsynapseCount, item.percentTotalSynapse,
                               item.classification, item.hemisphere, item.postsynapticToLC4, item.postsynapticToLPLC2,
                               item.postsynapticToLC6, item.postsynapticToLPLC1, item.postsynapticToLPC1,
                               item.synapsesByBranch['lateral'], item.synapsesByBranch['medial'],
                               item.synapsesByBranch['anterior'], item.synapsesByBranch['soma tract'], item.soma[0],
                               item.soma[1], item.soma[2]])
    return


def saveAnnotationsAsColumns(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        annotationCheck = {}
        secondLevel = {}
        myAnnotations = []
        for item in mySet:
            for annotation in item.annotations:
                if annotation not in myAnnotations:
                    myAnnotations.append(annotation)

                secondLevel[annotation] = 1
            annotationCheck[item.neuronName] = secondLevel
            secondLevel = {}
        myNeur = list(annotationCheck.keys())

        for item in myAnnotations:
            for i in myNeur:
                if item not in annotationCheck[i]:
                    annotationCheck[i][item] = 0
        fields = ['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'percent total synapses']
        fields += myAnnotations
        # myWriter.writerow(['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'percent total synapses', myAnnotations])
        myWriter.writerow(fields)
        for item in mySet:
            myWriter.writerow([item.neuronName, item.skeletonID, item.DNrightsynapseCount, item.percentTotalSynapse,
                               annotationCheck[item.neuronName]])
    return


def combineAllSynLocations(aSet):
    mySet = aSet
    AllSyn = {}
    count = 0
    for i in mySet:
        for z in i.synLocation:
            x = z
            while x in AllSyn:
                x = str(z)
                x += str(count)
                x = int(x)
                count += 1
            AllSyn[x] = i.synLocation[z]
            AllSyn[x].append(i.skeletonID)
    return AllSyn


def saveWithSynLocation(args):
    myFile = args[0]
    mySet = args[1]
    mySyns = combineAllSynLocations(mySet)
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['connectorID', 'X', 'Y', 'Z', 'skeletonID'])
        for item in mySyns:
            myWriter.writerow([item, mySyns[item][0], mySyns[item][1], mySyns[item][2], mySyns[item][3]])
    return


# Use for exporting LPLC2 average LP point coordinates
def saveSKIDwithXYZ(args):
    myFile = args[0]
    mySet = args[1]
    myAvgCoordinates = mySet.LPLC2_LP_Filter()
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['skeletonID', 'X', 'Y', 'Z'])
        for item in myAvgCoordinates:
            myWriter.writerow([item, myAvgCoordinates[item][0], myAvgCoordinates[item][1], myAvgCoordinates[item][2]])
    return


# same as above but CSV contains specific color for each LPCL2
def saveSKIDwithXYZandColor(args):
    myFile = args[0]
    mySet = args[1]
    if "LPLC2" in mySet[0].classification:
        myAvgCoordinates = mySet.LPLC2_LP_Filter()
    elif "putative LC4 neuron" in mySet[0].classification:
        myAvgCoordinates = mySet.LC4_LO_Filter()
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['skeletonID', 'X', 'Y', 'Z', 'color'])
        for item in myAvgCoordinates:
            myWriter.writerow([item, myAvgCoordinates[item][0], myAvgCoordinates[item][1], myAvgCoordinates[item][2],
                               myAvgCoordinates[item][3]])
    return


def saveSKIDwithColor(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['skeletonID', 'synapse_count', 'color'])
        for item in mySet:
            myWriter.writerow([item.skeletonID, item.DNrightsynapseCount, item.curColor])
    return


def saveSKIDWithSynClusters(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['skeletonID', '1', '2', '3', '4', '5', '6', '7', '8'])
        for item in mySet:
            myWriter.writerow([item.skeletonID, item.DNrightSynapticClusters['1'], item.DNrightSynapticClusters['2'],
                               item.DNrightSynapticClusters['3'], item.DNrightSynapticClusters['4'],
                               item.DNrightSynapticClusters['5'], item.DNrightSynapticClusters['6'],
                               item.DNrightSynapticClusters['7'], item.DNrightSynapticClusters['8']])
    return


def saveLPLC2Quantiles(args):
    myFile = args[0]
    myStarterSet = args[1]
    mySet = myStarterSet.makeQuantiles()
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Quantile', 'synapse_Threshold', 'number_Neurons', 'average_synapse_count', 'median_synapse_count',
             'all_DNright_Synapses', 'percent of all LPLC2 synapses on DNright'])
        for item in mySet:
            myWriter.writerow([item, item['synapse_Threshold'], item['number_Neurons'], item['average_synapse_count'],
                               item['median_synapse_count'], item['all_DNright_Synapses'],
                               item['percent of all LPLC2 synapses on DNright']])
    return


def saveGeneralWithQuantiles(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['Neuron Name', 'skeletonID', 'DNright Synapse Count', 'percent total synapses', 'quantile'])
        for item in mySet:
            myWriter.writerow(
                [item.neuronName, item.skeletonID, item.DNrightsynapseCount, item.percentTotalSynapse, item.quantile])
    return


def makeCSV_LC6partners(mySet, formatType='saveLC6_Connectors'):
    formatTypeDict = {'saveGeneral': saveGeneral, 'saveLC6_Connectors': saveLC6_Connectors}
    copyNumber = 0

    nameVar = formatType
    nameVar += 'AndPostsynapticPartners'
    myFileName = str(nameVar)
    saveCount = 0
    DNvar = None
    pathVar = "C:/Users/polskyj/AllScriptingResults/CSV"
    myPath = "{}/{}/".format(pathVar, str(nameVar))
    myPath = os.path.normpath(myPath)

    if not os.path.isdir(myPath):
        os.makedirs(myPath)

    fileName = str(now.year) + str(now.month) + str(now.day)
    fileName += myFileName
    finalFileName = os.path.join(myPath, fileName)

    myFile = str(finalFileName)
    myFileCheck = myFile + ".csv"
    myBaseFile = myFile
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFileCheck = myFile + "_" + str(copyNumber)
        myBaseFile = myFileCheck
        myFileCheck += '.csv'
    myFile = myFileCheck
    args = [myFile, mySet]
    formatTypeDict[formatType](args)
    return


def saveLC6_Connectors(args):
    myFile = args[0]
    mySet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['connector_id', 'LC6_skeleton_id', 'X', 'Y', 'Z', 'LC6_treenode_id', 'Postsynaptic_Partner1',
                           'cable_length(nm)', 'Postsynaptic_Partner2', 'cable_length(nm)', 'Postsynaptic_Partner3',
                           'cable_length(nm)', 'Postsynaptic_Partner4', 'cable_length(nm)', 'Postsynaptic_Partner5',
                           'cable_length(nm)', 'Postsynaptic_Partner6', 'cable_length(nm)', 'Postsynaptic_Partner7',
                           'cable_length(nm)', 'Postsynaptic_Partner8', 'cable_length(nm)'])
        for item in mySet:
            myRow = [mySet[item][1], mySet[item][0], mySet[item][2], mySet[item][3], mySet[item][4], mySet[item][5]]
            partnerNumber = 0
            for i in mySet[item][6]:
                myRow.extend([i, mySet[item][6][i]])
                partnerNumber += 1
            filler = 22 - len(myRow)
            myRow.extend(['n/a'] * filler)
            myWriter.writerow(myRow)
    return


def fNew(i, conList):
    mytest = list(conList[i][6].keys())
    return mytest


def saveDNp020411(args):
    myFile = args[0]
    mySet = args[1]
    myInfo = mySet.getConnectorsInfo()
    neuronNames = {}
    DNs = [7138957, 6958818, 5349447]
    for neuron in mySet:
        neuronNames[str(neuron.skeletonID)] = neuron.neuronName
    cleanedInfo = {}
    for item in myInfo:
        mytest = fNew(item, myInfo)

        if 7138957 in mytest or 6958818 in mytest or 5349447 in mytest:
            cleanedInfo[item] = myInfo[item]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(['connector_id', 'X', 'Y', 'Z', 'NeuronName', 'skeletonID', 'DNp02', 'DNp04', 'DNp11'])
        for con in cleanedInfo:
            aName = str(cleanedInfo[con][0])
            for abc in DNs:
                if abc in cleanedInfo[con][6].keys():
                    cleanedInfo[con].append(True)
                else:
                    cleanedInfo[con].append(False)

            myWriter.writerow(
                [cleanedInfo[con][1], cleanedInfo[con][2], cleanedInfo[con][3], cleanedInfo[con][4], neuronNames[aName],
                 cleanedInfo[con][0], cleanedInfo[con][7], cleanedInfo[con][8], cleanedInfo[con][9]])
    return


def saveClassSummary(args):
    myFile = args[0]
    mySuperSet = args[1]
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        myWriter.writerow(
            ['Classification', 'Number of Neurons', 'Number of GF1 Synapses', 'Percent Total GF1 Synapses',
             'Minimum Synapses', 'Maximum Synapses', 'Average Synapses', 'Median Synapses'])
        for i in mySuperSet:
            myWriter.writerow(
                [i.classification, i.numNeurons, i.AllGF1Synapses, i.percentTotalSynapses, i.minSyn, i.maxSyn,
                 i.averageSyn, i.medianSyn])
    return
