import sklearn
#from CatmaidCode import MyCustomGFNeuronClass as CN
#from CatmaidCode import CustomNeuronClassSet as CS
import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
import config

import matplotlib.pyplot as plt
from itertools import cycle

#from CatmaidCode import jsonNeurons as JN

# input should be a set of neurons with their somata updated. Clusters neurons based upon soma location, plots a cluster graph, and outputs a json
def clusterSomata(mySet):
    setHolder = mySet
    tempGroupName = mySet.groupName
    '''for item in mySet:
        for i in item.soma:
            if i is None:
                print("{} removed because its soma could not be found".format(item.skeletonID))
                mySet -= item #mySet[mySet.index(i.skeletonID)]
                break'''
    mySet = removeSomaless(mySet)
    AP = AffinityPropagation()

    n_samples = mySet.numNeurons
    n_features = 3
    coordinateList = []
    labels_true = []
    for i in mySet:
        coordinateList.append(i.soma)
        labels_true.append(i.skeletonID)
        
    coordinateList = np.array(coordinateList)

    X = coordinateList
    af = AP.fit(X)
    labels = AP.fit_predict(X)
    cluster_centers_indices = af.cluster_centers_indices_
    n_clusters_ = len(cluster_centers_indices)
    myAdditionalInfo = ""
    print('Estimated number of clusters: %d' % n_clusters_)
    print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    print("Adjusted Rand Index: %0.3f" % metrics.adjusted_rand_score(labels_true, labels))
    print("Adjusted Mutual Information: %0.3f" % metrics.adjusted_mutual_info_score(labels_true, labels))
    print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels, metric='sqeuclidean'))
    myAdditionalInfo += str(tempGroupName) + '\n'    
    myAdditionalInfo += 'Estimated number of clusters: %d' % n_clusters_ + '\n'
    myAdditionalInfo += "Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Completeness: %0.3f" % metrics.completeness_score(labels_true, labels) + '\n'
    myAdditionalInfo += "V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Adjusted Rand Index: %0.3f" % metrics.adjusted_rand_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Adjusted Mutual Information: %0.3f" % metrics.adjusted_mutual_info_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels, metric='sqeuclidean') + '\n'

    
    
    
    plt.close('all')
    plt.figure(1)
    plt.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    myClusters = {}
    for k, col in zip(range(n_clusters_), colors):
        class_members = labels == k
        tempList = []
        count = 0
        for item in labels:
            if item == k:
                tempList.append(labels_true[count])
                count += 1
            else:
                count += 1
        myClusters[str(col) + str(k)] = tempList

        cluster_center = X[cluster_centers_indices[k]]
        plt.plot(X[class_members, 0], X[class_members, 1], col + '.')
        plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                 markeredgecolor='k', markersize=14)
        for x in X[class_members]:
            plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)

    plt.title('Estimated number of clusters: %d' % n_clusters_)
    #plt.savefig(
    plt.show()

    #return myClusters

#myclusters should be dictionary of lists of skids (as returned by above function), returns list containing GFIN_sets
#def createSet(myClusters):
    myBigSet = [] 
    count = 0
    for item in myClusters:
        tempItem = CS.buildFromSkidList(myClusters[item])
        tempItem.groupName = str(tempGroupName) + 'Clustering' + str(count)
        myBigSet.append(tempItem)
        count += 1
   # return myBigSet
    JN.autoSaveJSONFlatColor(myBigSet, myAdditionalInfo)
    for i in myBigSet:
        for item in i:
            item.soma = setHolder[setHolder.index(item.skeletonID)].soma
    return myBigSet

#can be used in other functions to remove neurons that do not have a soma in order to avoid error
def removeSomaless(mySet):
    for item in mySet:
        for i in item.soma:
            if i is None:
                print("{} removed because its soma could not be found".format(item.skeletonID))
                mySet -= item #mySet[mySet.index(i.skeletonID)]
                break
    return mySet
  
    
    
