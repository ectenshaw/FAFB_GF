import config

# coding: utf-8

# In[44]:

import requests
import json
import itertools

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id


# Gets all GF1 synaptic partners
def getGF1Partners(skeleton_id=4947529):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/connectivity'.format(project_id),
        auth=auth,
        data={'source_skeleton_ids[]': [ skeleton_id ], 'boolean_op': "OR"}

    )

    myNeurons = json.loads(response.content.decode('utf-8'))

    return myNeurons


# returns a dictionary of SkelIds mapped to synapse count with GF1; defaults to GF1, but can be set to other neurons
# as well
def removeExtra(skeleton_id='4947529'):
    myNeurons = getGF1Partners(int(skeleton_id))
    IncomingPartners = {}
    IncomingPartners = myNeurons['incoming']
    AllSynapses = {}

    # removes all seed nodes
    for i in IncomingPartners:
        d = IncomingPartners[ i ]

        # if d['num_nodes'] > 4:
        e = d[ 'skids' ]
        tempList = e[ skeleton_id ]
        AllSynapses[ i ] = tempList[ 4 ]
        tempList = [ ]

    return AllSynapses


'''def getGF1PartnersWithFilter(filterName):

    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/connectivity'.format(project_id), 
        auth = auth,
        data={'source_skeleton_ids[]': [4947529], 'boolean_op' : "OR", 'filter': str(filterName) }

    )

    return response
'''


def filterGF(annotation):
    pass


# Gets all GF1 synaptic partners - in form: {'outgoing': {str('aSkeletonID'): {'skids': { str('aSKID'): {[0,0,0,0,
# int(num synapses)]}, 'num_nodes': int(anumber of nodes)}, str('aSkeletonID'): repeat}}, 'incoming': {str(
# 'aSkeletonID'): {'skids':{str('aSKID'):
def getSkeletonPartners(SKID):
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/skeletons/connectivity'.format(project_id),
        auth=auth,
        data={'source_skeleton_ids[]': [ SKID ], 'boolean_op': "OR"}

    )

    myNeurons = json.loads(response.content)

    return myNeurons


def getConnectorsStep1(SKIDS, relation_type, with_tags=True):
    # if SKIDS is None:
    # SKIDS = []
    if 'pre' in relation_type or "Pre" in relation_type:
        relation = 'presynaptic_to'
    elif 'post' in relation_type or "Post" in relation_type:
        relation = 'postsynaptic_to'
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/',
        auth=auth,
        data={
            'skeleton_ids': SKIDS,
            'relation_type': relation,
            'with_tags': with_tags
        }
    )
    myConnectors = json.loads(response.content)
    return myConnectors


def getConnectors(SKIDS, relation_type, with_tags=True):
    """
      :param SKIDS: array of int ,
             relation_type: str either presynaptic or postsynaptic
      :return: {LC6 ConID: [LC6 skid, LC6 conID, x, y, z, tnid]}
      """
    # if SKIDS is None:
    # SKIDS = []
    if 'pre' in relation_type or "Pre" in relation_type:
        relation = 'presynaptic_to'
    elif 'post' in relation_type or "Post" in relation_type:
        relation = 'postsynaptic_to'
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/links/',
        auth=auth,
        data={
            'skeleton_ids': SKIDS,
            'relation_type': relation,
            'with_tags': with_tags
        }
    )
    myConnectors = json.loads(response.content)

    new = {}
    for i in myConnectors[ 'links' ]:
        if str(i[ 1 ]) in myConnectors[ 'tags' ]:
            new[ str(i[ 1 ]) ] = i
    cleaned = {}
    for i in new:
        cleaned[ i ] = new[ i ][ 0:8 ]
        del (cleaned[ i ][ 5:7 ])
    return cleaned


# parameter should be above function call, returns same as above with a list of postsynaptic partner skids apended to
#  end
def getConnectorPartners(connectorIDArray):
    newDict = {}
    for connectorID in connectorIDArray:
        response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/1/connectors/{}/'.format(connectorID)
        )
        myR = json.loads(response.content)
        myPartners = {}
        for partner in myR[ 'partners' ]:
            cable_length = json.loads(requests.get(
                'https://neuropil.janelia.org/tracing/fafb/v14/1/skeletons/{}/cable-length'.format(
                    partner[ 'skeleton_id' ])).content)[ 'cable_length' ]
            if cable_length >= 10.0:
                myPartners[ partner[ 'skeleton_id' ] ] = cable_length
        newDict[ connectorID ] = connectorIDArray[ connectorID ]
        newDict[ connectorID ].append(myPartners)
    return newDict
