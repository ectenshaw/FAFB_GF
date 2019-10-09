import config

# coding: utf-8

#corresponds to part 3

# In[2]:
import requests
import json
import itertools

# returns dictionary containing a lookup table with int(annotation id) as key and annotation string/name as value
def getLookUpTable():    
    import requests
    import json
    import itertools

    token = config.token
    auth = config.CatmaidApiTokenAuth(token)

    project_id = config.project_id
    object_ids = [134]
    created_by = [134]
    annotated_with = [863792]

    headers = config.CatmaidApiTokenAuth(token)




    allAnnotations = requests.get(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/'.format(project_id), 
            auth = auth
    )

    someData = json.loads(allAnnotations.content.decode('utf-8'))

    #print(someData)
    AnnotationLookUpTable = {}
    AnnotationLookUpTable = someData["annotations"]

    myLookUpTable = {}

    for d in AnnotationLookUpTable:
        myLookUpTable[d['id']] = d['name']

    return myLookUpTable


# In[ ]:
def getAnnotationID(myAnnotation):
    c = getLookUpTable()
    for i in c:
        if c[i] == str(myAnnotation):
            return i
    return    


