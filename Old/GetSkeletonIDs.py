
# coding: utf-8

#corresponds to part 2?

# In[1]:
import requests
from GetAnnotations import GetAnnotations
myAnnotations = GetAnnotations()
from ConvertAnnotations2Array import ConvertAnnotations

mySkeletonIDlist = ConvertAnnotations(myAnnotations)

def GetIDs(mySkeletonIDlist):
    
    newResponse = requests.post(
            'https://neuropil.janelia.org/tracing/fafb/v14/{}/annotations/forskeletons'.format(project_id), 
            auth = auth,
            data={'skeleton_ids': SkidList}
    )
    return requests.models.Response(newResponse)

# In[ ]:



