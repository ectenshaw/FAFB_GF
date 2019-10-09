import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from kmodes.kmodes import KModes
import json
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools



#creates a plot and json of clusters
#add more colors if more than 8 clusters
#file is created with e2c saveWithNeuropils
#filepath example:
#'C:/Users/tenshawe/Desktop/pyCharmOutputs/CSV/saveWithNeuropilsAllGF1inputNeurons/2019125saveWithNeuropilsAllGF1inputNeurons.csv'
def createNeuropilClusters(mySet, numClusters, filepath):
    #read CSV for neuropils -
    data = pd.read_csv(filepath)
    names = data['Neuron Name']
    data.pop('Neuron Name')
    data.pop('Classification')

    Sum_of_squared_distances = []
    K = range(1,15)
    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(data)
        Sum_of_squared_distances.append(km.inertia_)
    plt.plot(K, Sum_of_squared_distances, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Sum_of_squared_distances')
    plt.title('Elbow Method For Optimal k')
    plt.show()

    km = KMeans(n_clusters= numClusters).fit(data)
    cluster_map = pd.DataFrame()
    cluster_map['data_index'] = data.index.values
    cluster_map['cluster'] = km.labels_
    clusters = cluster_map['cluster']
    clusterDict = dict(zip(names, clusters))
    clusterDict2 = defaultdict(list)
    for k, v in clusterDict.items():
        clusterDict2[v].append(k)
    keys = []
    keys = list(clusterDict2.keys())
    values = []
    for k, v in clusterDict2.items():
        values.append(len(v))

    keys, values = zip(*sorted(zip(keys, values)))
    count = 0
    while count < len(clusterDict2):
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[0]:
                neuron.curColor = 'rgb(0,255,0)'
            count = count + 1
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[1]:
                neuron.curColor = 'rgb(0,0,255)'
            count = count + 1
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[2]:
                neuron.curColor = 'rgb(255,0,255)'
            count = count + 1
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[3]:
                neuron.curColor = 'rgb(0, 255,255)'
            count = count + 1
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[4]:
                neuron.curColor = 'rgb(255,0,0)'
            count = count + 1
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[5]:
                neuron.curColor = 'rgb(255,255,0)'
            count = count + 1
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[6]:
                neuron.curColor = 'rgb(255,218,185)'
            count = count + 1
        for neuron in mySet:
            if neuron.neuronName in clusterDict2[7]:
                neuron.curColor = 'rgb(255,128,0)'
            count = count + 1

    colors = ('rgb(0,255,0)', 'rgb(0,0,255)', 'rgb(255,0,255)', 'rgb(0, 255,255)', 'rgb(255,0,0)',
              'rgb(255,255,0)', 'rgb(255,218,185)','rgb(255,128,0)')
    trace = go.Bar(
            x = keys,
            y = values,
            text = values,
        textposition = 'auto',
        marker=dict(color = colors)
        )
    layout = go.Layout(
        title = str(numClusters) + " Clusters"
    )
    traceData = [trace]
    fig = go.Figure(data = traceData, layout = layout)
    py.plot(fig, filename='Clustering Plots/' + str(numClusters) + 'Clusters')

    #createJSON
    aListOfNeurons = []
    for item in mySet:
            mySKID = item.skeletonID
            aNeuron = {
            "skeleton_id": mySKID,
            "color": item.curColor,
            "opacity": 1
            }
            aListOfNeurons.append(aNeuron)
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    c = open('C:/Users/tenshawe/Desktop/pyCharmOutputs/ClusteringJSON/' + str(numClusters) + 'Clusters.json', 'w')
    c.write(myJSON)
    c.close()
    return


'''
    for i in mySet:
        #red
        if i.modality == "Descending Neuron":
            i.curColor = 'rgb(255,51,51)'
        #lime
        elif i.modality == "Ascending Neuron":
            i.curColor = 'rgb(0,255,0)'
        #yellow
        elif i.modality == "Other Visual":
            i.curColor = 'rgb(255,255,0)'
        #orange
        elif i.modality == "VPN":
            i.curColor = 'rgb(255,128,0)'
        #cyan
        elif i.modality == "Non-Visual Interneuron":
            i.curColor = 'rgb(0,255,255)'
        #blue
        elif i.modality == "Visual Interneuron":
            i.curColor = 'rgb(0,0,255)'
        #pink
        elif i.modality == "JONeuron":
            i.curColor = 'rgb(255,0,255)'
        #white
        elif i.modality == "Mechanosensory Interneuron":
            i.curColor = 'rgb(255,255,255)'

    aListOfNeurons = []
    for item in mySet:
        mySKID = item.skeletonID
        aNeuron = {
            "skeleton_id": mySKID,
            "color": item.curColor,
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    c = open('ColorByModality.json', 'w')
    c.write(myJSON)
    c.close()



    aListOfNeurons = []
    for item in mySet:
        if item.modality == "Ascending Neuron":
            mySKID = item.skeletonID
            aNeuron = {
                "skeleton_id": mySKID,
                "color": item.curColor,
                "opacity": 1
            }
            aListOfNeurons.append(aNeuron)
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    c = open('AscendingModality.json', 'w')
    c.write(myJSON)
    c.close()
    
'''

'''
km = KModes(n_clusters=8, init='Huang', n_init=5, verbose=1)
clusters = km.fit_predict(data)
modesDict = dict(zip(names, clusters))
modesDict2 = defaultdict(list)
for k, v in modesDict.items():
    modesDict2[v].append(k)
keys = []
keys = list(modesDict2.keys())
values = []
for k, v in modesDict2.items():
    values.append(len(v))
    
keys, values = zip(*sorted(zip(keys, values)))
trace = go.Bar(
    x = keys,
    y = values,
    text = values,
    textposition = 'auto',
    marker=dict(color = colors)
)
traceData = [trace]
#fig = go.Figure(data = traceData, layout = layout)
py.plot(traceData, filename='Tests/ModesBar')

for neuron in mySet:
    if neuron.neuronName in modesDict2[0]:
        neuron.curColor = 'rgb(0,255,0)'
for neuron in mySet:
    if neuron.neuronName in modesDict2[1]:
        neuron.curColor = 'rgb(0,0,255)'
for neuron in mySet:
    if neuron.neuronName in modesDict2[2]:
        neuron.curColor = 'rgb(255,0,255)'
for neuron in mySet:
    if neuron.neuronName in modesDict2[3]:
        neuron.curColor = 'rgb(0, 255,255)'
for neuron in mySet:
    if neuron.neuronName in modesDict2[4]:
        neuron.curColor = 'rgb(255,0,0)'
for neuron in mySet:
    if neuron.neuronName in modesDict2[5]:
        neuron.curColor = 'rgb(255,255,0)'
for neuron in mySet:
    if neuron.neuronName in modesDict2[6]:
        neuron.curColor = 'rgb(255,218,185)'
for neuron in mySet:
    if neuron.neuronName in modesDict2[7]:
        neuron.curColor = 'rgb(255,128,0)'
        
aListOfNeurons = []
for item in mySet:
            mySKID = item.skeletonID
            aNeuron = {
            "skeleton_id": mySKID,
            "color": item.curColor,
            "opacity": 1
            }
            aListOfNeurons.append(aNeuron)
myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
c = open('8modesCluster.json', 'w')
c.write(myJSON)
c.close()



'''

