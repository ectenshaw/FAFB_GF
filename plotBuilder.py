import requests
import json
import os
import datetime
now = datetime.datetime.now()
import config
import pandas as pd
token = config.token
project_id = config.project_id
import plotly
plotly.tools.set_credentials_file(username='CardLab', api_key='NsYwbHlFACg2IWkRUJvs')
from collections import defaultdict
import MyCustomGFNeuronClass as GF
import CustomNeuronClassSet as CS
import colour
import csv
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
from collections import OrderedDict


#takes a long time to run
#Run only once
#returns dictonary of dicts by connector ids
#connector ID = key
#value is a dict:
#   value dict keys: 'connector_id', 'x', 'y', 'z', 'confidence', 'partners(list'
#   partners list: list of presyn and postsyn partners for CID


def createCytoscapeCSV(mySet, classification):
    copyNumber = 0
    fileName = classification + " cytoscape"
    pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/CSV/Cytoscape/NEW"
    #myPath = os.path.normpath(myPath)
    finalFileName = os.path.join(pathVar, fileName)
    myFile = str(finalFileName)
    myFileCheck = myFile + ".csv"
    myBaseFile = myFile
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        myFileCheck = myFile + "_" + str(copyNumber)
        myBaseFile = myFileCheck
        myFileCheck += '.csv'
    myFile = myFileCheck
    classSet = []
    for neuron in mySet:
        if classification in neuron.annotations:
            classSet.append(neuron)
    classSet = CS.GFIN_set(classSet)
    with open(myFile, 'w', newline='') as outfile:
        myWriter = csv.writer(outfile)
        row0 = ['Neuron Name', 'Skeleton ID', 'GF1 Synapse Count', 'Target', 'Classification', 'Soma Location']
        myWriter.writerow(row0)
        for neuron in classSet:
            if neuron.synapsesByBranch['anterior'] > 0:
                antRow = [neuron.neuronName, neuron.skeletonID, neuron.synapsesByBranch['anterior'],
                          "Anterior", neuron.classification, neuron.IpsiContraMid]
                myWriter.writerow(antRow)
            if neuron.synapsesByBranch['medial'] > 0:
                medRow = [neuron.neuronName, neuron.skeletonID, neuron.synapsesByBranch['medial'],
                          "Medial", neuron.classification, neuron.IpsiContraMid]
                myWriter.writerow(medRow)
            if neuron.synapsesByBranch['lateral'] > 0:
                latRow = [neuron.neuronName, neuron.skeletonID, neuron.synapsesByBranch['lateral'],
                          "Lateral", neuron.classification, neuron.IpsiContraMid]
                myWriter.writerow(latRow)
            if neuron.synapsesByBranch['soma tract'] > 0:
                somaRow = [neuron.neuronName, neuron.skeletonID, neuron.synapsesByBranch['soma tract'],
                          "Soma Tract", neuron.classification, neuron.IpsiContraMid]
                myWriter.writerow(somaRow)
            if neuron.synapsesByBranch['descending tract'] > 0:
                descRow = [neuron.neuronName, neuron.skeletonID, neuron.synapsesByBranch['descending tract'],
                          "Descending Tract", neuron.classification, neuron.IpsiContraMid]
                myWriter.writerow(descRow)
    return


def getSynInfo(mySet):
    allSyn = mySet.connectorInfo.get('medial') + mySet.connectorInfo.get('lateral') + mySet.connectorInfo.get('soma tract') + mySet.connectorInfo.get('anterior') + mySet.connectorInfo.get('descending tract')
    allInfo = getConnectPartners(allSyn)
    return allInfo

#builds set; high to low GF1 synapses
#builds allInfo connectors
def buildSetGetInfo():
    mySet = CS.builder()
    #mySet = CS.sortBySynL2H(mySet)
    # gets soma node xyz
    # mySet.updateSomata()
    # gets all node coordinate points of every neuron in set - don't run unless this info is necessary
    # mySet.updateSkeletonNodes()
    # connector xyz location and partner info
    mySet.getConnectors()
    # Get partner info (visual partners)
    #mySet.getNumPartnersBySkid()
    # Breakdown syn count by branch
    mySet.getAllGFINSynByBranch()
    mySet.findNeuropils()
    mySet.findBranchDistributions()
    #mySet.combineAllSynLocations()
    allInfo = getSynInfo(mySet)
    mySet.findIpsiContraMid()
    mySet.findBiUni()
    mySet.findModality()
    mySet.findMorphology()
    return mySet, allInfo

#returns list of neurons with more than 100 synapses onto GF
def topInputs(mySet):
    topInputs = []
    for neuron in mySet:
        if neuron.GF1synapseCount > 99:
            topInputs.append(neuron)
    return topInputs


#returns connected partners of ConnectorID
#runs as subfunction -- don't need to call
def getConnectPartners(connectorIDArray):
    newDict = {}
    for connectorID in connectorIDArray:
        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/{}/'.format(connectorID)
        )
        myR = json.loads(response.content.decode('utf-8'))
        #print(myR)
        newDict[connectorID] = myR
    return newDict

