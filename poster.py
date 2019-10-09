import json
import CustomNeuronClassSet as CS
import createPlots as CP
import plotBuilder as PB
import plotly.graph_objs as go
import colour
from collections import defaultdict
import plotly.plotly as py
import numpy as np

'''
Neurons present in buildSet:
VPN = [284703, 292771, 1143611, 6107965]
OtherVisual = [7741106, 3734117]
VisualInterneuron = [867713, 2977775, 864634, 2438338]
JO = [7664963, 8255422, 8576699, 8578056, 9594272]
MechanoInter = [3785330, 1200640, 4140263, 4223727]
NonVisInter = [2416268, 2260024]
Ascending = [3483710, 2799979]
Descending = [3410595, 7164401]
GF = 4947529
GF2 = 291870
'''

def multimodalCheck(mySet):
    modals = ['Visual_Interneuron', 'Non-Visual_Interneuron', 'Mechanosensory Interneuron']
    multiModal = []
    for neuron in mySet:
        results = {}
        annos = neuron.annotations
        for mode in modals:
            results[mode] = annos.count(mode)
        if sum(results.values()) > 1:
            multiModal.append(neuron)
    for i in multiModal:
        if "JONeuron" in i.annotations:
            multiModal.remove(i)
        if "Visual" in i.annotations:
            multiModal.remove(i)
        if "Descending Neuron" in i.annotations:
            multiModal.remove(i)
        if "Ascending Neuron" in i.annotations:
            multiModal.remove(i)
    mmLen = len(multiModal)
    taggedModal = []
    for i in mySet:
        if "Multi-Modal" in i.annotations:
            taggedModal.append(i)
    tmLen = len(taggedModal)
    twoTag = []
    for i in mySet:
        if "Visual_Interneuron" in i.annotations and "Mechanosensory Interneuron" in i.annotations and "Descending Neuron" not in i.annotations and "Ascending Neuron" not in i.annotations:
            twoTag.append(i)
    ttLen = len(twoTag)
    diff_list = []
   # print(ttLen)
   # print(tmLen)
   # print(mmLen)
    if mmLen == tmLen == ttLen:
        return
    elif mmLen == tmLen != ttLen:
        mmNames = []
        ttNames= []
        for i in multiModal:
            mmNames.append(i.neuronName)
        for i in twoTag:
            ttNames.append(i.neuronName)
        diff_list = np.setdiff1d(mmNames, ttNames)
        print(diff_list)
        raise Exception("Two Tag not the same")
    elif mmLen != tmLen == ttLen:
        mmNames = []
        ttNames = []
        for i in multiModal:
            mmNames.append(i.neuronName)
        for i in twoTag:
            ttNames.append(i.neuronName)
        diff_list = np.setdiff1d(mmNames, ttNames)
        print(diff_list)
        raise Exception("Multi-Modal not the same")
    elif mmLen == ttLen != tmLen:
        mmNames = []
        tMNames = []
        for i in multiModal:
            mmNames.append(i.neuronName)
        for i in taggedModal:
            tMNames.append(i.neuronName)
        diff_list = np.setdiff1d(mmNames, tMNames)
        print(diff_list)
        raise Exception("Tagged Modal not the same")
    else:
        raise Exception("Unknown Error")
    return

def getPosterModalities(mySet):
    multimodalCheck(mySet)
    for i in mySet:
        if "Multi-Modal" in i.annotations:
            i.modality = 'Multi-Modal'
        elif "Visual_Interneuron" in i.annotations:
            i.modality = "Visual Interneuron"
        elif "Non-Visual_Interneuron" in i.annotations:
            i.modality = "Non-Visual Interneuron"
        elif "Mechanosensory Interneuron" in i.annotations:
            i.modality = "Mechanosensory Interneuron"
        if "Neuron Fragment" in i.annotations:
            i.modality = "Unknown"
        if "Descending Neuron" in i.annotations:
            i.modality = "Descending Neuron"
        if "Ascending Neuron" in i.annotations:
            i.modality = "Ascending Neuron"
        if "Visual" in i.annotations:
            i.modality = "VPN"
        if "JONeuron" in i.annotations:
            i.modality = "JONeuron"
        if "Other Visual" in i.annotations:
            i.modality = "VPN"
    return

'''def buildModalitySet():
    allIDs = [3410595, 7164401, 3483710, 2799979, 2416268, 2260024, 3785330, 1200640, 4140263, 4223727, 7664963,
              8255422, 8576699, 8578056, 9594272, 867713, 2977775, 864634, 2438338, 7741106, 3734117, 284703, 292771,
              1143611, 6107965]
    modalitySet = CS.buildFromSkidList(allIDs)
    modalitySet.findModality()
    return modalitySet'''

