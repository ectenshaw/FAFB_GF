
# coding: utf-8


#corresponds to part 2?

# In[1]:

import requests
import json
import itertools
import GetLookUpTable
import GetAnnotationsRemoveExtraneousInfo

def getMyAnnotations():
    myNeuronswithAnnotations = GetAnnotationsRemoveExtraneousInfo.convertID2String()

    return myNeuronswithAnnotations

