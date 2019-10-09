import requests
import json
import config

token = config.token
auth = config.CatmaidApiTokenAuth(token)
project_id = config.project_id

token = config.token
project_id = config.project_id


# enter endDate in format 'YYYY-MM-DD'
def getAllStats(endDate, startDate=None):
    if startDate is None:
        startDate = '2017-01-01'
    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/stats/user-history?pid=1&start_date={}&end_date={}'.format(
            startDate, endDate),
        auth=auth
    )

    allStats = json.loads(response.content)

    relevantStats = allStats['stats_table']
    CATstats = {}
    catUsers = getUserIds()
    # print(catUsers)
    # print(relevantStats)
    for i in catUsers:
        i = str(i)
        if i in relevantStats:
            CATstats[i] = relevantStats[i]
    return CATstats


# returns all CATMAID User IDs
def getAllUserIDs():
    allAnnotations = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/annotations/',
        auth=auth
    )
    myAnnotations = json.loads(allAnnotations.content)

    theAnnotations = myAnnotations['annotations']
    return theAnnotations


# returns all unique CATMAID User IDs
def getUniqueUserIDs():
    allUserIDs = getAllUserIDs()
    IDlist = []
    for i in allUserIDs:
        for item in i['users']:
            if item['name'] not in IDlist:
                IDlist.append(item['name'])
    return IDlist


def makeUserIDLookUpTable():
    myTable = {}
    # userIDs = getUniqueUserIDs()
    # for i in test:
    #     for item in Users:
    #         if item in i['users'][0]['name']:
    #             print(i['users'][0]['id'])
    # for i in userIDs:
    #     pass
    # pass
    allUserIDs = getAllUserIDs()
    for i in allUserIDs:
        if not i['users']:
            continue
        elif i['users'][0]['name'] not in myTable:
            myTable[i['users'][0]['name']] = i['users'][0]['id']
    return myTable


# returns all CAT user IDs
def getUserIds():
    myUserIDs = []
    theAnnotations = getAllUserIDs()
    theUserIDList = getUniqueUserIDs()

    myUserList = ['parekhr', 'wangf', 'patrickc', 'patersont', 'alghailanis', 'polskyj', 'alis', 'dreherm', 'moranc',
                  'yangt', 'suleimana', 'lafossep', 'ludwigh', 'laughlandc', 'greerm', 'forknalln', 'eubanksb',
                  'fairbanksk', 'rampallyn', 'walshj', 'padillan', 'ndamam', 'flynnm', 'gezahegnb']

    while len(myUserList) >= 1:
        tempUser = myUserList.pop()
        for item in theAnnotations:

            if item['users'] != []:
                if item['users'][0]['name'] == tempUser:
                    myUserIDs.append(item['users'][0]['id'])
                    break
                else:
                    continue
    # these users are not returned from annotations api
    extraUserIDs = [187, 186, 196, 195]
    for i in extraUserIDs:
        if i not in myUserIDs:
            myUserIDs.append(i)

    return myUserIDs


def getCATIDs():
    myUserIDs = []
    allIDs = makeUserIDLookUpTable()
    myUserList = ['parekhr', 'wangf', 'patrickc', 'patersont', 'alghailanis', 'polskyj', 'alis', 'dreherm', 'moranc',
                  'yangt', 'suleimana', 'lafossep', 'ludwigh', 'laughlandc', 'greerm', 'forknalln', 'eubanksb',
                  'fairbanksk', 'rampallyn', 'walshj', 'padillan', 'ndamam', 'flynnm', 'gezahegnb']
    while len(myUserList) >= 1:
        tempUser = myUserList.pop()
        if tempUser in allIDs:
            myUserIDs.append(allIDs[tempUser])
    return myUserIDs