#returns same format as distribution synapses
#(25854587, {'connector_id': 25854587, 'x': 473092.0, 'y': 205574.0, 'z': 146480.0, 'confidence': 5, 'partners': [{'link_id': 7944040, 'partner_id': 25854568, 'confidence': 5, 'skeleton_id': 4947529, 'relation_id': 8, 'relation_name': 'postsynaptic_to'}, {'link_id': 7944039, 'partner_id': 11542963, 'confidence': 5, 'skeleton_id': 2642963, 'relation_id': 14, 'relation_name': 'presynaptic_to'}]})
def getBranchOnlySynapses(mySet, allInfo, branch):
    branchInfo = mySet.connectorInfo.get(branch)
    branchPartners = []
    for item in allInfo.items():
        if item[0] in branchInfo:
            branchPartners.append(item)
    return branchPartners

def branchPreSynPartnersSkid(mySet, allInfo, branch):

    branch_syn = getBranchOnlySynapses(mySet, allInfo, branch)

    branch_presyn_partners = []
    for item in branch_syn:
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                skid = partner['skeleton_id']
                branch_presyn_partners.append(skid)

    return branch_presyn_partners


from scipy import ndimage
import numpy as np

def find_clusters(array):
    clustered = np.empty_like(array)
    unique_vals = np.unique(array)
    cluster_count = 0
    for val in unique_vals:
        labelling, label_count = ndimage.label(array == val)
        for k in range(1, label_count + 1):
            clustered[labelling == k] = cluster_count
            cluster_count += 1
    return clustered, cluster_count



def createBranchTrace(mySet, allInfo, branch, distribution, rgb):
    presynParts = branchPreSynPartnersSkid(mySet, allInfo, branch)
    partners = []
    for i in mySet:
        if i.distribution is distribution:
            if i.skeletonID in presynParts:
                partners.append(i)
    distPreSynSkid = []
    for i in partners:
        distPreSynSkid.append(i.skeletonID)
    x_vals = []
    y_vals = []
    z_vals = []
    synapses = getBranchOnlySynapses(mySet, allInfo, branch)
    for item in synapses:
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                skid = partner['skeleton_id']
        if skid in distPreSynSkid:
            x_vals.append(item[1]['x'])
            y_vals.append(item[1]['y'])
            z_vals.append(item[1]['z'])
        branchTrace = go.Scatter3d(
        x= x_vals,
        y= y_vals,
        z= z_vals,
        mode='markers',
        marker=dict(
        size=5,
        color= rgb),
        name=distribution)
    return branchTrace

#returns list of neurons in mySet that have the distribution given.
#ex: 'Anterior' gives anterior only
def distributionList(mySet, distribution):
    distributionOnly = []
    for i in mySet:
        if i.distribution == distribution:
            distributionOnly.append(i)

    return distributionOnly

#returns list of neurons in mySet that have the annotation given
#ex: by neuropil
def annotationList(mySet, annotation):
    annotationOnly = []
    for i in mySet:
        if annotation in i.annotations:
            annotationOnly.append(i)

    return annotationOnly

#returns SKID of distribution list
def distributionSkid(mySet, distribution):
    distributionSkid = []
    distributionOnly = distributionList(mySet, distribution)
    for item in distributionOnly:
        distributionSkid.append(item.skeletonID)

    return distributionSkid

#returns SKID of annotation list
def annotationSkid(mySet, annotation):
    annotationSkid = []
    annotationOnly = annotationList(mySet, annotation)
    for item in annotationOnly:
        annotationSkid.append(item.skeletonID)

    return annotationSkid

#returns tuple of connectorID, {cID, x, y, z, conf, partners)
#includes ALL partners of connector ID
#MUST use another formula to retrieve relevant skeletons
#Can be used for XYZ coordinates
#params: mySet - gf set, allInfo - returned list from 'getSynInfo', distribution - string
def distributionSynapses(mySet, allInfo, distribution):
    # keys = synapse id
    # values = [x,y,z].

    distribution_skid = distributionSkid(mySet, distribution)

    distribution_syn = []
    for item in allInfo.items():
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                if partner['skeleton_id'] in distribution_skid:
                    distribution_syn.append(item)

    return distribution_syn

#returns tuple of connectorID, (CID, X,Y,Z, conf, partners)
#Use for XYZ coordinates
#params: mySet - gf set, allInfo - returned list from 'getSynInfo', annotation - string
def annotationSynapses(mySet, allInfo, annotation):
    # keys = synapse id
    # values = [x,y,z].
    annotation_skid = annotationSkid(mySet, annotation)
    annotation_syn = []
    for item in allInfo.items():
        for it in allInfo.items():
            for partner in it[1]['partners']:
                if partner['relation_name'] == 'presynaptic_to':
                    if partner['skeleton_id'] in annotation_skid:
                        annotation_syn.append(item)

    return annotation_syn

#returns XYZ coordinates of synapse and a CSV for R to cluster
def distributionXYZ(mySet, allInfo, distribution, filename):
    distributionXYZ = {}

    distribution_syn = distributionSynapses(mySet, allInfo, distribution)
    x_vals = []
    y_vals = []
    z_vals = []

    for item in distribution_syn:
        x_vals.append(item[1]['x'])
        y_vals.append(item[1]['y'])
        z_vals.append(item[1]['z'])

    normx = [float(i) / sum(x_vals) for i in x_vals]
    normy = [float(i) / sum(y_vals) for i in y_vals]
    normz = [float(i) / sum(z_vals) for i in z_vals]

    count = 0
    for item in distribution_syn:
        cid = item[0]
        xyz = []
        xyz.append(normx[count])
        xyz.append(normy[count])
        xyz.append(normz[count])
        skid = item[1]['partners'][1]['skeleton_id']
        xyz.append(skid)
        distributionXYZ.update({cid: xyz})
        df = pd.DataFrame(distributionXYZ)
        df = df.transpose()
        df.to_csv(filename)
        count = count + 1

    return distributionXYZ

