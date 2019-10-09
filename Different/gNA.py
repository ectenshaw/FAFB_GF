import requests
import json
import itertools

from requests.auth import AuthBase

class CatmaidApiTokenAuth(AuthBase):
    """Attaches HTTP X-Authorization Token headers to the given Request."""
    def __init__(self, token):
            self.token = token

    def __call__(self, r):
            r.headers['X-Authorization'] = 'Token {}'.format(self.token)
            return r
        
token = config.token
project_id = config.project_id

def gAN():
    response = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/analytics/skeletons'
    .format(project_id), 
            auth = auth,
            data = {'skeleton_ids[0]' : 905634}

    )

    myData = json.loads(response.content)

    #relevantDict = {}
    relevantDict = myData['issues']
    #relevantDict = relevantDict[]
    #print(relevantDict)

    #my5List = []
    for i in relevantDict:
        #print("i = ", type(i))
        for e in i:
            if type(e) != int:
                newList = e
            #print ("e = ", type(e))
    #print(newList)

    treeNodeList = []
    for elem in newList:
        if elem[0] == 5:
            treeNodeList.append(elem[1])

    return treeNodeList