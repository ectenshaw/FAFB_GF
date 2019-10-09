#converts current subgroup into a json that can be opened by catmaid

import MyCustomDNNeuronClass
import CustomNeuronClassSet as CN
import json
import os
import colour
import datetime
now = datetime.datetime.now()
import clusteringAlgorithms as CA

def makeJson(mySet):
    aListOfNeurons = []
    for item in mySet:
        mySKID = item.skeletonID
        aNeuron = {
        "skeleton_id": mySKID,
        "color": "#00eee5",
        "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON

#call this function to save json file to computer;  work on naming protocol(if not annotations, etc...)     
def makeJsonFile(mySet):
    if type(mySet) is not CN.DNIN_set:
        mySet = CN.buildFromSkidList(mySet)
    myData = makeJson(mySet)
    copyNumber = 0
    if mySet.groupName is None:
        nameVar = mySet.AllDNrightSynapses
        fileName = str(nameVar) + "synapses"
    else:
        fileName = mySet.groupName
    myFile = str(fileName)
    myFileCheck = myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        #myFile += str(copyNumber)
        myFileCheck = myFile + '_' +str(copyNumber) + '.json'
    myFile += '.json'
    c = open(myFile, 'w')
    c.write(myData)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return



def makeJsonSynapticColorGradient(mySet):
    mySet = CN.sortBySynL2H(mySet)
    aListOfNeurons = []
    #numInSet = mySet.numNeurons
    #myIncrement = int(16777000 / numInSet)
    red = colour.Color("red")
    blue = colour.Color("blue")
    allColors = list(blue.range_to(red, mySet.numNeurons + 1))
    curColor = 0
    for item in mySet:
        mySKID = item.skeletonID
        synCount = item.DNrightsynapseCount
        curColor += 1
        myColor = allColors[curColor].hex_l
        item.curColor = myColor
        aNeuron = {
        "skeleton_id": mySKID,
        "color": myColor,
        "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON


def autoSaveJSON(mySet):
    myData = makeJsonSynapticColorGradient(mySet)
    copyNumber = 0
    if mySet.groupName is None:
        nameVar = mySet.AllDNrightSynapses
        myFileName = str(nameVar) + "synapses"
    else:
        myFileName = mySet.groupName
    saveCount = 0
    pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs"
    if mySet.myDN is not None:
        DNpath = mySet.myDN
    pathVar += '/{}'.format(DNpath)
    while (saveCount <=1):
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
        c.write(myData)
        c.close()  
        print("JSON saved as {}".format(str(myFile)))

        myBaseFile += "AdditionalInfo.txt"
        additionalInfo = getGeneralAdditionalInfo(mySet)
        d = open(myBaseFile, 'w')
        d.write(additionalInfo)
        d.close()
        pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs"
        if mySet.myDN is not None:
            DNpath = mySet.myDN
        pathVar += '/{}'.format(DNpath)
        saveCount += 1
    
    return


#returns json file of set of neurons colored by gradient according to quantile of synapses
def makeJsonFileSynColGrad(mySet):
    myData = makeJsonSynapticColorGradient(mySet)
    copyNumber = 0
    if mySet.groupName is None:
        nameVar = mySet.AllDNrightSynapses
        fileName = str(nameVar) + "synapses"
        #fileName = mySet[0].skeletonID + mySet[1].skeletonID + mySet[2].skeletonID
    else:
        fileName = mySet.groupName
    myFile = "colorGradient" + str(fileName)
    myFileCheck = "colorGradient" + myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFile += str(copyNumber)
        myFileCheck = myFile + '.json'
    myFile += '.json'
    c = open(myFile, 'w')
    c.write(myData)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return


#same as above except with autosave - use this one
def autoSaveJSONColorGrad(mySet):
    myData = makeJsonSynapticColorGradient(mySet)
    copyNumber = 0
    if mySet.groupName is None:
        nameVar = mySet.AllDNrightSynapses
        myFileName = str(nameVar) + "synapses"
    else:
        myFileName = mySet.groupName
    saveCount = 0
    pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs"
    DNpath = ''
    if mySet.myDN is not None:
        DNpath = mySet.myDN
    pathVar += '/{}'.format(str(DNpath))
    while (saveCount <1):
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
        c.write(myData)
        c.close()  
        print("JSON saved as {}".format(str(myFile)))

        myBaseFile += "AdditionalInfo.txt"
        additionalInfo = getAdditionalInfo(mySet)
        d = open(myBaseFile, 'w')
        d.write(additionalInfo)
        d.close()
        pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs"
        if mySet.myDN is not None:
            DNpath = str(mySet.myDN)
        pathVar += ("/{}".format(str(DNpath)))
        saveCount += 1
    
    return

#C:/Users/polskyj/Dropbox (HHMI)/CAT-CardLab-Files/AllScriptingResults
#C:/Users/tenshawe/Desktop/pyCharmOutputs

def getAdditionalInfo(mySet):
    myQuant = str(CN.quantiles(mySet))
    myInfo = str(mySet.groupName) +"\n"+ "number: " + str(mySet.numNeurons) +"\n"+ "number of DNright synapses: " + str(mySet.AllDNrightSynapses)+ "\n" +  "percent total DNright synapses: " + str(mySet.percentTotalSynapses) +"\n" + "quantiles used for distribution: " + myQuant + "\n"
    return myInfo

def getGeneralAdditionalInfo(mySet):
    myInfo = str(vars(mySet))
    return myInfo

#def setPathForSave():
   # myPath = 'C:\Users\polskyj\{}\'.format(mySet.groupName) 
  #  myLPLC2Path = 'C:\Users\polskyj\LPLC2_DataAnalytics\' 
 #   fileName = str(now.year) + str(now.month) + str(now.day)
    
#    pathWithName = os.path.join(myPath, fileName+".json")

def makeJsonColorGradientSetOfSets(mySuperSet):
    myData = makeJsonSynapticColorGradient(mySet)
    copyNumber = 0
    if mySet.groupName is None:
        nameVar = mySet.AllDNrightSynapses
        fileName = str(nameVar) + "synapses"
        #fileName = mySet[0].skeletonID + mySet[1].skeletonID + mySet[2].skeletonID
    else:
        fileName = mySet.groupName
    myFile = "colorGradient" + str(fileName)
    myFileCheck = "colorGradient" + myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFile += str(copyNumber)
        myFileCheck = myFile + '.json'
    myFile += '.json'
    c = open(myFile, 'w')
    c.write(myData)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return    

#use with customneuronclassset makedistributedgroupsbycolor function when no gradient is desired
def makeJsonFlatColor(mySet):
    red = colour.Color("red")
    blue = colour.Color("blue")
    yellow = colour.Color("yellow")
    white = colour.Color("white")
   # colorList = [red, yellow, blue]
    colorList = list(blue.range_to(red, len(mySet)))
    aListOfNeurons = []
    count = 0
    for item in mySet:
        for i in item:
            mySKID = i.skeletonID
            aNeuron = {
            "skeleton_id": mySKID,
            "color": colorList[count].hex_l,
            "opacity": 1
            }
            aListOfNeurons.append(aNeuron)
        count += 1
    
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON




#returns the same json from above function for use in other functions
def autoSaveJSONFlatColor(mySet, additionalInfo):
    myData = makeJsonFlatColor(mySet)
    copyNumber = 0
    myFileName = ''
    myGroupName = mySet[0].groupName
    if myGroupName is None:
        myGroupName = mySet[1].groupName
    if myGroupName is None:
        myGroupName = 'ReWriteGroupNameCode'
    if isinstance(myGroupName, list) or len(myGroupName)>34:
        if 'clustering' in myGroupName:
            myFileName = "clustering"
        else:
            myFileName = 'NoGradient'        
    else:
        for i in mySet:
            if i.groupName != None:
                if 'clustering' in i.groupName:
                    myFileName = 'i.groupName'
                    break
                else:
                    myFileName += i.groupName + 'NoGradient'
                    break
    pathVar = 'C:/Users/polskyj/Dropbox (HHMI)/CAT-CardLab-Files/AllScriptingResults'
    # if mySet.myDN is not None:
    #     DNpath = mySet.myDN
    # pathVar += '/{}'.format(DNpath)
    saveCount = 0
    windowsErrorCharacters = '[],\"\''
    for x in windowsErrorCharacters:
        myFileName = myFileName.replace(x,'')
    if ' ' in myFileName:    
        myFileName = myFileName.replace(' ', '')
    if '-' in myFileName:
        myFileName = myFileName.replace('-', '_')
    
    while (saveCount <=1):
        if len(myFileName) > 164:
            myFileName = myFileName[len(myFileName)-21:len(myFileName)]
        myPath = '{}/{}/'.format(pathVar, str(myFileName))       

        
        myPath = os.path.normpath(myPath)

        if not os.path.isdir(myPath):
            os.makedirs(myPath)

        fileName = str(now.year) + str(now.month) + str(now.day)
        fileName += myFileName
        finalFileName = os.path.join(myPath, fileName)


        myFile = str(finalFileName)
        myFileCheck = myFile + '.json'
        myBaseFile = myFile
        while os.path.isfile(myFileCheck) == True:
            copyNumber += 1
            myFileCheck = myFile + '_' + str(copyNumber)
            myBaseFile = myFileCheck
            myFileCheck += '.json'
        myFile = myFileCheck
        c = open(myFile, 'w')
        c.write(myData)
        c.close()  
        print('JSON saved as {}'.format(str(myFile)))

        myBaseFile += 'AdditionalInfo.txt'
        additionalInfo = additionalInfo
        d = open(myBaseFile, 'w')
        d.write(additionalInfo)
        d.close()
        pathVar = 'C:/Users/tenshawe/Desktop/pyCharmOutputs'
        # if mySet.myDN is not None:
        #     DNpath = mySet.myDN
        # pathVar += '/{}'.format(DNpath)
        saveCount += 1
    return myData

#input should be a subset of neurons that will be run through various clustering algorithms: input should be a json with desired colors and a list containing sub-lists of sets of DN input neurons to be used to set opacity (usually by DNright synapse count
def makeJsonOpacity(myNeurons):
    somaCluster = CA.clusterSomata(myNeurons)
    myJSON = makeJsonFlatColor(somaCluster)
    myJSON = json.loads(myJSON)
    tempOpacity = 0
    myOpacityList = []
    myOs = (1.0/len(somaCluster))
    count = len(somaCluster)
    while count > 0:
        myOpacityList.append(myOs * count)
        count -= 1

    synapticCluster = CN.makeDistributedGroupsByColor(myNeurons)
    newCount = len(myOpacityList) - 1
    tempSkidList = []
    while newCount >= 0:
        for item in synapticCluster:
            for i in item:
                tempSkidList.append(i.skeletonID)
            for x in myJSON:
                if x['skeleton_id'] in tempSkidList:
                    x['opacity'] = myOpacityList[newCount]
            tempSkidList = []
            newCount -= 1

    myJSON = json.dumps(myJSON)
    return myJSON

def makeJsonFileForOpacity(myData):
    copyNumber = 0
    fileName = "opacitySynapsesinSomacluster"
    myFile = str(fileName)
    myFileCheck = myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFile += str(copyNumber)
        myFileCheck = myFile + '.json'
    myFile += '.json'
    c = open(myFile, 'w')
    c.write(myData)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return

#call this function to save json file to computer;  work on naming protocol(if not annotations, etc...)     
def makePlainJSON(mySet):
    if type(mySet) is not CN.DNIN_set:
        mySet = CN.buildFromSkidList(mySet)
    myData = makeJson(mySet)
    copyNumber = 0
    if mySet.groupName is None:
        for i in mySet[0].annotations:
            if i in mySet[len(mySet)-2].annotations:
                nameVar = i
                fileName = str(nameVar)
            else: 
                nameVar = 'myFile'
                fileName = str(nameVar)
    else:
        fileName = mySet.groupName
    myFile = str(fileName)
    myFileCheck = myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        #myFile += str(copyNumber)
        myFileCheck = myFile + '_' +str(copyNumber) + '.json'
    myFile += '.json'
    c = open(myFileCheck, 'w')
    c.write(myData)
    c.close()
    print("JSON saved as {}".format(str(myFile)))
    return