def annotationXYZ(mySet, allInfo, annotation, filename):
    annotationXYZ = {}

    annotation_syn = annotationSynapses(mySet, allInfo, annotation)
    x_vals = []
    y_vals = []
    z_vals = []

    for item in annotation_syn:
        x_vals.append(item[1]['x'])
        y_vals.append(item[1]['y'])
        z_vals.append(item[1]['z'])

    normx = [float(i) / sum(x_vals) for i in x_vals]
    normy = [float(i) / sum(y_vals) for i in y_vals]
    normz = [float(i) / sum(z_vals) for i in z_vals]

    count = 0
    for item in annotation_syn:
        cid = item[0]
        xyz = []
        xyz.append(normx[count])
        xyz.append(normy[count])
        xyz.append(normz[count])
        skid = item[1]['partners'][1]['skeleton_id']
        xyz.append(skid)
        annotationXYZ.update({cid: xyz})
        df = pd.DataFrame(annotationXYZ)
        df = df.transpose()
        df.to_csv(filename)
        count = count + 1

    return annotationXYZ

#returns list of presynaptic partners from synapes
#synapes attained from distribution
def distributionPreSynPartnersSkid(mySet, allInfo, distribution):
    distribution_syn = distributionSynapses(mySet, allInfo, distribution)

    distribution_presyn_partners = []
    for item in distribution_syn:
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                skid = partner['skeleton_id']
                distribution_presyn_partners.append(skid)

    return distribution_presyn_partners

#returns list of presynaptic partners from synapses
#synapses attained from annotation
def annotationPreSynPartnersSkid(mySet, allInfo, annotation):

    annotation_syn = annotationSynapses(mySet, allInfo, annotation)

    annotation_presyn_partners = []
    for item in annotation_syn:
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                skid = partner['skeleton_id']
                annotation_presyn_partners.append(skid)
    return annotation_presyn_partners

#takes list from presynPartnersSkid
#takes list from text file generated by R
def createClusterDict(presynSKIDList, clusterList):
    clusterDict = {}
    count = len(clusterList)

    for i in range(0, count):
        clusterDict[i] = (presynSKIDList[i], clusterList[i])

    return clusterDict

#takes in cluster dictionary and returns list of lists
#each sublist is the cluster number followed by the neurons in that cluster
#cluster 0 is "noise"
def getClusters(clusterDict):

    SKIDs = []
    clusterList = []

    for i in clusterDict:
        SKIDs.append(clusterDict[i][0])
        clusterList.append(clusterDict[i][1])

    num = max(clusterList)

    cluster = [[] for k in range(0, num + 1)]

    for i in clusterDict.items():
        cluster[i[1][1]].append(i[1][0])

    return cluster

#creates a list of cluster#: neurons in cluster
def getNeuronsFromClusters(mySet, clusterList):

    clusterNeurons = {}
    leng = len(clusterList)
    keys = []
    for i in range(0, leng):
        keys.append(i)


    clusterNeurons = {k: [] for k in keys}
    count = 0
    for i in clusterList:
        for j in i:
            for k in mySet:
                if k.skeletonID == j:
                    clusterNeurons[count].append(k)
        count = count + 1

    return clusterNeurons

#creates a json of neurons from a given cluster number
#run after gerNeuronFromClusters
def makeClusterJson(clusterNeurons, cluster, fileName):

    clus = clusterNeurons[cluster]

    editClus = []

    for i in clus:
        if i not in editClus:
            editClus.append(i)

    aListOfNeurons = []
    for item in editClus:
        mySKID = item.skeletonID
        aNeuron = {
            "skeleton_id": mySKID,
            "color": "#00eee5",
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    copyNumber = 0
    nameVar = fileName
    myFile = str(fileName)
    pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/JSON"
    myPath = "{}/".format(pathVar)
    myPath = os.path.normpath(myPath)
    if not os.path.isdir(myPath):
        os.makedirs(myPath)
    print(myPath, fileName)
    finalFileName = os.path.join(myPath)
    myFile = str(finalFileName)
    myFileCheck = myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        # myFile += str(copyNumber)
        myFileCheck = myFile + '_' + str(copyNumber) + '.json'
    myFile += '.json'
    c = open(myFile, 'w')
    c.write(myJSON)
    c.close()
    print("JSON saved as {}".format(str(myFile)))

    return editClus

#creates a trace of the given distribution using the given RGB value
#used for plotting in plotly
# distributions in use: (12/4/18)
# Anterior
# AnteriorDescending
# AnteriorLateral
# AnteriorLateralSoma
# AnteriorMedial
# AnteriorMedialLateral
# AnteriorMedialLateralSoma
# AnteriorMedialSoma
# Descending
# Lateral
# LateralSoma
# Medial
# MedialDescending
# MedialLateral
# MedialLateralSoma
# MedialSoma
# Soma
def getDistributionTrace(mySet, allInfo, distribution, rgb):
    x_vals = []
    y_vals = []
    z_vals = []
    synapses = distributionSynapses(mySet, allInfo, distribution)
    for item in synapses:
        x_vals.append(item[1]['x'])
        y_vals.append(item[1]['y'])
        z_vals.append(item[1]['z'])
    distribTrace = go.Scatter3d(
        x= x_vals,
        y= y_vals,
        z= z_vals,
        mode='markers',
        marker=dict(
            size=5,
            color= rgb),
        name=distribution)
    return distribTrace



#data MUST be in brackets [] even if just one item
def createPlotlyPlot(data, name):
    layout = go.Layout(
        title=name,
        legend=dict(x=-.05, y=0.5),
        scene=dict(
            xaxis=dict(
                title='x Axis'),
            yaxis=dict(
                title='y Axis'),
            zaxis=dict(
                title='z Axis')),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        )
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=name)

    return