def buildPosterModalitySet():
    allIDs = [3410595, 7164401, 3483710, 2799979, 2416268, 2260024, 3785330, 1200640, 4140263, 4223727, 7664963,
              8255422, 8576699, 8578056, 9594272, 867713, 2977775, 864634, 2438338, 7741106, 3734117, 292771,
              1143611, 874409, 3658067]
    modalitySet = CS.buildFromSkidList(allIDs)
    getPosterModalities(modalitySet)
    return modalitySet

def createJSON(inputSet):
    aListOfNeurons = []
    for item in inputSet:
        mySKID = item.skeletonID
        color = item.curColor
        aNeuron = {
            "skeleton_id": mySKID,
            "color": color,
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    GF1 = {
        "skeleton_id": 4947529,
        "color": "rgb(135, 135, 135)",
        "opacity": 1
    }
    GF2 = {
        "skeleton_id": 291870,
        "color": "rgb(135, 135, 135)",
        "opacity": 1
    }
    aListOfNeurons.append(GF1)
    aListOfNeurons.append(GF2)
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    return myJSON

def modalityImage():
    modalitySet = buildPosterModalitySet()
    for i in modalitySet:
        if i.modality == "JONeuron":
            i.curColor = "rgb(255, 242, 0)"
        elif i.modality == "VPN":
            i.curColor = "rgb(197, 108, 240)"
        elif i.modality == "Multi-Modal":
            i.curColor = "rgb(6, 82, 221)"
        elif i.modality == "Visual Interneuron":
            i.curColor = "rgb(255, 56, 56)"
        elif i.modality == "Mechanosensory Interneuron":
            i.curColor = "rgb(255, 159, 26)"
        elif i.modality == "Non-Visual Interneuron":
            i.curColor = "rgb(58, 227, 116)"
        elif i.modality == "Ascending Neuron":
            i.curColor = "rgb(23, 192, 235)"
        elif i.modality == "Descending Neuron":
            i.curColor = "rgb(0,0,0)"
    myJSON = createJSON(modalitySet)
    c = open("ModalityImage.json", 'w')
    c.write(myJSON)
    c.close()
    return

'''
using the color website: https://flatuicolors.com/
scheme 1 = dutch top, scheme 2 = dutch bottom
scheme 3 = turkish, scheme 4 = german
a few colors may be switched out in schemes
'''

def colorSchemeJSON(modalitySet):
    for i in modalitySet:
        i.curColor = None
    getPosterModalities(modalitySet)
    for i in modalitySet:
        if i.modality == "JONeuron":
            i.curColor = "rgb(255, 242, 0)"
        elif i.modality == "VPN":
            i.curColor = "rgb(197, 108, 240)"
        elif i.modality == "Multi-Modal":
            i.curColor = "rgb(6, 82, 221)"
        elif i.modality == "Visual Interneuron":
            i.curColor = "rgb(255, 56, 56)"
        elif i.modality == "Mechanosensory Interneuron":
            i.curColor = "rgb(255, 159, 26)"
        elif i.modality == "Non-Visual Interneuron":
            i.curColor = "rgb(58, 227, 116)"
        elif i.modality == "Ascending Neuron":
            i.curColor = "rgb(23, 192, 235)"
        elif i.modality == "Descending Neuron":
            i.curColor = "rgb(0,0,0)"
    myJSON = createJSON(modalitySet)
    c = open("PosterColorScheme.json", 'w')
    c.write(myJSON)
    c.close()
    return


"""
LC4s = [310806, 873664, 873720, 874359, 1060221, 1060322, 1077585, 1108155, 1325578]
"""
"""
LPLC2s = [1143465, 5996597, 1143611, 1316553, 1316678, 1316994, 1317004, 3755062, 3815708]
"""
"""
GCI = [295022, 308072, 2369058]
"""
"""
JO = [7460597, 7426399, 7237462, 7196379, 6864302, 6544974, 6538032, 5296246, 3786320]
"""
"""
DNp06 = [3158872]
"""
"""
types = LC4, LPLC2, DNp06, GCI, JO
"""
def knownTypesJSON(type):
    LC4s = [310806, 873664, 873720, 874359, 1060221, 1060322, 1077585, 1108155, 1325578]
    LPLC2s = [1143465, 5996597, 1143611, 1316553, 1316678, 1316994, 1317004, 3755062, 3815708]
    GCI = [295022, 308072, 2369058]
    JO = [7460597, 7426399, 7237462, 7196379, 6864302, 6544974, 6538032, 5296246, 3786320]
    DNp06 = [3158872]

    if type == "LC4":
        LC4Set = CS.buildFromSkidList(LC4s)
        for i in LC4Set:
            i.curColor = "rgb(197, 108, 240)"
        myJSON = createJSON(LC4Set)
    elif type == "LPLC2":
        LPLC2Set = CS.buildFromSkidList(LPLC2s)
        for i in LPLC2Set:
            i.curColor = "rgb(197, 108, 240)"
        myJSON = createJSON(LPLC2Set)
    elif type == "GCI":
        GCISet = CS.buildFromSkidList(GCI)
        for i in GCISet:
            i.curColor = "rgb(255, 56, 56)"
        myJSON = createJSON(GCISet)
    elif type == "JO":
        JOSet = CS.buildFromSkidList(JO)
        for i in JOSet:
            i.curColor = "rgb(255, 242, 0)"
        myJSON = createJSON(JOSet)
    elif type == "DNp06":
        DNp06Set = CS.buildFromSkidList(DNp06)
        for i in DNp06Set:
            i.curColor = "rgb(0,0,0)"
        myJSON = createJSON(DNp06Set)

    c = open("Known" + str(type) + "colored.json", 'w')
    c.write(myJSON)
    c.close()
    return



#---------------------------------------------------------------------------------------------------

#histogram by type
def gfClassHistogram(mySet, filename='Poster/HistogramByType_Synapse'):
    mySet = CS.sortBySynH2L(mySet)
    classes = []
    GF1Syn = []
    mySetCopy = CP.shortenClassNames(mySet)

    classif = defaultdict(list)
    for neuron in mySetCopy:
        classes.append(neuron.classification)
        GF1Syn.append(neuron.GF1synapseCount)
        classif[neuron.classification].append(neuron.GF1synapseCount)

    countsList = []
    for v in classif.values():
        countsList.append(len(v))
    keys = list(classif.keys())
    values = []
    for k, v in classif.items():
        sum = 0
        for syn in v:
            sum = sum + syn
        values.append(sum)

    values, keys, countsList = zip(*sorted(zip(values, keys, countsList),reverse=True))
    countsList = list(countsList)

    trace1 = go.Bar(
        x= keys,
        y=values,
        text=countsList,
        textposition='outside'
    )
    data = [trace1]
    layout = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        title="Class Synapse Count",
        yaxis=dict(title='Synapse Count'),
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return

#histogram by type
def gfClassHistogram2(mySet, filename='Poster/HistogramByType_Neuron'):
    mySet = CS.sortBySynH2L(mySet)
    classes = []
    GF1Syn = []
    mySetCopy = CP.shortenClassNames(mySet)

    classif = defaultdict(list)
    for neuron in mySetCopy:
        classes.append(neuron.classification)
        GF1Syn.append(neuron.GF1synapseCount)
        classif[neuron.classification].append(neuron.GF1synapseCount)

    countsList = []
    for v in classif.values():
        countsList.append(len(v))
    keys = list(classif.keys())
    values = []
    lengths = []
    for k, v in classif.items():
        sum = 0
        lengths.append(len(v))
        for syn in v:
            sum = sum + syn
        values.append(sum)


    lengths, keys, countsList = zip(*sorted(zip(lengths, keys, countsList),reverse=True))
    countsList = list(countsList)

    trace1 = go.Bar(
        x=keys,
        y=lengths,
        textposition='outside'
    )
    data = [trace1]
    layout = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        title="Class Synapse Count",
        yaxis=dict(title='Synapse Count'),
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return



def makePosterModalityBars(mySet, filename='Poster/ModalityBars'):
    mySetCopy = CP.shortenClassNames(mySet)
    #removed other visual
    keys = ['VPN', 'Non-Visual Interneuron', 'JONeuron', 'Mechanosensory Interneuron',
            'Visual Interneuron', 'Multi-Modal', 'Descending Neuron',
            'Ascending Neuron', 'Unknown']
    modalities = {k: [] for k in keys}
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)
    modalities.pop('Unknown')
    keys = list(modalities.keys())
    values = []
    for k, v in modalities.items():
        values.append(len(v))
    # H -> L : VPN, NVI, JO, MI, VI, MM, DN, AN
    colors = ['rgb(197, 108, 240)', "rgb(58, 227, 116)",
              'rgb(255, 242, 0)', 'rgb(255, 159, 26)', "rgb(255, 56, 56)",
              "rgb(6, 82, 221)", 'rgb(0,0,0)', "rgb(23, 192, 235)"]
    Modalities = go.Bar(
        name='Modalities',
        x=keys,
        y=values,
        # text=values,
        textposition='auto',
        marker=dict(color=colorbis)

    )
    layout = go.Layout(autosize=False,
                       showlegend=False,
                       margin=dict(b=200),
                       bargap=0
                       # title='Modality Bars by Neuron Count',
                       # xaxis=dict(
                       #    tickfont=dict(size=20),
                       #    range=[-0.5, 10]
                       # ),
                       # yaxis=dict(title='Neuron Count'),
                       # legend=dict(
                       #    font=dict(
                       #        size=30
                       #    )
                       # )
                       )
    data = [Modalities]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return


