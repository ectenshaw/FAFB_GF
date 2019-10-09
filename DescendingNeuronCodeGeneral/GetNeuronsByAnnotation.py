
#3489456 == LC6 neurons

import requests
import json
import itertools
import GetLookUpTable
import config

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id
object_ids = [134]
created_by = [134]
annotated_with = [3489456]
LC6partners = [3169164]



def getLC6neurons():
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id),
        auth=auth,
        data={'annotated_with': annotated_with}

    )
    myData = json.loads(response.content)

    relevantDict = {}
    relevantDict = myData['entities']

    return relevantDict

def getSKIDlist():
    myDict = getLC6neurons()
    myList = []
    for i in myDict:
        myList.append(i['id'])
    return myList

def getLC6partners():
    response = requests.post(
        'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/query-targets'.format(project_id),
        auth=auth,
        data={'annotated_with': LC6partners}

    )
    myData = json.loads(response.content)

    relevantDict = {}
    relevantDict = myData['entities']

    return relevantDict

def getSKIDlistPartners():
    myDict = getLC6partners()
    myList = []
    for i in myDict:
        myList.append(i['id'])
    return myList