# returns cable length, connectors, and reviewed Nodes for CAT (note that cable length is currently listed as 'nodes' in the API results)
def getCatStats(endDate):
    ourStats = getAllStats(endDate)
    myNewStats = {}
    newTreeNodes = 0.0
    newConnectors = 0.0
    newReviewedNodes = 0.0
    newCableLength = 0.0
    for i in ourStats:
        for item in ourStats[i]:
            if bool(ourStats[i][item]) == True:
                if 'new_treenodes' in ourStats[i][item]:
                    newTreeNodes += ourStats[i][item]['new_treenodes']
                if 'new_connectors' in ourStats[i][item]:
                    newConnectors += ourStats[i][item]['new_connectors']
                if 'new_reviewed_nodes' in ourStats[i][item]:
                    newReviewedNodes += ourStats[i][item]['new_reviewed_nodes']
                if 'new_cable_length' in ourStats[i][item]:
                    newCableLength += ourStats[i][item]['new_cable_length']
    myNewStats['nodes'] = newTreeNodes
    myNewStats['connectors'] = newConnectors
    myNewStats['reviewed_Nodes'] = newReviewedNodes
    myNewStats['cable_length'] = newCableLength

    return myNewStats


def getStats(endDate, startDate=None):
    if startDate is None:
        startDate = '2017-01-01'
    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/stats/user-history?pid=1&start_date={}&end_date={}'.format(
            startDate, endDate),
        auth=auth
    )

    allStats = json.loads(response.content)

    relevantStats = allStats['stats_table']
    return relevantStats


def getAllUserStats(endDate):
    ourStats = getStats(endDate)
    myNewStats = {}
    newTreeNodes = 0.0
    newConnectors = 0.0
    newReviewedNodes = 0.0
    newCableLength = 0.0
    for i in ourStats:
        for item in ourStats[i]:
            if bool(ourStats[i][item]) == True:
                if 'new_treenodes' in ourStats[i][item]:
                    newTreeNodes += ourStats[i][item]['new_treenodes']
                if 'new_connectors' in ourStats[i][item]:
                    newConnectors += ourStats[i][item]['new_connectors']
                if 'new_reviewed_nodes' in ourStats[i][item]:
                    newReviewedNodes += ourStats[i][item]['new_reviewed_nodes']
                if 'new_cable_length' in ourStats[i][item]:
                    newCableLength += ourStats[i][item]['new_cable_length']
    myNewStats['nodes'] = newTreeNodes
    myNewStats['connectors'] = newConnectors
    myNewStats['reviewed_Nodes'] = newReviewedNodes
    myNewStats['cable_length'] = newCableLength

    return myNewStats


def getCatPercentage(endDate):
    allStats = getAllUserStats(endDate)
    catStats = getCatStats(endDate)
    pctNodes = catStats['nodes'] / allStats['nodes']
    pctConnectors = catStats['connectors'] / allStats['connectors']
    pctReviewed = catStats['reviewed_Nodes'] / allStats['reviewed_Nodes']
    pctCableLength = catStats['cable_length'] / allStats['cable_length']
    print('percent Nodes: ', pctNodes, ' percent connectors: ', pctConnectors, ' percent Reviewed: ', pctReviewed,
          'percent cable length: ', pctCableLength)
    return


# returns nodeCount from beginning of time (we use a prespecified start date - 2017-1-1 - so this is irrelevant
def getNodeCount():
    response = requests.get(
        'https://neuropil.janelia.org/tracing/fafb/v14/1/stats/nodecount',
        auth=config.CatmaidApiTokenAuth(token)
    )

    allNodes = json.loads(response.content)
    return allNodes


def getAllNodes():
    allNodes = 0
    nodeDict = getNodeCount()
    for i in nodeDict:
        allNodes += nodeDict[i]
    return allNodes


def getCATNodes():
    CATNodes = 0
    CAT = getUserIds()
    nodeDict = getNodeCount()
    for i in nodeDict:
        if int(i) in CAT:
            CATNodes += nodeDict[i]
    return CATNodes