def makePosterModalityBarsBySynapse(mySet, filename='Poster/ModalityBarsSynapse'):
    mySetCopy = CP.shortenClassNames(mySet)
    #removed other visual
    getPosterModalities(mySetCopy)
    keys = ['VPN', 'Multi-Modal','Mechanosensory Interneuron', "JONeuron",
            'Non-Visual Interneuron', 'Visual Interneuron', 'Descending Neuron',
            'Ascending Neuron', 'Unknown']
    modalities = {k: [] for k in keys}
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)
    modalities.pop('Unknown')
    keys = list(modalities.keys())
    values = defaultdict(int)
    GFSyns = 0
    for k, v in modalities.items():
        for neuron in v:
            GFSyns = GFSyns + neuron.GF1synapseCount
        values[k] = GFSyns
        GFSyns = 0
    # H -> L : VPN, MM, MI, JO, NVI, VI, DN, AN
    colors = ['rgb(197, 108, 240)', "rgb(6, 82, 221)",
              "rgb(255, 159, 26)", "rgb(255, 242, 0)", "rgb(58, 227, 116)",
              "rgb(255, 56, 56)", 'rgb(0,0,0)', "rgb(23, 192, 235)"]
    values2 = list(values.values())
    Modalities = go.Bar(
        name='Modalities',
        x=keys,
        y=values2,
        # text=values,
        textposition='auto',
        marker=dict(color=colors)

    )
    layout = go.Layout(autosize=False,
                       showlegend=False,
                       margin=dict(b=200),
                       bargap=0
                       # title='Modality Bars by Neuron Count',
                       # xaxis=dict(
                       #    tickfont=dict(size=20),
                       #    range=[-0.5, 10]
                       # ),
                       # yaxis=dict(title='Neuron Count'),
                       # legend=dict(
                       #    font=dict(
                       #        size=30
                       #    )
                       # )
                       )
    data = [Modalities]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return



