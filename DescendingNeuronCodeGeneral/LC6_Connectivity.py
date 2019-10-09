#l3169164

# coding: utf-8

# In[44]:

import requests
import json
import itertools
import config
import GetNeuronsByAnnotation as GNA

token = config.token
auth = config.CatmaidApiTokenAuth(token)

project_id = config.project_id

# Gets all DNright synaptic partners - parameter is the DN of interest's skeletonID (use int)
# DNp02 == 7138957
# DNp04 == 6958818
def getDNrightPartners():
    mySkids = GNA.getSKIDlist()
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/connectivity'.format(project_id),
        auth=auth,
        data={'source_skeleton_ids[]': mySkids, 'boolean_op': "OR"}

    )

    myNeurons = json.loads(response.content)

    return myNeurons


# returns a dictionary of SkelIds mapped to synapse count with DNright
def removeExtra():
    myNeurons = getDNrightPartners()
    OutgoingPartners = {}
    OutgoingPartners = myNeurons['outgoing']
    AllSynapses = {}

    # removes all seed nodes
    for i in OutgoingPartners:
        d = OutgoingPartners[i]

        if d['num_nodes'] > 4:
            e = d['skids']
            tempList = e[str(skeletonID)]
            AllSynapses[i] = tempList[4]
            tempList = []

    return AllSynapses


# returns string list of all skeleton ids that are presynaptic to the given skeletonID parameter
def getMySkids(DNconnectivity=None):
    if DNconnectivity is not None:
        mySkels = DNconnectivity
    else:
        mySkels = removeExtra()
    mySkeletons = list(mySkels.keys())
    return mySkeletons


'''def getDNrightPartnersWithFilter(filterName):

    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/connectivity'.format(project_id), 
        auth = auth,
        data={'source_skeleton_ids[]': [4947529], 'boolean_op' : "OR", 'filter': str(filterName) }

    )

    return response
'''


def filterDN(annotation):
    pass


# Gets all DNright synaptic partners - in form: {'outgoing': {str('aSkeletonID'): {'skids': { str('aSKID'): {[0,0,0,0,int(num synapses)]}, 'num_nodes': int(anumber of nodes)}, str('aSkeletonID'): repeat}}, 'outgoing': {str('aSkeletonID'): {'skids':{str('aSKID'):
def getSkeletonPartners(SKID):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/connectivity'.format(project_id),
        auth=auth,
        data={'source_skeleton_ids[]': [SKID], 'boolean_op': "OR"}

    )

    myNeurons = json.loads(response.content)

    return myNeurons

#returns {LC6 ConID: [LC6 skid, LC6 conID, x, y, z, tnid]}
def getConnectors(SKIDS = None):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/links/',
        auth=auth,
        data={
            'skeleton_ids': [3117027],#, 3146029, 3281836, 3123735],
            'relation_type': 'presynaptic_to',
            'with_tags' : True
        }
    )

    myConnectors = json.loads(response.content)
    new = {}
    for i in myConnectors['links']:
        if str(i[1]) in myConnectors['tags']:
            new[str(i[1])] = i
    cleaned = {}
    for i in new:
        cleaned[i] = new[i][0:8]
        del (cleaned[i][5:7])
    return cleaned

#parameter should be above function call, returns same as above with a list of postsynaptic partner skids apended to end
def getConnectorPartners(connectorIDArray):
    newDict = {}
    for connectorID in connectorIDArray:
        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/{}/'.format(connectorID)
        )
        myR = json.loads(response.content)
        myPartners = {}
        for partner in myR['partners']:
            cable_length = json.loads(requests.get('https://neuropil.janelia.org/tracing/fafb/v14/1/skeletons/{}/cable-length'.format(partner['skeleton_id'])).content)['cable_length']
            if cable_length >= 10.0:
                myPartners[partner['skeleton_id']] = cable_length
        newDict[connectorID] = connectorIDArray[connectorID]
        newDict[connectorID].append(myPartners)
    return newDict