def clusterRightHemisphere(mySet):
    tempGroupName = mySet.groupName
    mySet = removeSomaless(mySet)
    for item in mySet:
        if item.soma[0] > 550000:
            mySet -= item 
    mySet.groupName = str(tempGroupName) + 'OnlyRightHemisphere'
    myBigSet = clusterSomata(mySet)
    return myBigSet

def clusterLeftHemisphere(mySet):
    tempGroupName = mySet.groupName
    mySet = removeSomaless(mySet)
    for item in mySet:
        if item.soma[0] < 550000:
            mySet -= item
    mySet.groupName = str(tempGroupName) + 'OnlyRightHemisphere'
    myBigSet = clusterSomata(mySet)
    return myBigSet

#input should be the output from the clusterSomata function, allowing for the reclustering of a given cluster
def reclusterResults(myBigSet):
    for i in myBigSet:
        clusterSomata(i)
    return
    
def clusterSynapses(mySet):
    setHolder = mySet
    tempGroupName = str(mySet.groupName)
    tempGroupName += 'synapseCoordinatesCluster'
    AP = AffinityPropagation()
    if mySet.allSynapseCoordinates is None:
        mySet.combineAllSynLocations()
    n_samples = len(mySet.allSynapseCoordinates) - 1
    n_features = 3
    coordinateList = []
    labels_true = []

    for i in mySet.allSynapseCoordinates:
        coordinateList.append(mySet.allSynapseCoordinates[i])
        labels_true.append(i)
        
    coordinateList = np.array(coordinateList)

    X = coordinateList
    af = AP.fit(X)
    labels = AP.fit_predict(X)
    cluster_centers_indices = af.cluster_centers_indices_
    n_clusters_ = len(cluster_centers_indices)
    myAdditionalInfo = ""
    print('Estimated number of clusters: %d' % n_clusters_)
    print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    print("Adjusted Rand Index: %0.3f" % metrics.adjusted_rand_score(labels_true, labels))
    print("Adjusted Mutual Information: %0.3f" % metrics.adjusted_mutual_info_score(labels_true, labels))
    print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels, metric='sqeuclidean'))
    myAdditionalInfo += str(tempGroupName) + '\n'    
    myAdditionalInfo += 'Estimated number of clusters: %d' % n_clusters_ + '\n'
    myAdditionalInfo += "Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Completeness: %0.3f" % metrics.completeness_score(labels_true, labels) + '\n'
    myAdditionalInfo += "V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Adjusted Rand Index: %0.3f" % metrics.adjusted_rand_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Adjusted Mutual Information: %0.3f" % metrics.adjusted_mutual_info_score(labels_true, labels) + '\n'
    myAdditionalInfo += "Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels, metric='sqeuclidean') + '\n'

    
    
    
    plt.close('all')
    plt.figure(1)
    plt.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    myClusters = {}
    for k, col in zip(range(n_clusters_), colors):
        class_members = labels == k
        tempList = []
        count = 0
        for item in labels:
            if item == k:
                tempList.append(labels_true[count])
                count += 1
            else:
                count += 1
        myClusters[str(col) + str(k)] = tempList

        cluster_center = X[cluster_centers_indices[k]]
        plt.plot(X[class_members, 0], X[class_members, 1], col + '.')
        plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                 markeredgecolor='k', markersize=14)
        for x in X[class_members]:
            plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)

    plt.title('Estimated number of clusters: %d' % n_clusters_)
    #plt.savefig(
    plt.show()

    return myClusters

#myclusters should be dictionary of lists of connectorIDs (as returned by above function), returns list containing GFIN_sets
#def createSet(myClusters):
    '''myBigSet = [] 
    count = 0
    for item in myClusters:
        tempItem = CS.buildFromSkidList(myClusters[item])
        tempItem.groupName = str(tempGroupName) + 'Clustering' + str(count)
        myBigSet.append(tempItem)
        count += 1
    return myBigSet
    JN.autoSaveJSONFlatColor(myBigSet, myAdditionalInfo)
    for i in myBigSet:
        for item in i:
            item.soma = setHolder[setHolder.index(item.skeletonID)].soma
    return myBigSet'''
    