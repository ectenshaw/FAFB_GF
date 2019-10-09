import MyCustomGFNeuronClass
import numpy as np
import scipy as sp


class GFIN_set(object):
    
    def __init__(self, data):
        #self.data = np.array(MyCustomGFNeuronClass.builder())
        #self.data = np.array()
        self.data = data
        self.AllGF1Synapses = int()
        
    def __str__(self):
        return "{} GF input neurons \n {} synapses onto GF1".format(self.data.shape, self.AllGF1Synapses)
    
    #def __str__(self.data):
     #   for i in self.data:
      #      print(i)

    def getNeurons(self):
        return self.data
    #def setData():
    #for i in data:
     #   self.AllGF1Synapses += i.GF1synapseCount
      #  self.AllGF1Synapses

    
def builder():
    
    mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
     
    
    #myData = np.array(MyCustomGFNeuronClass.builder())
    
    for i in mySet.data:
        mySet.AllGF1Synapses += i.GF1synapseCount
    
    return mySet