def makePosterTopInputtingPlotAll(mySet, filename='Poster/Top10'):
    mySetCopy = CP.shortenClassNames(mySet)
    summedDict = CP.synapseDict(mySetCopy)

    top10 = {k: summedDict[k] for k in list(summedDict)[:10]}

   #colors = ['rgb(197, 108, 240)', 'rgb(255, 242, 0)', 'rgb(197, 108, 240)',
     #             'rgb(240,0,172)', 'rgb(240,0,172)', 'rgb(240,0,172)',
    #              'rgb(240,0,172)', 'rgb(240,0,172)', 'rgb(240,0,172)',
      #            'rgb(240,0,172)']
#VPN, JO, VPN, MI, MM, MM, MI, MM, DESC, NVI
    colors = ['rgb(197, 108, 240)', 'rgb(255, 242, 0)', 'rgb(197, 108, 240)',
              "rgb(255, 56, 56)", "rgb(6, 82, 221)", "rgb(6, 82, 221)",
              "rgb(255, 159, 26)", "rgb(6, 82, 221)", "rgb(0,0,0)", "rgb(58, 227, 116)"]
    keys = list(top10.keys())
    keys = ['LC4', 'JO', 'LPLC2', 'Type 25', 'Type 10', 'Type 8', 'Type 30*', 'Type 31*', 'Type 3', 'Type 2a*']
    values = list(top10.values())
    trace1 = go.Bar(
        x = keys,
        y=values,
        marker=dict(color=list(colors)),
        text=None,
        #width=[0.3, 0.3, 0.3, 0.3, 0.3,0.3, 0.3, 0.3, 0.3, 0.3]
    )
    data = [trace1]
    layout = go.Layout(
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        xaxis=None,
        bargap = 0
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return


def makePosterTopTenNeurons(mySet, filename='Poster/Top10Neurons'):
    mySet = CS.sortBySynH2L(mySet)
    top10 = mySet[0:10]
    getPosterModalities(mySet)
    colors = []
    for i in top10:
        if i.modality == "JONeuron":
            i.curColor = "rgb(255, 242, 0)"
        elif i.modality == "VPN":
            i.curColor = "rgb(197, 108, 240)"
        elif i.modality == "Multi-Modal":
            i.curColor = "rgb(6, 82, 221)"
        elif i.modality == "Visual Interneuron":
            i.curColor = "rgb(255, 56, 56)"
        elif i.modality == "Mechanosensory Interneuron":
            i.curColor = "rgb(255, 159, 26)"
        elif i.modality == "Non-Visual Interneuron":
            i.curColor = "rgb(58, 227, 116)"
        elif i.modality == "Ascending Neuron":
            i.curColor = "rgb(23, 192, 235)"
        elif i.modality == "Descending Neuron":
            i.curColor = "rgb(0,0,0)"
    neuronNames = []
    GFSYN = []
    for i in top10:
        colors.append(i.curColor)

    for neuron in top10:
        GFSYN.append(neuron.GF1synapseCount)
        neuronNames.append(neuron.neuronName)

    aListOfNeurons = []
    for item in top10:
        mySKID = item.skeletonID
        aNeuron = {
            "skeleton_id": mySKID,
            "color": item.curColor,
            "opacity": 1
        }
        aListOfNeurons.append(aNeuron)
    myJSON = json.dumps(aListOfNeurons, separators=(', \n', ': '))
    c = open('top10Neurons.json', 'w')
    c.write(myJSON)
    c.close()
    trace1 = go.Bar(
        y=GFSYN,
        x=neuronNames,
        marker=dict(color=list(colors))
    )
    data = [trace1]
    layout = go.Layout(
        margin=go.layout.Margin(
            b=300,
            r=200
        )
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return

def makePosterSynapseBars(mySet, filename='Poster/Synapse Count Bars'):
    mySet = CS.sortBySynH2L(mySet)
    GFSYN = []
    neuronNames = []
    for neuron in mySet:
        GFSYN.append(neuron.GF1synapseCount)
        neuronNames.append(neuron.neuronName)
    colors = []
    color = str()
    getPosterModalities(mySet)
    for i in mySet:
        if i.modality == "JONeuron":
            i.curColor = "rgb(255, 242, 0)"
        elif i.modality == "VPN":
            i.curColor = "rgb(197, 108, 240)"
        elif i.modality == "Multi-Modal":
            i.curColor = "rgb(6, 82, 221)"
        elif i.modality == "Visual Interneuron":
            i.curColor = "rgb(255, 56, 56)"
        elif i.modality == "Mechanosensory Interneuron":
            i.curColor = "rgb(255, 159, 26)"
        elif i.modality == "Non-Visual Interneuron":
            i.curColor = "rgb(58, 227, 116)"
        elif i.modality == "Ascending Neuron":
            i.curColor = "rgb(23, 192, 235)"
        elif i.modality == "Descending Neuron":
            i.curColor = "rgb(0,0,0)"
        else:
            i.curColor = "rgb(192,192,192)"
        colors.append(i.curColor)
    trace1 = go.Bar(
        y=GFSYN,
        marker=dict(color=colors)
    )
    data = [trace1]
    layout = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        # title="Individual Neuron Synapse Count"
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return




def makePosterStackedModalityByNeuron(mySet, filename='Poster/Stacked Modalities By Neuron Count'):
    mySetCopy = CP.shortenClassNames(mySet)
    branches = defaultdict(list)
    for neuron in mySetCopy:
        if "Input to GF1 anterior" in neuron.annotations:
            branches["Anterior"].append(neuron)
        if "Input to GF1 lateral" in neuron.annotations:
            branches["Lateral"].append(neuron)
        if "Input to GF1 medial" in neuron.annotations:
            branches["Medial"].append(neuron)
        if "Input to GF1 descending tract" in neuron.annotations:
            branches["Descending Tract"].append(neuron)
        if "Input to GF1 soma tract" in neuron.annotations:
            branches["Soma Tract"].append(neuron)

    AnteriorModes = defaultdict(list)
    LateralModes = defaultdict(list)
    MedialModes = defaultdict(list)
    DescendingModes = defaultdict(list)
    SomaModes = defaultdict(list)

    for neuron in branches['Anterior']:
        AnteriorModes[neuron.modality].append(neuron)
    for neuron in branches['Lateral']:
        LateralModes[neuron.modality].append(neuron)
    for neuron in branches['Medial']:
        MedialModes[neuron.modality].append(neuron)
    for neuron in branches['Descending Tract']:
        DescendingModes[neuron.modality].append(neuron)
    for neuron in branches['Soma Tract']:
        SomaModes[neuron.modality].append(neuron)

    AnteriorModesSummed = defaultdict(int)
    for k, v in AnteriorModes.items():
        AnteriorModesSummed[k] = len(v)
    # AnteriorModesSummed.pop('default_factory')

    LateralModesSummed = defaultdict(int)
    for k, v in LateralModes.items():
        LateralModesSummed[k] = (len(v))
    # LateralModesSummed.pop('default_factory')
    MedialModesSummed = defaultdict(int)
    for k, v in MedialModes.items():
        MedialModesSummed[k] = (len(v))
    # MedialModesSummed.pop('default_factory')
    DescendingModesSummed = defaultdict(int)
    for k, v in DescendingModes.items():
        DescendingModesSummed[k] = (len(v))
    # DescendingModesSummed.pop('default_factory')
    SomaModesSummed = defaultdict(int)
    for k, v in SomaModes.items():
        SomaModesSummed[k] = (len(v))
    # SomaModesSummed.pop('default_factory')

    VPN = []
    VI = []
    MM = []
    NVI = []
    JO = []
    MI = []
    DN = []
    AN = []

    branches = ["Anterior", "Lateral", "Medial", "Descending Tract", "Soma Tract"]
    allBranchesSummed = [AnteriorModesSummed, LateralModesSummed,
                         MedialModesSummed, DescendingModesSummed,
                         SomaModesSummed]
    for branch in allBranchesSummed:
        if 'Visual Interneuron' in branch:
            VI.append(branch['Visual Interneuron'])
        else:
            VI.append(0)
        if 'VPN' in branch:
            VPN.append(branch['VPN'])
        else:
            VPN.append(0)
        if 'Multi-Modal' in branch:
            MM.append(branch['Multi-Modal'])
        else:
            MM.append(0)
        if 'Non-Visual Interneuron' in branch:
            NVI.append(branch['Non-Visual Interneuron'])
        else:
            NVI.append(0)
        if 'JONeuron' in branch:
            JO.append(branch['JONeuron'])
        else:
            JO.append(0)
        if 'Mechanosensory Interneuron' in branch:
            MI.append(branch['Mechanosensory Interneuron'])
        else:
            MI.append(0)
        if 'Descending Neuron' in branch:
            DN.append((branch['Descending Neuron']))
        else:
            DN.append(0)
        if 'Ascending Neuron' in branch:
            AN.append(branch['Ascending Neuron'])
        else:
            AN.append(0)

    sumAnt = sum(AnteriorModesSummed.values())
    sumLat = sum(LateralModesSummed.values())
    sumMed = sum(MedialModesSummed.values())
    sumDesc = sum(DescendingModesSummed.values())
    sumSoma = sum(SomaModesSummed.values())

    trace1 = go.Bar(
        y=branches,
        x=VPN,
        # text=VPN,
        # textposition='auto',
        name='VPN',
        marker=dict(color='rgb(197, 108, 240)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace2 = go.Bar(
        y=branches,
        x=MM,
        # text=OV,
        # textposition='auto',
        name='Multi-Modal',
        marker=dict(color='rgb(6, 82, 221)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace3 = go.Bar(
        y=branches,
        x=VI,
        # text=VI,
        # textposition='auto',
        name='Visual Interneuron',
        marker=dict(color='rgb(255, 56, 56)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace4 = go.Bar(
        y=branches,
        x=JO,
        # text=JO,
        # textposition='auto',
        name='JONeuron',
        marker=dict(color='rgb(255, 242, 0)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
      orientation='h'
    )
    trace5 = go.Bar(
        y=branches,
        x=MI,
        # text=MI,
        # textposition='auto',
        name='Mechanosensory Interneuron',
        marker=dict(color='rgb(255, 159, 26)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace6 = go.Bar(
        y=branches,
        x=NVI,
        # text=NVI,
        # textposition='auto',
        name='Non-Visual Interneuron',
        marker=dict(color='rgb(58, 227, 116)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace7 = go.Bar(
        y=branches,
        x=AN,
        # text=AN,
        # textposition='auto',
        name='Ascending Neuron',
        marker=dict(color='rgb(23, 192, 235)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace8 = go.Bar(
        y=branches,
        x=DN,
        # text=DN,
        # textposition='auto',
        name='Descending Neuron',
        marker=dict(color='rgb(0,0,0)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    layout = go.Layout(
        barmode='stack',
        autosize=False,
        # title="Modality by Branch by Neuron Count",
        barnorm='percent',
        # xaxis=dict(title='Neuron Count'),
        # yaxis=dict(
        #    tickfont=dict(size=10)
        # )
    )
    data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return

def makePosterStackedModalityBySynapse(mySet, filename='Poster/Stacked Modalities by Synapse'):
    mySetCopy = CP.shortenClassNames(mySet)
    branches = defaultdict(list)
    for neuron in mySetCopy:
        if "Input to GF1 anterior" in neuron.annotations:
            branches["Anterior"].append(neuron)
        if "Input to GF1 lateral" in neuron.annotations:
            branches["Lateral"].append(neuron)
        if "Input to GF1 medial" in neuron.annotations:
            branches["Medial"].append(neuron)
        if "Input to GF1 descending tract" in neuron.annotations:
            branches["Descending Tract"].append(neuron)
        if "Input to GF1 soma tract" in neuron.annotations:
            branches["Soma Tract"].append(neuron)

    AnteriorModes = defaultdict(list)
    LateralModes = defaultdict(list)
    MedialModes = defaultdict(list)
    DescendingModes = defaultdict(list)
    SomaModes = defaultdict(list)

    for neuron in branches['Anterior']:
        AnteriorModes[neuron.modality].append(neuron)
    for neuron in branches['Lateral']:
        LateralModes[neuron.modality].append(neuron)
    for neuron in branches['Medial']:
        MedialModes[neuron.modality].append(neuron)
    for neuron in branches['Descending Tract']:
        DescendingModes[neuron.modality].append(neuron)
    for neuron in branches['Soma Tract']:
        SomaModes[neuron.modality].append(neuron)

    GFSyns = 0
    AnteriorModesSummed = defaultdict(int)
    for k, v in AnteriorModes.items():
        for neuron in v:
            GFSyns = GFSyns + neuron.synapsesByBranch['anterior']
        AnteriorModesSummed[k] = GFSyns
        GFSyns = 0

    LateralModesSummed = defaultdict(int)
    for k, v in LateralModes.items():
        for neuron in v:
            GFSyns = GFSyns + neuron.synapsesByBranch['lateral']
        LateralModesSummed[k] = GFSyns
        GFSyns = 0

    MedialModesSummed = defaultdict(int)
    for k, v in MedialModes.items():
        for neuron in v:
            GFSyns = GFSyns + neuron.synapsesByBranch['medial']
        MedialModesSummed[k] = GFSyns
        GFSyns = 0

    DescendingModesSummed = defaultdict(int)
    for k, v in DescendingModes.items():
        for neuron in v:
            GFSyns = GFSyns + neuron.synapsesByBranch['descending tract']
        DescendingModesSummed[k] = GFSyns
        GFSyns = 0

    SomaModesSummed = defaultdict(int)
    for k, v in SomaModes.items():
        for neuron in v:
            GFSyns = GFSyns + neuron.synapsesByBranch['soma tract']
        SomaModesSummed[k] = GFSyns
        GFSyns = 0

    VPN = []
    VI = []
    MM = []
    NVI = []
    JO = []
    MI = []
    DN = []
    AN = []

    branches = ["Anterior", "Lateral", "Medial", "Descending Tract", "Soma Tract"]
    allBranchesSummed = [AnteriorModesSummed, LateralModesSummed,
                         MedialModesSummed, DescendingModesSummed,
                         SomaModesSummed]
    for branch in allBranchesSummed:
        if 'Visual Interneuron' in branch:
            VI.append(branch['Visual Interneuron'])
        else:
            VI.append(0)
        if 'VPN' in branch:
            VPN.append(branch['VPN'])
        else:
            VPN.append(0)
        if 'Multi-Modal' in branch:
            MM.append(branch['Multi-Modal'])
        else:
            MM.append(0)
        if 'Non-Visual Interneuron' in branch:
            NVI.append(branch['Non-Visual Interneuron'])
        else:
            NVI.append(0)
        if 'JONeuron' in branch:
            JO.append(branch['JONeuron'])
        else:
            JO.append(0)
        if 'Mechanosensory Interneuron' in branch:
            MI.append(branch['Mechanosensory Interneuron'])
        else:
            MI.append(0)
        if 'Descending Neuron' in branch:
            DN.append((branch['Descending Neuron']))
        else:
            DN.append(0)
        if 'Ascending Neuron' in branch:
            AN.append(branch['Ascending Neuron'])
        else:
            AN.append(0)

    trace1 = go.Bar(
        y=branches,
        x=VPN,
        # text=VPN,
        # textposition='auto',
        name='VPN',
        marker=dict(color='rgb(197, 108, 240)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace2 = go.Bar(
        y=branches,
        x=MM,
        # text=OV,
        # textposition='auto',
        name='Multi-Modal',
        marker=dict(color='rgb(6, 82, 221)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace3 = go.Bar(
        y=branches,
        x=VI,
        # text=VI,
        # textposition='auto',
        name='Visual Interneuron',
        marker=dict(color='rgb(255, 56, 56)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace4 = go.Bar(
        y=branches,
        x=JO,
        # text=JO,
        # textposition='auto',
        name='JONeuron',
        marker=dict(color='rgb(255, 242, 0)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace5 = go.Bar(
        y=branches,
        x=MI,
        # text=MI,
        # textposition='auto',
        name='Mechanosensory Interneuron',
        marker=dict(color='rgb(255, 159, 26)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace6 = go.Bar(
        y=branches,
        x=NVI,
        # text=NVI,
        # textposition='auto',
        name='Non-Visual Interneuron',
        marker=dict(color='rgb(58, 227, 116)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace7 = go.Bar(
        y=branches,
        x=AN,
        # text=AN,
        # textposition='auto',
        name='Ascending Neuron',
        marker=dict(color='rgb(23, 192, 235)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    trace8 = go.Bar(
        y=branches,
        x=DN,
        # text=DN,
        # textposition='auto',
        name='Descending Neuron',
        marker=dict(color='rgb(0,0,0)'),
        # width=[0.3, 0.3, 0.3, 0.3, 0.3],
        orientation='h'
    )
    layout = go.Layout(
        barmode='stack',
        autosize=False,
        # title="Modality by Branch by Synapse Count",
        barnorm='percent',
        # xaxis=dict(title='Synapse Count'),
        # yaxis=dict(
        #    tickfont=dict(size=10)
        # )
    )
    data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return



# returns list of neurons in mySet that have the modality given.
def modalityList(mySet, modality):
    modalityOnly = []
    for i in mySet:
        if i.modality == modality:
            modalityOnly.append(i)

    return modalityOnly

def modalitySkid(mySet, modality):
    modalSkid = []
    modalOnly = modalityList(mySet, modality)
    for item in modalOnly:
        modalSkid.append(item.skeletonID)

    return modalSkid
# returns tuple of connectorID, {cID, x, y, z, conf, partners)
# includes ALL partners of connector ID
# MUST use another formula to retrieve relevant skeletons
# Can be used for XYZ coordinates
# params: mySet - gf set, allInfo - returned list from 'getSynInfo', modality - string
def modalitySynapses(mySet, allInfo, modality):

    modal_Skid = modalitySkid(mySet, modality)

    modal_Syn = []
    for item in allInfo.items():
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                if partner['skeleton_id'] in modal_Skid:
                    modal_Syn.append(item)

    return modal_Syn

def getModalityTrace(mySet, allInfo, modality, rgb):
    x_vals = []
    y_vals = []
    z_vals = []
    synapses = modalitySynapses(mySet, allInfo, modality)
    for item in synapses:
        x_vals.append(item[1]['x'])
        y_vals.append(item[1]['y'])
        z_vals.append(item[1]['z'])
    modalTrace = go.Scatter3d(
        x=x_vals,
        y=y_vals,
        z=z_vals,
        mode='markers',
        marker=dict(
            size=5,
            color=rgb),
        name=modality)
    return modalTrace

def createModalityScatterPlot(mySet, allInfo):
    Structure = CP.createStructure()
    VPN = getModalityTrace(mySet, allInfo, "VPN", 'rgb(197, 108, 240)')
    JONeuron = getModalityTrace(mySet, allInfo, "JONeuron", 'rgb(255, 242, 0)')
    MultiModal = getModalityTrace(mySet, allInfo, "Multi-Modal", 'rgb(6, 82, 221)')
    VisualInterneuron = getModalityTrace(mySet, allInfo, "Visual Interneuron", 'rgb(255, 56, 56)')
    MechanoInterneuron = getModalityTrace(mySet, allInfo, "Mechanosensory Interneuron", 'rgb(255, 159, 26)')
    NonVisInterneuron = getModalityTrace(mySet, allInfo, "Non-Visual Interneuron", 'rgb(58, 227, 116)')
    Ascending = getModalityTrace(mySet, allInfo, "Ascending Neuron", 'rgb(23, 192, 235)')
    Descending = getModalityTrace(mySet, allInfo, "Descending Neuron", 'rgb(0, 0, 0)')

    allData = [Structure, VPN, JONeuron, MultiModal, VisualInterneuron, MechanoInterneuron, NonVisInterneuron,

               Ascending, Descending]

    PB.createPlotlyPlot(allData, "Poster/All Modality Synapse Scatter")
    return
