import MyCustomGFNeuronClass as MC
import CustomNeuronClassSet as CS
import exportToCSV as e2c
import jsonNeurons as JN


mySet = CS.builder()

#gets soma node xyz
mySet.updateSomata()

#gets all node coordinate points of every neuron in set - don't run unless this info is necessary
#mySet.updateSkeletonNodes()

#connector xyz location and partner info
mySet.getConnectors()

#Get partner info (visual partners)
mySet.getNumPartnersBySkid()

#Breakdown syn count by branch
mySet.getAllGFINSynByBranch()

mySet.findNeuropils()
mySet.findBranchDistributions()

mySet.combineAllSynLocations()

#export CSV with cleansed data
e2c.makeCSV(mySet, "saveWithAll")

#export CSV with cleansed data and every possible annotation as a column

e2c.makeCSV(mySet, "saveWithAllAndAnnotations")




def AL(aset):
    myAnnotations =[]
    for i in aset:
        for item in i.annotations:
            if item not in myAnnotations:
                myAnnotations.append(item)
    return myAnnotations

def CL(aset):
    myClasses =[]
    for i in aset:
        if i.classification not in myClasses:
                myClasses.append(i.classification)
    return myClasses

test = CL(mySet)



thisResponse = requests.post('https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/',  auth=auth, data = {'skeleton_ids':4947529})
myData = json.loads(thisResponse.content)

for i in myRealTotal['incoming']:
    for item in myRealTotal['incoming'][i]['skids']:
        for con in myRealTotal['incoming'][i]['skids'][item]:
            if myRealTotal['incoming'][i]['skids'][item].index(con) != 4 and con >0:
                print(myRealTotal['incoming'].keys())

for i in myData['connectors']:
    groundTruth.append(i[0])
for i in groundTruth:
    if i not in AllGFconnectors:
        missingConnectors.append(i)


import ClassificationNeuralNetwork as CNN
myClasses = CNN.layer0(mySet)

comClass = CNN.layer1(classTypeGroups=CNN.layer0(mySet))

newTest = CNN.layer2(CNN.layer1(classTypeGroups = CNN.layer0(mySet)))

visList = []
for i in mySet:
    if i.classification != 'putative LC4 neuron' and i.classification != "LPLC2":
        for item in i.annotations:
            if 'LC6' in item or 'LPLC' in item or 'LLP' in item or 'LC4' in item or 'LC11' in item and 'presynaptic' not in item:
                visList.append(i)
                break



superSet = []
for i in list(newTest.keys()):
    tempVar = ""
    tempVar += str(i)
    for item in list(newTest[i].keys()):
        tempVar = str(i) + str(item)
        for obj in list(newTest[i][item].keys()):
            tempVar = str(i) +str(item) + str(obj)
            globals()['{}'.format(tempVar)] = CS.buildFromSkidList(tempVar)
            superSet.append(tempVar)



import MyCustomGFNeuronClass as MC
import CustomNeuronClassSet as CS
import exportToCSV as e2c

mySet = CS.builder()

import ClassificationNeuralNetwork as CNN
newTest = CNN.layer2(CNN.layer1(classTypeGroups = CNN.layer0(mySet)))


import json
import os
import sys
import datetime
now = datetime.datetime.now()
for classification in newTest:
    for commissure in newTest[classification]:
        for cbr in newTest[classification][commissure]:
            aListOfNeurons = []
            for neuron in newTest[classification][commissure][cbr]:
                mySKID = neuron.skeletonID
                aNeuron = {
                    "skeleton_id": mySKID,
                    "color": '0090ff',
                    "opacity": 1
                }
                aListOfNeurons.append(aNeuron)
            myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
            copyNumber = 0
            myFileName = str(classification) +str(commissure) + str(cbr)
            indexCount = 0
            for i in myFileName:
                if i == ':':
                    new = myFileName[:indexCount] + '-' + myFileName[(indexCount + 1):]
                    myFileName = new
                    indexCount +=1
                else:
                    indexCount += 1
            saveCount = 0
            pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/FunnelFilterGrouping"
            while (saveCount <= 1):
                myPath = "{}/{}/".format(pathVar, str(myFileName))
                myPath = os.path.normpath(myPath)
                if not os.path.isdir(myPath):
                    os.makedirs(myPath)

                fileName = str(now.year) + str(now.month) + str(now.day)
                fileName += myFileName
                finalFileName = os.path.join(myPath, fileName)

                myFile = str(finalFileName)
                myFileCheck = myFile + ".json"
                myBaseFile = myFile
                while os.path.isfile(myFileCheck) == True:
                    copyNumber += 1
                    myFileCheck = myFile + "_" + str(copyNumber)
                    myBaseFile = myFileCheck
                    myFileCheck += '.json'
                myFile = myFileCheck
                c = open(myFile, 'w')
                c.write(myJSON)
                c.close()
                print("JSON saved as {}".format(str(myFile)))
                pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/FunnelFilterGrouping"
                saveCount += 1

newTESTsubset = CS.subSetBuilder(newTest['Unclassified']['GC']['PCBR'])


classOfInterest = ['Unclassified GF input neuron - type 68', 'Unclassified GF input neuron - type 67', 'Unclassified GF input neuron - type 62', 'Unclassified GF input neuron - type 58', 'Unclassified GF input neuron - type 57', 'Unclassified GF input neuron - type 54', 'Unclassified GF input neuron - type 51', 'Unclassified GF input neuron - type 5 ','Unclassified GF input neuron - type 4 ','Unclassified GF input neuron - type 30', 'Unclassified GF input neuron - type 2b', 'Unclassified GF input neuron - type 29', 'Unclassified GF input neuron - type 28', 'Unclassified GF input neuron - type 21', 'Unclassified GF input neuron - type 2 ','Unclassified GF input neuron - type 19', 'Unclassified GF input neuron - type 14']


testing123 = CS.createGroupByAnnotation(mySet, classOfInterest)
JN.autoSaveJSON(testing123,thisJsonFunction = JN.makeJsonFlatColorByClass)



for i in test:
    globals()['{}'.format(i)] = CS.createGroupByClassification(mySet,str(i))
myDict = {}
for i in test:
    myDict[i] = globals()['{}'.format(i)]
for item in myDict:
    JN.autoSaveJSON(myDict[item], thisJsonFunction=JN.makeJsonFlatColorByClass)


presynPartners = {}
for i in mySet:
    presynPartners[i.skeletonID] =



import seaborn as sns; sns.set(color_codes=True)
iris = sns.load_dataset("iris")

import pandas as pd

data = pd.read_csv(
    'C:/Users/tenshawe/Desktop/pyCharmOutputs/CSV/saveWithAllAllGF1inputNeurons/2018921saveWithAllAllGF1inputNeurons.csv'
)