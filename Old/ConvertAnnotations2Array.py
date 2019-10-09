
# coding: utf-8

#corresponds to part2?

# In[14]:



#ThisCodeWorks- returns list of skeletonIDs 
import requests
import json
import itertools

from GetAnnotations import GetAnnotations

myAnnotations = GetAnnotations.GetAnnotations()


#returns list of relevant skeleton IDs
def ConvertAnnotations(myAnnotations):

    myData = json.loads(myAnnotations.content)
    
    relevantDict = {}
    relevantDict = myData['entities']
    SkidList = []
    #print(type(relevantDict))

    for d in relevantDict:
        if d['type'] == 'neuron':
            SkidList.append(d['skeleton_ids'])

    return SkidList


#returns dictionary containing skeleton ID and neuron name pairings
def getLookUpTableSkID_Name():
    myData = json.loads(myAnnotations.content)
    
    relevantDict = {}
    relevantDict = myData['entities']
    SkIDLookUpNeuronName = {}

    #returns dictionary containing SkID : neuron name pairs
    for d in relevantDict:

        if d["type"] == 'neuron':
            SkIDLookUpNeuronName[((d['skeleton_ids'])[0])] = d['name']
            
    return SkIDLookUpNeuronName



