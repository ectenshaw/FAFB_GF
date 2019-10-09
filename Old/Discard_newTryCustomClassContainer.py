import MyCustomGFNeuronClass
import numpy as np
import scipy as sp
import collections


class GFIN_set(np.ndarray):
    
    def __init__(self): 
        
        #super().__init__()
        np.ndarray.__init__(self, *args, **kwargs)    
        self.AllGF1Synapses = self._GF1Synapses()       
    
    def __str__(self):
        this = ""
        for item in self:
            this += str(item)
            this += "\n"
        return this
        
    def _GF1Synapses(self):
        curSyn = 0
        for item in self: 
            curSyn += item.GF1synapseCount
        return curSyn

def builder():
    
    #mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
    
    #mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
    
    mySet = GFIN_set(MyCustomGFNeuronClass.builder())
        
    #myData = np.array(MyCustomGFNeuronClass.builder())
    
    #for i in mySet.data:
     #   mySet.AllGF1Synapses += i.GF1synapseCount
    
    return mySet

class subArray(GFIN_set,):
    def __init__(self, GFSet, *args, **kwargs):
        GFIN_set.__init__(self, AllGF1Synapses)
        self.AllGF1Synapses = GFSet.AllGF1Synapses
        #self.AllGF1Synapses = AllGF1Synapses
        #self.aNeuronSet = GFIN_set(aNeuronSet)
        
        
        self.PCT = self._getSynCount()
        #return obj

    def _getSynCount(self):
        mySynCount = 0
        for item in self:
            print("item", item)
            mySynCount += self[item].GF1synapseCount
        return mySynCount
    def __str__(self):
        return GFIN_set.str(self)