import config
# coding: utf-8

# In[1]:

#Corresponds to Part1

#ThisCodeWorks- returns the skeleton id,type (e.g. neuron), neuron id, and neuron name  of all neurons annotated with DNright input neuron
import requests
import json

def GetAnnotations():

    token = config.token
    auth = config.CatmaidApiTokenAuth(token)
    project_id = config.project_id
    object_ids = [134]
    created_by = [134]
    annotated_with = [863792]

    headers = config.CatmaidApiTokenAuth(token)
    #print(str(headers))

    payload = {
        #'skeleton_ids': [
            0
        #],
        #'type': "",
        #'name': "",
        #"id": 0
        #'annotated_with': '8863792'
    }

    response = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id), 
            auth = auth,
            data={'annotated_with': 863792}

    )
    return response


def buildAllAnnotationLookUpTable():
    response = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/'.format(project_id), 
            auth = auth
    )
    myTable = json.loads(response.content)
    return myTable
    

