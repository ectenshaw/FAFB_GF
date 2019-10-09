import pandas as pd
import typecluster.typecluster as typecluster
import neuprint as neu
import csv
from sklearn.cluster import MiniBatchKMeans
from sklearn import datasets
from sklearn.preprocessing import StandardScaler

allInAndOut = pd.read_csv("allItems.csv")
bodylist = allInAndOut
#bodylist = ','.join(int(i) for i in allInAndOut)
client = neu.Client('emdata1.int.janelia.org:11000', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImVtaWx5dGVuc2hhd0BnbWFpbC5jb20iLCJsZXZlbCI6InJlYWR3cml0ZSIsImltYWdlLXVybCI6Imh0dHBzOi8vbGg0Lmdvb2dsZXVzZXJjb250ZW50LmNvbS8tdmhYaGxhYjFxcFEvQUFBQUFBQUFBQUkvQUFBQUFBQUFBQUEvQUNIaTNyZWcwN21uZHVkQ2RpWVRkeFJGWGdONmlnMENOZy9waG90by5qcGc_c3o9NTAiLCJleHAiOjE3NDUzNjg2MzR9.ZdpdpSZeYx4jeMBnnYvCpc-Pvtwh7WZ1Xf37zWyY91A')
neuroninfo = pd.read_csv("allInfo.csv")


'''
try removing neurons with known type to reduce clustering number
'''
unknowntype = neuroninfo[neuroninfo['type'].isnull()]
knowntype = neuroninfo[neuroninfo['type'].notnull()]




# fetch features based on input/output cell types (will work better if more neurons have identified cell types)
#features = typecluster.features.compute_connection_similarity_features(neuroninfo["bodyid"].values.tolist(), "hemibrain", client, preprocess=False, normalize=False)

'''
there is too much data and the memory cannot handle it
need another way to do this clustering on all of the data
or need to split the features data into multiple files to cluster
but splitting means the clusters will not be true clusters
'''
# create clusters based on kmeans or hierarchical clustering
#heiarchical clustering takes too much memory
#kclusterthousand = typecluster.cluster.kmeans_cluster(features[0], 1000) # over partition
#hclusterthousand = typecluster.cluster.hierarchical_cluster(features[0])


ukfeatures = typecluster.features.compute_connection_similarity_features(unknowntype["bodyid"].values.tolist(), "hemibrain", client, preprocess=False, normalize=False)
unknownkclusterthousand = typecluster.cluster.kmeans_cluster(ukfeatures[0], 1000) # over partition

unknownmapping, unknownclusterinfo = unknownkclusterthousand.get_partitions()

with open('unknownClusterDict.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in unknownmapping.items():
        writer.writerow([key, value])

#try to mini batch the kmeans
miniUKKmeans = MiniBatchKMeans(n_clusters=1000, batch_size=200, verbose=1).fit(ukfeatures[0])


kfeatures = typecluster.features.compute_connection_similarity_features(knowntype["bodyid"].values.tolist(), "hemibrain", client, preprocess=False, normalize=False)
knownkclusterthousand = typecluster.cluster.kmeans_cluster(kfeatures[0], 1000) # over partition

knownmapping, knownclusterinfo = knownkclusterthousand.get_partitions()

with open('knownClusterDict.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in knownmapping.items():
        writer.writerow([key, value])