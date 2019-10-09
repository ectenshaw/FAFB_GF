      
import pandas


def importClusters(mySet):
    df=pandas.read_csv('C:/Users/polskyj/myCode/RCode/newTest/AllDNrightSynapses8ClustersWithSKID.csv',converters={"connectorID":int, 'X':float,'Y':float, 'Z':float, 'Cluster':int})
    
    
    for index, row in df.iterrows():    
        mySet[int(row['skeletonID'])].DNrightSynapticClusters.append(row['Cluster'])
    return



    
#filter for neurons with all synapses in a single cluster
for i in mySet:
    prevItem = None
    count = len(i.DNrightSynapticClusters) - 1
    for item in i.DNrightSynapticClusters:
        curItem = item
        if prevItem is not None:
            if curItem != prevItem:
                continue
            if count == 1:
                print(i.skeletonID, ': ', i.DNrightSynapticClusters)
                continue
            count -= 1
            prevItem = curItem
        prevItem = curItem
                