import CustomNeuronClassSet as CS
import jsonNeurons as JN
import exportToCSV as E2C
import GetAnnotationsRemoveExtraneousInfo as GA

#commissure = 9809716

mySet = CS.builder()

myClassTypes = GA.queryByMetaAnnotation('classType')
for annotation in myClassTypes:
    globals()['{}'.format(annotation)] = []

myCommissures = GA.queryByMetaAnnotation('commissure')
finalCommissures = {}
for annotation in myCommissures:
    globals()['{}'.format(annotation)] = []
    finalCommissures[annotation] = []


#layer0 set the class types(e.g. visual, secondary_auditory, etc...)
def layer0(mySet):
    myClassTypes = GA.queryByMetaAnnotation('classType')
    classTypeGroups = {}
    for annotation in myClassTypes:
        globals()['{}'.format(annotation)] = []
        classTypeGroups[annotation] = []
    classTypeGroups['Unclassified'] = []
    for neuron in mySet:
        thisNeuron = False
        for annotation in neuron.annotations:
            if annotation in myClassTypes: #and annotation != "Visual_Interneuron" and annotation != "secondary_auditory_interneurons":  #(annotation == "Descending Neuron" or annotation == "Ascending Neuron" or annotation == "Visual"):
                globals()['{}'.format(annotation)].append(neuron.skeletonID)
                classTypeGroups[annotation].append(neuron)
                thisNeuron = True

        if thisNeuron is False:
            classTypeGroups['Unclassified'].append(neuron)

    return classTypeGroups


#layer 1 = set commissures for each classType
def layer1(mySet = None, classTypeGroups = None):

    myCommissures = GA.queryByMetaAnnotation('commissure')
    myCommissures.append('unilateral')
    print(myCommissures)
    finalCommissures = {}
    comClass = {}
    for annotation in myCommissures:
        globals()['{}'.format(annotation)] = []
        finalCommissures[annotation] = []
    if mySet is not None:
        for neuron in mySet:
            for annotation in neuron.annotations:
                if annotation in myCommissures:
                    globals()['{}'.format(annotation)].append(neuron.skeletonID)
                    finalCommissures[annotation].append(neuron.skeletonID)
    if classTypeGroups is not None:
        for aClass in classTypeGroups:
            comClass[aClass] = {}
            for neuron in classTypeGroups[aClass]:
                if neuron.commissure not in comClass[aClass]:
                    comClass[aClass][neuron.commissure] = [neuron]
                else:
                    comClass[aClass][neuron.commissure].append(neuron)

                #for annotation in neuron.annotations:

                    #if annotation in myCommissures:
                     #   if annotation not in comClass[aClass]:
                      #      comClass[aClass][annotation] = [neuron]
                       # else:
                        #    comClass[aClass][annotation].append(neuron)
    if bool(comClass) is False:
        return finalCommissures
    else:
        return comClass


#layer2 - set cell body rind for each commissure for each class type
def layer2(args):
    myRinds = GA.queryByMetaAnnotation('cellBodyRind')
    if type(args) is CS.GFIN_set:
        mySet = args
        finalRinds = {}
        for annotation in myRinds:
            globals()['{}'.format(annotation)] = []
            finalRinds[annotation] = []
        for neuron in mySet:
            for annotation in neuron.annotations:
                if annotation in myRinds:
                    globals()['{}'.format(annotation)].append(neuron.skeletonID)
                    finalRinds[annotation].append(neuron.skeletonID)
    else:
        CBR = {}
        comsAndClasses = args
        classList = list(comsAndClasses.keys())
        for aClass in classList:
            CBR[aClass] = {}
            for aCom in comsAndClasses[aClass]:
                CBR[aClass][aCom] = {}
                for neuron in comsAndClasses[aClass][aCom]:
                    for annotation in neuron.annotations:
                        if annotation in myRinds:
                            if annotation not in CBR[aClass][aCom]:
                                CBR[aClass][aCom][annotation] = [neuron]
                            else:
                                CBR[aClass][aCom][annotation].append(neuron)
                    if neuron.cellBodyRind is None:
                        if 'CBnotInBrain' not in CBR[aClass][aCom]:
                            CBR[aClass][aCom]['CBnotInBrain'] = [neuron]
                        else:
                            CBR[aClass][aCom]['CBnotInBrain'].append(neuron)


    return CBR

def layer3(args):

    pass








    '''
    if finalCommissures in args:
        comsAndRinds = {}
        #for annotation in myRinds:
        for commissure in finalCommissures:
            for skeleton in finalCommissures['commissure']:
                pass
    return finalRinds

    '''
