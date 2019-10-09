import config

import pandas


def importClusters(mySet):
    df=pandas.read_csv('C:/Users/polskyj/myCode/RCode/newTest/AllGF1Synapses8ClustersWithSKID.csv',converters={"connectorID":int, 'X':float,'Y':float, 'Z':float, 'Cluster':int})
    
    
    for index, row in df.iterrows():    
        mySet[int(row['skeletonID'])].GF1SynapticClusters.append(row['Cluster'])
    return



    
#filter for neurons with all synapses in a single cluster
for i in mySet:
    prevItem = None
    count = len(i.GF1SynapticClusters) - 1
    for item in i.GF1SynapticClusters:
        curItem = item
        if prevItem is not None:
            if curItem != prevItem:
                continue
            if count == 1:
                print(i.skeletonID, ': ', i.GF1SynapticClusters)
                continue
            count -= 1
            prevItem = curItem
        prevItem = curItem
                