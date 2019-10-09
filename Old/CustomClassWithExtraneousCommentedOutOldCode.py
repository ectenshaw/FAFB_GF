import MyCustomGFNeuronClass
import numpy as np
import scipy as sp
import collections


class GFIN_set(object):
    
    def __init__(self, container=None): 
        
        super().__init__()
        
        if container is None:
            self.container = []
        else:
            self.container = container

            
        self.AllGF1Synapses = self._GF1Synapses()
        
        self.percentTotalSynapses = 1


        #self.SynSum = self._getSUM()
        #self.NSynCounts = []
        
        #i = 0
        #for Neuron in container:
         #   self.NSynCounts[i] = self._getSynCount(Neuron)        
        
    def __len__(self):
        return len(self.container)
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return self.container[index]
        elif isinstance(index, slice):         #bug: if subSet is defined multiple times, percent total shifts to percent of previous group
            
            #sets each of the neurons in the subset percentTotalSynapse
            for i in self.container[index]:
                i.percentTotalSynapse = i.percentCurrentGroup
            
            #returns subset of type GFIN_set
            x = GFIN_set(self.container[index])
            return x
        
        else:
            raise TypeError
    def __setitem__(self, index, value):
        if index <= len(self.container):
            self.container[index] = value
        else:
            raise IndexError()
            
    def __getslice__(self,i,j):
        return self.container[max(0, i):max(0, j):]
    
    
    def __contains__(self, value):
        return value in self.container
    
    def append(self, value):
        self.container.append(value)
    
    def __repr__(self):
        return str(self.container)
    
    def __add__(self, otherList):
        return GFIN_set(self.container + otherList.container)
    
    def __str__(self):
        this = ""
        for item in self:
            this += str(item)
            this += "\n"
        return this
    
   # def __str__(percentTotalSynapses):
    #    myPercent = percentTotalSynapses * 100
     #   myString = str(myPercent)
      #  myString += "%"
       # return myString
    
    #Sets total GF1 Synapse Count
    def _GF1Synapses(self):
        curSyn = 0
        for item in self: 
            curSyn += item.GF1synapseCount
            
        #gives each neuron object a percent of total synapses
        for item in self:
            item.percentCurrentGroup = item.GF1synapseCount/curSyn
        return curSyn
    


        #def _getSUM():
        #curSum = 0
        #for i in container:
            #curSum += container[i].GF1synapseCount
            
    
    #def __str__():
        #for i in container:
          #  return (self[i])
        
   # def getStr(self):
    #    myStr = ""
     #   for i in self.container:
      #      myStr + self.container[i]
       # return myStr
        
    #def __str__(self):
     #   return "{} GF input neurons \n {} synapses onto GF1".format(self.data.shape, self.AllGF1Synapses)
    
    #def __str__(self.data):
     #   for i in self.data:
      #      print(i)

    #def getNeurons(self):
     #   return self.data
    #def setData():
    #for i in data:
     #   self.AllGF1Synapses += i.GF1synapseCount
      #  self.AllGF1Synapses

    
def builder():
    
    #mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
    
    #mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
    
    mySet = GFIN_set(np.array(MyCustomGFNeuronClass.builder()))
    
    #myData = np.array(MyCustomGFNeuronClass.builder())
    
    #for i in mySet.data:
     #   mySet.AllGF1Synapses += i.GF1synapseCount
    
    return mySet

def sortBySynL2H(mySet):
    L2H = sorted(mySet, key = MyCustomGFNeuronClass.GFinputNeuron.getGF1synapse)
    return L2H
def sortBySynH2L(mySet):
    H2L = sorted(mySet, key = MyCustomGFNeuronClass.GFinputNeuron.getGF1synapse, reverse=True)
    return H2L

def sliceBuilder(aSet):
    print(aSet)
    newSet = GFIN_set(np.array(aSet))
    return newSet

class subArray(GFIN_set, np.ndarray):
    def __init__(self, GFSet, *args, **kwargs):
    #def __init__(self, aNeuronSet, PCT = None):
        #super(subArray, self).__init__()
        GFIN_set.__init__(self, container, AllGF1Synapses)
        self.GFSet = GFIN_set(GFSet)
        np.ndarray.__init__(self, *args, **kwargs)
        #obj = np.asarray(GFSet).view(self)
        #obj.PCT = PCT
        self.container = GFSet.container
        self.AllGF1Synapses = GFSet.AllGF1Synapses
        #self.container = container
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
    #def __str__(self):
     #   return GFIN_set.str(self)
        
        
        
def totalSynapseCount(neurons):
    totalSynapseCount = int()
    for i in neurons:
        totalSynapseCount += neurons[i].GF1synapseCount
    return totalSynapseCount  
        
        #neurons[i].percentTotalSynapse = neurons[i].GF1synapseCount/

#class subArray(GFIN_set):
        
    #def __init__(self, aNeuronSet, PCT = None):
        
        #super().__init__()
        #if pctTotalGFsynpases is None:
         #   self.pctTotalGFsynapses = 0
        #else:
         #   self.pctTotalGFsynapses = pctTotalGFsynapses
            
        #mySet = np.asarray(aNeuronSet).view(cls)
        #mySet = GFIN_set(aNeuronSet)
        #self.aNeuronSet = aNeuronSet
        #cls.mySet = aNeuronSet
    #    if PCT is None:
     #       PCT = _self._getSynCount()
        
   # def _getSynCount(self):
       # mySynCount = 0
      #  for item in self:
        #    print("item", item)
         #   mySynCount += self[item].GF1synapseCount
        #return mySynCount
        

#Needs so much work
#class subArray(GFIN_set):
    
 #   def __new__(cls, input_array, pctTotalGFsynapses=None):
  #      thisArray = input_array.view(cls)
   #     mySynCount = 0
    #    print(type(thisArray))
     #   for i in thisArray:
      #      mySynCount += thisArray[i].GF1synapseCount
       #     #print(thisArray[i])
        #thisArray.pctTotalGFsynapses = mySynCount
        #return thisArray
    
    
   # def ___array_finalize__(self, thisArray):
    #    if thisArray is None: return
     #   self.pctTotalGFsynapses = getattr(thisArray, 'pctTotalGFsynapses', None)