#creates a JSON of a branch's gradient
def makeBranchColorGradient(mySet, allInfo, branch):
    connectIDs = mySet.connectorInfo.get(branch)
    preSKID = []

    for item in allInfo.items():
        cid = item[0]
        if cid in connectIDs:
            for partner in item[1]['partners']:
                if partner['relation_name'] == 'presynaptic_to':
                    preSKID.append(partner['skeleton_id'])
    neurons = []
    for i in mySet:
        if i.skeletonID in preSKID:
            neurons.append(i)
    #for i in neurons:
        #if i.classification == 'Unclassified GF input neuron - Fragment':
     #       neurons.remove(i)
    red = colour.Color("red")
    blue = colour.Color("blue")
    H2L = sorted(neurons, key=GF.GFinputNeuron.getGF1synapse, reverse=True)
    allColors = list(red.range_to(blue, len(H2L)))
    aListOfNeurons = []
    curColor = 0
    for item in H2L:
        mySKID = item.skeletonID
        synCount = item.GF1synapseCount
        myColor = allColors[curColor].hex_l
        item.curColor = myColor
        aNeuron = {
            "skeleton_id": mySKID,
            "color": myColor,
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
        curColor += 1

    copyNumber = 0
    fileName = branch + "H2L"
    nameVar = fileName
    myFile = str(fileName + "H2L.json")
    pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/Gradients/Branch"
    myPath = "{}/".format(pathVar)
    myPath = os.path.normpath(myPath)
    if not os.path.isdir(myPath):
        os.makedirs(myPath)
    finalFileName = os.path.join(myPath, fileName)
    myFile = str(finalFileName)
    myFileCheck = myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        # myFile += str(copyNumber)
        myFileCheck = myFile + '_' + str(copyNumber) + '.json'
    myFile += '.json'
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    c = open(myFile, 'w')
    c.write(myJSON)
    c.close()
    return aListOfNeurons

#creates a JSON of a distribution's gradient
def makeDistributionColorGradient(mySet, allInfo, distribution):
    neurons = []
    for i in mySet:
        if i.distribution == distribution:
            neurons.append(i)
    #for i in neurons:
    #    if i.classification == 'Unclassified GF input neuron - Fragment':
     #       neurons.remove(i)
    red = colour.Color("red")
    blue = colour.Color("blue")
    H2L = sorted(neurons, key=GF.GFinputNeuron.getGF1synapse, reverse=True)
    allColors = list(red.range_to(blue, len(H2L)))
    aListOfNeurons = []
    curColor = 0
    for item in H2L:
        mySKID = item.skeletonID
        synCount = item.GF1synapseCount
        myColor = allColors[curColor].hex_l
        item.curColor = myColor
        aNeuron = {
            "skeleton_id": mySKID,
            "color": myColor,
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
        curColor += 1

    copyNumber = 0
    fileName = distribution + "H2L"
    nameVar = fileName
    myFile = str(fileName + "H2L.json")
    pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/Gradients/Distribution"
    myPath = "{}/".format(pathVar)
    myPath = os.path.normpath(myPath)
    if not os.path.isdir(myPath):
        os.makedirs(myPath)
    finalFileName = os.path.join(myPath, fileName)
    myFile = str(finalFileName)
    myFileCheck = myFile + ".json"
    while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        # myFile += str(copyNumber)
        myFileCheck = myFile + '_' + str(copyNumber) + '.json'
    myFile += '.json'
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    c = open(myFile, 'w')
    c.write(myJSON)
    c.close()
    return aListOfNeurons

"""
type2a = types['Unclassified GF input neuron - type 2a']
H2L = sorted(type2a, key=GF.GFinputNeuron.getGF1synapse, reverse=True)
allColors = list(red.range_to(blue, len(H2L) + 1))
aListOfNeurons = []
curColor = 0
for item2 in H2L:
        mySKID = item2.skeletonID
        synCount = item2.GF1synapseCount
        myColor = allColors[curColor].hex_l
        item2.curColor = myColor
        classif = item2.classification
        aNeuron = {
            "skeleton_id": mySKID,
            "color": myColor,
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
        curColor += 1
fileName = classif + "H2L"
pathVar = "C:/Users/tenshawe/Desktop/pyCharmOutputs/Gradients/Synapses"
myPath = "{}/".format(pathVar)
myPath = os.path.normpath(myPath)
if not os.path.isdir(myPath):
    os.makedirs(myPath)
finalFileName = os.path.join(myPath, fileName)
myFile = str(finalFileName)
myFileCheck = myFile + ".json"
while os.path.isfile(myFileCheck) == True:
        copyNumber += 1
        # myFile += str(copyNumber)
        myFileCheck = myFile + '_' + str(copyNumber) + '.json'
myFile += '.json'
myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
c = open(myFile, 'w')
c.write(myJSON)
c.close()
"""

"""

SC.makeBranchColorGradient(mySet, allInfo, "lateral")
SC.makeBranchColorGradient(mySet, allInfo, "medial")
SC.makeBranchColorGradient(mySet, allInfo, "anterior")
SC.makeBranchColorGradient(mySet, allInfo, "descending tract")
SC.makeBranchColorGradient(mySet, allInfo, "soma tract")

SC.makeDistributionColorGradient(mySet, allInfo, 'Anterior')
SC.makeDistributionColorGradient(mySet, allInfo, 'AnteriorDescending')
SC.makeDistributionColorGradient(mySet, allInfo, 'AnteriorLateral')
SC.makeDistributionColorGradient(mySet, allInfo, 'AnteriorLateralSoma')
SC.makeDistributionColorGradient(mySet, allInfo, 'AnteriorMedial')
SC.makeDistributionColorGradient(mySet, allInfo, 'AnteriorMedialLateral')
SC.makeDistributionColorGradient(mySet, allInfo, 'AnteriorMedialLateralSoma')
SC.makeDistributionColorGradient(mySet, allInfo, 'AnteriorMedialSoma')
SC.makeDistributionColorGradient(mySet, allInfo, 'Descending')
SC.makeDistributionColorGradient(mySet, allInfo, 'Lateral')
SC.makeDistributionColorGradient(mySet, allInfo, 'LateralSoma')
SC.makeDistributionColorGradient(mySet, allInfo, 'Medial')
SC.makeDistributionColorGradient(mySet, allInfo, 'MedialDescending')
SC.makeDistributionColorGradient(mySet, allInfo, 'MedialLateral')
SC.makeDistributionColorGradient(mySet, allInfo, 'MedialLateralSoma')
SC.makeDistributionColorGradient(mySet, allInfo, 'MedialSoma')
SC.makeDistributionColorGradient(mySet, allInfo, 'Soma')

"""

'''
aListOfNeurons = []
Anterior1 = []
AnteriorDescending1 =[] 
AnteriorLateral1 = []
AnteriorLateralSoma1 = []
AnteriorMedial1 = []
AnteriorMedialLateral1 = []
AnteriorMedialLateralSoma1 = []
AnteriorMedialSoma1 = []
Descending1 = []
Lateral1 = []
LateralSoma1 = []
Medial1 = []
MedialDescending1 = []
MedialLateral1 = []
MedialLateralSoma1 = []
MedialSoma1 = []
Soma1 = []

for item in mySet:
    mySKID = item.skeletonID
    if item.distribution is "Anterior":
        item.curColor = 'rgb(220,20,60)'
        Anterior1.append(item)
    elif item.distribution is "AnteriorDescending":
        item.curColor = "rgb(0,100,0)"
        AnteriorDescending1.append(item)
    elif item.distribution is "AnteriorLateral":
        item.curColor = "rgb(0,255,255)"
        AnteriorLateral1.append(item)
    elif item.distribution is "AnteriorLateralSoma":
        item.curColor = "rgb(255,0,255)"
        AnteriorLateralSoma1.append(item)
    elif item.distribution is "AnteriorMedial":
        item.curColor = "rgb(107,142,35)"
        AnteriorMedial1.append(item)
    elif item.distribution is "AnteriorMedialLateral":
        item.curColor = "rgb(0,255,0)"
        AnteriorMedialLateral1.append(item)
    elif item.distribution is "AnteriorMedialLateralSoma":
        item.curColor = "rgb(0,0,255)"
        AnteriorMedialLateralSoma1.append(item)
    elif item.distribution is "AnteriorMedialSoma":
        item.curColor = "rgb(139,69,19)"
        AnteriorMedialSoma1.append(item)
    elif item.distribution is "Descending":
        item.curColor = "rgb(70,130,180)"
        Descending1.append(item)
    elif item.distribution is "Lateral":
        item.curColor = "rgb(255,165,0)"
        Lateral1.append(item)
    elif item.distribution is "LateralSoma":
        item.curColor = "rgb(147,112,219)"
        LateralSoma1.append(item)
    elif item.distribution is "Medial":
        item.curColor = "rgb(255,255,0)"
        Medial1.append(item)
    elif item.distribution is "MedialDescending":
        item.curColor = "rgb(218,165,32)"
        MedialDescending1.append(item)
    elif item.distribution is "MedialLateral":
        item.curColor = "rgb(105,105,105)"
        MedialLateral1.append(item)
    elif item.distribution is "MedialLateralSoma":
        item.curColor = "rgb(128,0,128)"
        MedialLateralSoma1.append(item)
    elif item.distribution is "MedialSoma":
        item.curColor = "rgb(250,128,114)"
        MedialSoma1.append(item)
    elif item.distribution is "Soma":
        item.curColor = "rgb(255,255,255)"
        Soma1.append(item)
    aNeuron = {
        "skeleton_id": mySKID,
        "color": item.curColor,
        "opacity": 1
    }
    aListOfNeurons.append(aNeuron)
allBranches = json.dumps(aListOfNeurons, separators=(', \n', ': '))
alljsonfile = open("AllInputs.json", 'w')
alljsonfile.write(allBranches)
alljsonfile.close()

Medz = []
Antz = []
Latz = []
Descz = []
Somz = []
Medz = AnteriorMedial1 + AnteriorMedialLateral1 + AnteriorMedialLateralSoma1 + AnteriorMedialSoma1 + Medial1 + MedialDescending1 + MedialLateral1 + MedialLateralSoma1 + MedialSoma1
Antz = AnteriorDescending1 + Anterior1 + AnteriorLateral1 + AnteriorLateralSoma1 + AnteriorMedial1 + AnteriorMedialLateral1 + AnteriorMedialLateralSoma1 + AnteriorMedialSoma1
Latz = Lateral1 + AnteriorLateral1 + AnteriorLateralSoma1 + AnteriorMedialLateral1 + AnteriorMedialLateralSoma1 + LateralSoma1 + MedialLateral1 + MedialLateralSoma1
Descz = Descending1 + AnteriorDescending1 + MedialDescending1
Somz = Soma1 + AnteriorLateralSoma1 + AnteriorMedialLateralSoma1 + MedialLateralSoma1 + LateralSoma1 + MedialSoma1
neuronList = []
for i in Anterior1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j1 = json.dumps(neuronList, separators=(', \n', ': '))
jf1 = open("Anterior.json", 'w')
jf1.write(j1)
jf1.close()
neuronList = []
for i in AnteriorDescending1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j2 = json.dumps(neuronList, separators=(', \n', ': '))
jf2 = open("Anterior_Descending.json", 'w')
jf2.write(j2)
jf2.close()
neuronList = []
for i in AnteriorLateral1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf3 = open("Anterior_Lateral.json", 'w')
jf3.write(j3)
jf3.close()
neuronList = []
for i in AnteriorLateralSoma1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf4 = open("Anterior_Lateral_Soma.json", 'w')
jf4.write(j3)
jf4.close()
neuronList = []
for i in AnteriorMedial1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf5 = open("Anterior_Medial.json", 'w')
jf5.write(j3)
jf5.close()
neuronList = []
for i in AnteriorMedialLateral1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf6 = open("Anterior_Medial_Lateral.json", 'w')
jf6.write(j3)
jf6.close()
neuronList = []
for i in AnteriorMedialLateralSoma1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf7 = open("Anterior_Medial_Lateral_Soma.json", 'w')
jf7.write(j3)
jf7.close()
neuronList = []
for i in AnteriorMedialSoma1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf8 = open("Anterior_Medial_Soma.json", 'w')
jf8.write(j3)
jf8.close()
neuronList = []
for i in Descending1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf9 = open("Descending.json", 'w')
jf9.write(j3)
jf9.close()
neuronList = []
for i in Lateral1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf10 = open("Lateral.json", 'w')
jf10.write(j3)
jf10.close()
neuronList = []
for i in LateralSoma1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf11 = open("Lateral_Soma.json", 'w')
jf11.write(j3)
jf11.close()
neuronList = []
for i in Medial1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf12 = open("Medial.json", 'w')
jf12.write(j3)
jf12.close()
neuronList = []
for i in MedialDescending1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf13 = open("Medial_Descending.json", 'w')
jf13.write(j3)
jf13.close()
neuronList = []
for i in MedialLateral1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf14 = open("Medial_Lateral.json", 'w')
jf14.write(j3)
jf14.close()
neuronList = []
for i in MedialLateralSoma1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf15 = open("Medial_Lateral_Soma.json", 'w')
jf15.write(j3)
jf15.close()
neuronList = []
for i in MedialSoma1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf16 = open("Medial_Soma.json", 'w')
jf16.write(j3)
jf16.close()
neuronList = []
for i in Soma1:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
j3 = json.dumps(neuronList, separators=(', \n', ': '))
jf17 = open("Soma.json", 'w')
jf17.write(j3)
jf17.close()

neuronList = []
for i in Medz:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
    
medzjson= json.dumps(neuronList, separators=(', \n', ': '))
medjsonfile = open("MedialInputs.json", 'w')
medjsonfile.write(medzjson)
medjsonfile.close()

neuronList = []
for i in Antz:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
antjson = json.dumps(neuronList, separators=(', \n', ': '))
antjsonfile = open("AnteriorInputs.json", 'w')
antjsonfile.write(antjson)
antjsonfile.close()


neuronList = []
for i in Latz:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
latjson = json.dumps(neuronList, separators=(', \n', ': '))
latjsonfile = open("LateralInputs.json", 'w')
latjsonfile.write(latjson)
latjsonfile.close()


neuronList = []
for i in Descz:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
desczjson = json.dumps(neuronList, separators=(', \n', ': '))
desczjsonfile = open("DescendingInputs.json", 'w')
desczjsonfile.write(desczjson)
desczjsonfile.close()


neuronList = []
for i in Somz:
    aNeuron = {
        "skeleton_id": i.skeletonID,
        "color": i.curColor,
        "opacity": 1
    }
    neuronList.append(aNeuron)
somzjson = json.dumps(neuronList, separators=(', \n', ': '))
somzjsonfile = open("SomaInputs.json", 'w')
somzjsonfile.write(somzjson)
somzjsonfile.close()
'''

'''
noFrag = []
for i in mySet:
    if i.classification is not 'Unclassified GF input neuron - Fragment':
        noFrag.append(i)
        
for i in noFrag:
    if i.classification == 'Unclassified GF input neuron - Fragment':
        noFrag.remove(i)
        
NoFragH2L = sorted(noFrag, key=GF.GFinputNeuron.getGF1synapse, reverse=True)
allColors = list(red.range_to(blue, len(H2L) + 1))
aListOfNeurons = []
curColor = 0
for item in H2L:
    mySKID = item.skeletonID
    synCount = item.GF1synapseCount
    myColor = allColors[curColor].hex_l
    item.curColor = myColor
    aNeuron = {
        "skeleton_id": mySKID,
        "color": myColor,
        "opacity": 1
    }
    aListOfNeurons.append(aNeuron)
    curColor += 1
x_vals = []
y_vals = []
z_vals = []
pres = []
allConnect = []
for i in allInfo.items():
    allConnect.append(i)
    
FragSKID = []
for i in mySet:
    if i.classification == 'Unclassified GF input type - Fragment':
        FragSKID.append(i.skeletonID)
        
for i in mySet:
    if i.classification == 'Unclassified GF input neuron - Fragment':
        FragSKID.append(i.skeletonID)
        
FragSKID = []
for i in mySet:
    if i.classification == 'Unclassified GF input neuron - Fragment':
        FragSKID.append(i.skeletonID)
        
noFragConnect = []
for item in allConnect:
    for partner in item[1]['partners']:
        if partner['relation_name'] == 'presynaptic_to':
            if partner['skeleton_id'] not in FragSKID:
                noFragConnect.append(item)               
x_vals = []
y_vals = []
z_vals = []
pres = []
for item in noFragConnect:
    x_vals.append(item[1]['x'])
    y_vals.append(item[1]['y'])
    z_vals.append(item[1]['z'])
    for partner in item[1]['partners']:
        if partner['relation_name'] == 'presynaptic_to':
            pres.append(partner['skeleton_id'])
aListOfNeurons = []
curColor = 0
for item in NoFragH2L:
    mySKID = item.skeletonID
    synCount = item.GF1synapseCount
    myColor = allColors[curColor].hex_l
    item.curColor = myColor
    aNeuron = {
        "skeleton_id": mySKID,
        "color": myColor,
        "opacity": 1
    }
    aListOfNeurons.append(aNeuron)
    curColor += 1           
allColors = []
for item in pres:
    for item2 in aListOfNeurons:
        if item == item2.skeletonID:
            allColors.append(item2.curColor)            
layout = go.Layout(
        title= "NoFragAllH2L",
        legend=dict(x=-.05, y=0.5),
        scene=dict(
            xaxis=dict(
                title='x Axis'),
            yaxis=dict(
                title='y Axis'),
            zaxis=dict(
                title='z Axis')),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0))
H2LTrace = go.Scatter3d(
        x=x_vals,
        y=y_vals,
        z=z_vals,
        text=pres,
        mode='markers',
        marker=dict(
            size=5,
            color=allColors),
        name="NoFragAllH2L")
x_s = [401000, 550000, 401000, 550000, 401000, 550000, 401000, 550000]
y_s = [192000, 192000, 298000, 298000, 192000, 192000, 298000, 298000]
z_s = [40960, 40960, 40960, 40960, 222320, 222320, 222320, 222320]
Structure = go.Scatter3d(
    x=x_s,
    y=y_s,
    z=z_s,
    mode='markers',
    marker=dict(
        size=1,
        color="rgb(255,255,255)"),
    name="STRUCTURE")
fig = go.Figure(data=[Structure, H2LTrace], layout=layout)
py.plot(fig, filename= "AllNoFragH2L")
'''

'''
dataDict = defaultdict(list)
for i in mySet:
    key = i.classification
    if key in dataDict.keys():
        dataDict[key].append(i.GF1synapseCount)
    else:
        dataDict[key].append(i.GF1synapseCount)
keys = []
for i,v in dataDict.items():
    keys.append(i)
values = []
for i in dataDict.values():
    count = 0
    for nums in i:
        count = count + nums
    values.append(count)
import operator    
data = dict(zip(keys, values))
sortedData = sorted(data.items(),key=lambda x: x[1])
sortedD2 = sortedData[::-1]
sortedDict = dict(sortedD2)
keys = sortedDict.keys()
values = sortedDict.values()
keys = list(keys)
values = list(values)

lowDict = defaultdict(list)

trace1 = go.Bar(
    x=keys,
    y= values,
    name='Classification'
)
data = [trace1]
layout = go.Layout(
    barmode='group',
    margin=go.layout.Margin(
        b=200,
        r = 150
    ), 
    xaxis = dict(tickangle = 45)
)
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='BarTest')

lowtypes2 = defaultdict(list)
for i in t2:
    key = i.classification
    if key in lowtypes2.keys():
        lowtypes[key].append(i.GF1synapseCount)
    else:
        lowtypes[key].append(i.GF1synapseCount)
        
for i in t2:
    key = i.classification
    if key in lowtypes2.keys():
        lowtypes2[key].append(i.GF1synapseCount)
    else:
        lowtypes2[key].append(i.GF1synapseCount)
        
keys3 = []
for i,v in lowtypes2.items():
    keys3.append(i)
values3 = []
for i in lowtypes2.values():
    count = 0
    for nums in i:
        count = count + nums
    values3.append(count)
import operator    
data3 = dict(zip(keys3, values3))
sortedData3 = sorted(data3.items(),key=lambda x: x[1])
sortedD23 = sortedData3[::-1]
sortedDict3 = dict(sortedD23)
keys4 = sortedDict3.keys()
values4 = sortedDict3.values()
keys5 = list(keys4)
values5 = list(values4)
trace1 = go.Bar(
    x=keys2,
    y= values2,
    name='Classification'
)
trace2 = go.Bar(
    x=keys5,
    y= values5,
    name='Classification'
)
data = [trace1, trace2]
layout = go.Layout(
    barmode='group',
    margin=go.layout.Margin(
        b=200,
        r = 150
    ), 
    xaxis = dict(tickangle = 45)
)
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='LowInputsCompare')
x = synapes
data = [go.Histogram(x=x,
                     xbins =dict(size = 1),
                     marker=dict(line=dict(
                             color='rgb(0,0,0)',
                             width=2
                         )))]
py.plot(data, filename='basic histogram')
'''

"""
twoNeurons = defaultdict(list)
for k,v in dataDict.items():
    if len(v) == 2:
        twoNeurons[k].append(v)
        
for k, v in twoNeurons.items():
    for neuron in v:
        yellow = colour.Color("yellow")
        purple = colour.Color("purple")
        orange = colour.Color("orange")
        allColors = list(blue.range_to(red, len(neuron) + 1))
        curColor = 0
        synList = []
        colors = []
        for item in neuron:
            synList.append(item.GF1synapseCount)
            if "RIGHT HEMISPHERE" in item.annotations:
                item.curColor = "purple"
            elif "LEFT HEMISPHERE" in item.annotations:
                item.curColor = "orange"
            elif "RIGHT HEMISPHERE" not in item.annotations and "LEFT HEMISPHERE" not in item.annotations:
                item.curColor = "yellow"
            colors.append(item.curColor)

twoLowTrace = go.Bar(
    x = twoKeys,
    y = twoVals1,
    marker=dict(color="rgb(0,0,225)"),
    name = "Low Value"
)
twoHighTrace = go.Bar(
    x = twoKeys,
    y = twoVals2,
    marker=dict(color = "rgb(255,51,51)"),
    name = "High Value"
)
layout = go.Layout(
    barmode='group',
    margin=go.layout.Margin(
        b=200,
        r = 150
    ), 
    xaxis = dict(tickangle = 45)
)
data = [twoLowTrace, twoHighTrace]
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='Two Neuron Soma Comparison')
"""

'''
mySet = CS.sortBySynL2H(mySet)
dataDict = defaultdict(list)
singleNeuron = defaultdict(list)

for i in mySet:
    dataDict[i.classification].append(i)

for v in dataDict.values():
    if len(v) == 1:
        singleNeuron[v[0].classification].append(v)

GF1Syns = []
data = []
row = 1
column = 1
singleKeys = list(singleNeuron.keys())
singleVals = []
colors = []
for k, v in singleNeuron.items():
    for neuron in v:
        red = colour.Color("red")
        blue = colour.Color("blue")
        green = colour.Color("green")
        allColors = list(blue.range_to(red, len(neuron) + 1))
        curColor = 0
        synList = []
        for item in neuron:
            if "RIGHT HEMISPHERE" in item.annotations:
                item.curColor = "purple"
            elif "LEFT HEMISPHERE" in item.annotations:
                item.curColor = "orange"
            elif "RIGHT HEMISPHERE" not in item.annotations and "LEFT HEMISPHERE" not in item.annotations:
                item.curColor = "yellow"
            colors.append(item.curColor)
            curColor += 1
            singleVals.append(item.GF1synapseCount)
singleTrace = go.Bar(
    x = singleKeys,
    y = singleVals,
    marker=dict(color = colors),
    name = "SingleContraIpsi"
)
layout = go.Layout(
    barmode='group',
    margin=go.layout.Margin(
        b=200,
        r = 175
    ),
    xaxis = dict(tickangle = 45)
)
data = [singleTrace]
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='Synapse Bins by Type')
'''


'''low = defaultdict(list)
high = defaultdict(list)
equal = defaultdict(list)
red = colour.Color("red")
blue = colour.Color("blue")
yellow = colour.Color("yellow")
for k, v in twoNeurons.items():
    syncount1 = v[0].GF1synapseCount
    syncount2 = v[1].GF1synapseCount
    if syncount1 < syncount2:
        low[v[0].classification].append(v[0])
        v[0].curColor = 'blue'
        high[v[1].classification].append(v[1])
        v[1].curColor = 'red'
    elif syncount1 > syncount2:
        low[v[0].classification].append(v[1])
        v[0].curColor = 'blue'
        high[v[1].classification].append(v[0])
        v[1].curColor = 'red'
    elif syncount1 == syncount2:
        equal[v[0].classification].append(v[0])
        v[0].curColor = 'yellow'
        equal[v[1].classification].append(v[1])
        v[1].curColor = 'yellow'
        
aListOfNeurons = []
for k, v in low.items():
    for neuron in v:
        skid = neuron.skeletonID
        aNeuron = {
            "skeleton_id": skid,
            "color": neuron.curColor,
            "opacity": 1
        }
    aListOfNeurons.append(aNeuron)
for k, v in high.items():
    for neuron in v:
        skid = neuron.skeletonID
        aNeuron = {
            "skeleton_id": skid,
            "color": neuron.curColor,
            "opacity": 1
        }
    aListOfNeurons.append(aNeuron)
for k, v in equal.items():
    for neuron in v:
        skid = neuron.skeletonID
        aNeuron = {
            "skeleton_id": skid,
            "color": neuron.curColor,
            "opacity": 1
        }
    aListOfNeurons.append(aNeuron)'''



