import MyCustomGFNeuronClass as NC
import CustomeNeuronClassSet as NCS

mySet = NCS.builder()

mySet.updateSomata()
mySet.getAllGFINSynByBranch()
mySet.getNumPartersBySkid()

NotLinks = {'Ascending':["Descending", "CBOnly"], "Descending": ["Ascending", "CBonly"], "CBOnly" : ['Connectives', "Ascending", "Descending"], "bilateral": ['ipsilateral'], 'ipsilateral': ['bilateral']}

def getAssociations(mySet):
    AndLinks = {}    
    for i in mySet:
        for item in i.annotations:
            