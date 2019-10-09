import CustomNeuronClassSet as CS
import MyCustomGFNeuronClass as GF
import colour
import scipy as sp
import requests
import json
import os
import datetime
import config
import pandas as pd
import numpy as np
import plotBuilder as PB
from collections import defaultdict
import exportToCSV as e2c
import jsonNeurons as JN
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
from collections import OrderedDict
from copy import copy, deepcopy
now = datetime.datetime.now()
token = config.token
project_id = config.project_id
py.sign_in('CardLab', 'NsYwbHlFACg2IWkRUJvs')
#plotly.tools.set_credentials_file(username='CardLab', api_key='NsYwbHlFACg2IWkRUJvs')
'''
mySet = CS.builder()
mySet = CS.sortBySynL2H(mySet)

#gets soma node xyz
#mySet.updateSomata()

#gets all node coordinate points of every neuron in set - don't run unless this info is necessary
#mySet.updateSkeletonNodes()
#allSynapseCoordinates = id:[x,y,z,presynaptic skeleton id -- only if branches is run..?]
#takes a while to run
# mySet.combineAllSynLocations()

#connector xyz location and partner info
mySet.getConnectors()

#Get partner info (visual partners)
mySet.getNumPartnersBySkid()

#Breakdown syn count by branch
mySet.getAllGFINSynByBranch()

mySet.findNeuropils()
mySet.findBranchDistributions()

mySet.combineAllSynLocations()
import SynapseClustering as PB
allInfo = PB.getSynInfo(mySet)
'''

#CP.makeBranchPieCharts(mySet, allInfo)
#CP.makeBranchMorphologyPie(mySet, 'anterior')
#CP.makeBranchMorphologyPie(mySet, 'medial')
#CP.makeBranchMorphologyPie(mySet, 'lateral')
#CP.makeBranchMorphologyPie(mySet, 'soma tract')
#CP.makeBranchMorphologyPie(mySet, 'descending tract')


# dict of neuron types and synapse counts
def synapseDict(mySet):
    synapseDict = defaultdict(list)
    for i in mySet:
        synapseDict[i.classification].append(i.GF1synapseCount)

    summedDict = defaultdict(list)
    for k, v in synapseDict.items():
        sum = 0
        for synCount in v:
            sum = sum + synCount
        summedDict[k].append(int(sum))
    keys = summedDict.keys()
    values = summedDict.values()
    values, keys = zip(*sorted(zip(values, keys)))
    values = reversed(values)
    keys = reversed(keys)
    summedDict = dict(zip(keys, values))
    return summedDict

#removes "GF Input neuron" part from name to make plots look better if labels are turned on
def shortenClassNames(mySet):
    mySetCopy = mySet
    for neuron in mySetCopy:
        classif = neuron.classification
        classif = classif.replace('Unclassified GF input neuron - ', '')
        neuron.classification = classif
        neuron.neuronName = str(neuron.skeletonID) + " " + classif
    return mySetCopy

# creates structure for plotly plots
# prevents plots from resizing when showing/hiding traces
def createStructure():
    x_vals = [401000, 550000, 401000, 550000, 401000, 550000, 401000, 550000]
    y_vals = [192000, 192000, 298000, 298000, 192000, 192000, 298000, 298000]
    z_vals = [40960, 40960, 40960, 40960, 222320, 222320, 222320, 222320]

    Structure = go.Scatter3d(
        x=x_vals,
        y=y_vals,
        z=z_vals,
        mode='markers',
        marker=dict(
            size=1,
            color="rgb(255,255,255)"),
        name="STRUCTURE")
    return Structure


# data MUST be in brackets [] even if just one item
def createPlotlyPlot(data, name):
    layout = go.Layout(
        title=name,
        legend=dict(x=-.05, y=0.5),
        scene=dict(
            xaxis=dict(
                title='x Axis'),
            yaxis=dict(
                title='y Axis'),
            zaxis=dict(
                title='z Axis')),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=100
        )
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=name)
    return

#data dict by classification; each classification will have all neurons of that type
#as a value
def createDataDict(mySet):
    dataDict = defaultdict(list)
    for i in mySet:
        dataDict[i.classification].append(i)
    dataDict = OrderedDict(sorted(dataDict.items(), key=lambda x: len(x[1])))
    return dataDict


# creates Pie Charts of branch inputs
def makeBranchPieCharts(mySet, allInfo):
    branchList = ['anterior', 'lateral', 'medial', 'soma tract', 'descending tract']
    mySetCopy = []
    for neuron in mySet:
        if "Unclassified GF input neuron - Fragment" not in neuron.annotations:
            mySetCopy.append(neuron)
    mySetCopy = CS.GFIN_set(mySetCopy)
    mySetCopy.getConnectors()
    aSKID = PB.branchPreSynPartnersSkid(mySetCopy, allInfo, 'anterior')
    aNames = defaultdict(list)
    aSkids = defaultdict(list)
    aSums = defaultdict(list)
    aClassSums = defaultdict(list)
    for v in aSKID:
        aSkids[v].append(1)
    for k, v in aSkids.items():
        aSums[k].append(sum(v))
    for k, v in aSums.items():
        for item in mySet:
            if k == item.skeletonID:
                aNames[item.classification].append(v)
    for k, v in aNames.items():
        total = 0
        for n in v:
            total = total + n[0]
        aClassSums[k].append(total)

    if 'default_factory' in aClassSums.keys():
        aClassSums.pop('default_factory')
    atrace = go.Pie(labels=list(aClassSums.keys()), values=list(aClassSums.values()),
                    hoverinfo='label+percent', textinfo='label+value',
                    textfont=dict(size=20),
                    name='Anterior',
                    marker=dict(
                        line=dict(color='#000000', width=2)
                    ))

    lSKID = PB.branchPreSynPartnersSkid(mySet, allInfo, 'lateral')
    lNames = defaultdict(list)
    lSkids = defaultdict(list)
    lSums = defaultdict(list)
    lClassSums = defaultdict(list)
    for v in lSKID:
        lSkids[v].append(1)
    for k, v in lSkids.items():
        lSums[k].append(sum(v))
    for k, v in lSums.items():
        for item in mySet:
            if k == item.skeletonID:
                lNames[item.classification].append(v)
    for k, v in lNames.items():
        total = 0
        for n in v:
            total = total + n[0]
        lClassSums[k].append(total)

    if 'default_factory' in lClassSums.keys():
        lClassSums.pop('default_factory')
    ltrace = go.Pie(labels=list(lClassSums.keys()), values=list(lClassSums.values()),
                    hoverinfo='label+percent', textinfo='label+value',
                    textfont=dict(size=20),
                    name='Lateral',
                    marker=dict(
                        line=dict(color='#000000', width=2)
                    ))

    mSKID = PB.branchPreSynPartnersSkid(mySet, allInfo, 'medial')
    mNames = defaultdict(list)
    mSkids = defaultdict(list)
    mSums = defaultdict(list)
    mClassSums = defaultdict(list)
    for v in mSKID:
        mSkids[v].append(1)
    for k, v in mSkids.items():
        mSums[k].append(sum(v))
    for k, v in mSums.items():
        for item in mySet:
            if k == item.skeletonID:
                mNames[item.classification].append(v)
    for k, v in mNames.items():
        total = 0
        for n in v:
            total = total + n[0]
        mClassSums[k].append(total)

    if 'default_factory' in mClassSums.keys():
        mClassSums.pop('default_factory')
    mtrace = go.Pie(labels=list(mClassSums.keys()), values=list(mClassSums.values()),
                    hoverinfo='label+percent', textinfo='label+value',
                    textfont=dict(size=20),
                    name='Medial',
                    marker=dict(
                        line=dict(color='#000000', width=2)
                    ))

    sSKID = PB.branchPreSynPartnersSkid(mySet, allInfo, 'soma tract')
    sNames = defaultdict(list)
    sSkids = defaultdict(list)
    sSums = defaultdict(list)
    sClassSums = defaultdict(list)
    for v in sSKID:
        sSkids[v].append(1)
    for k, v in sSkids.items():
        sSums[k].append(sum(v))
    for k, v in sSums.items():
        for item in mySet:
            if k == item.skeletonID:
                sNames[item.classification].append(v)
    for k, v in sNames.items():
        total = 0
        for n in v:
            total = total + n[0]
        sClassSums[k].append(total)

    if 'default_factory' in sClassSums.keys():
        sClassSums.pop('default_factory')
    strace = go.Pie(labels=list(sClassSums.keys()), values=list(sClassSums.values()),
                    hoverinfo='label+percent', textinfo='label+value',
                    textfont=dict(size=20),
                    name='Soma Tract',
                    marker=dict(
                        line=dict(color='#000000', width=2)
                    ))

    dSKID = PB.branchPreSynPartnersSkid(mySet, allInfo, 'descending tract')
    dNames = defaultdict(list)
    dSkids = defaultdict(list)
    dSums = defaultdict(list)
    dClassSums = defaultdict(list)
    for v in dSKID:
        dSkids[v].append(1)
    for k, v in dSkids.items():
        dSums[k].append(sum(v))
    for k, v in dSums.items():
        for item in mySet:
            if k == item.skeletonID:
                dNames[item.classification].append(v)
    for k, v in dNames.items():
        total = 0
        for n in v:
            total = total + n[0]
        dClassSums[k].append(total)

    if 'default_factory' in dClassSums.keys():
        dClassSums.pop('default_factory')
    dtrace = go.Pie(labels=list(dClassSums.keys()),
                    values=list(dClassSums.values()),
                    hoverinfo='label+percent', textinfo='label+value',
                    textfont=dict(size=20),
                    name='Descending Tract',
                    marker=dict(
                        line=dict(color='#000000', width=2)
                    ))
    '''for branch in branchList:
        branchSKID = branchPreSynPartnersSkid(mySet, allInfo, branch)
        branchNames = defaultdict(list)
        branchSkids = defaultdict(list)
        branchSums = defaultdict(list)
        branchClassSums = defaultdict(list)
        for v in branchSKID:
            branchSkids[v].append(1)
        for k, v in branchSkids.items():
            branchSums[k].append(sum(v))
        for k, v in branchSums.items():
            for item in mySet:
                if k == item.skeletonID:
                    branchNames[item.classification].append(v)
        for k, v in branchNames.items():
            total = 0
            for n in v:
                total = total + n[0]
            branchClassSums[k].append(total)

        if 'default_factory' in branchClassSums.keys():
            branchClassSums.pop('default_factory')

        trace = go.Pie(labels = list(branchClassSums.keys()), values = list(branchClassSums.values()))
        fig.append_trace(trace, row, column)
        row = row + 1'''
    '''data = [atrace, ltrace, mtrace, strace, dtrace]

    aAnn = dict(font=dict(size=20),
            showarrow=False,
            text='Anterior',
            # Specify text position (place text in a hole of pie)

            )
    lAnn = dict(font=dict(size=20),
                showarrow=False,
                text='Lateral',
                # Specify text position (place text in a hole of pie)

                )
    mAnn = dict(font=dict(size=20),
                showarrow=False,
                text='Medial',
                # Specify text position (place text in a hole of pie)

                )
    sAnn = dict(font=dict(size=20),
                showarrow=False,
                text='Soma Tract',
                # Specify text position (place text in a hole of pie)

                )
    dAnn = dict(font=dict(size=20),
                showarrow=False,
                text='Descending Tract',
                )

    layout = go.Layout(title='Branch Inputs',
                       annotations=[aAnn, lAnn, mAnn, dAnn, sAnn])
    fig = go.Figure(data=data, layout=layout)'''
    py.plot([atrace], filename='Pie Charts/Branch Inputs/Anterior Class Inputs')
    py.plot([ltrace], filename='Pie Charts/Branch Inputs/Lateral Class Inputs')
    py.plot([mtrace], filename='Pie Charts/Branch Inputs/Medial Inputs')
    py.plot([strace], filename='Pie Charts/Branch Inputs/Soma Tract Inputs')
    py.plot([dtrace], filename='Pie Charts/Branch Inputs/Descending Tract Inputs')
    return

#pie chart based off morphology and input branch - ipsilateral, contra, ect.
def makeBranchMorphologyPie(mySet, branch):
    branchInputs = []
    for neuron in mySet:
        if "Input to GF1 " + branch in neuron.annotations:
            branchInputs.append(neuron)
    BiIpsiProject = []
    BiIpsiLocal = []
    BiMidLocal = []
    BiMidProject = []
    BiContraProject = []
    UniProject = []
    UniLocal = []
    BiIpsiProjectCount = 0
    BiIpsiLocalCount = 0
    BiMidLocalCount = 0
    BiMidProjectCount = 0
    BiContraProjectCount = 0
    UniProjectCount = 0
    UniLocalCount = 0
    Fragments = []
    FragmentsCount = 0
    for neuron in branchInputs:
        if "Unclassified GF input neuron - Fragment" in neuron.annotations:
            Fragments.append(neuron)
            FragmentsCount = FragmentsCount + 1
        elif "Bilateral" in neuron.annotations:
            if "Ipsilateral" in neuron.annotations:
                if "projection neuron" in neuron.annotations:
                    BiIpsiProject.append(neuron)
                    BiIpsiProjectCount = BiIpsiProjectCount + 1
                elif "local neuron" in neuron.annotations:
                    BiIpsiLocal.append(neuron)
                    BiIpsiLocalCount = BiIpsiLocalCount + 1
            elif "contralateral" in neuron.annotations:
                if "projection neuron" in neuron.annotations:
                    BiContraProject.append(neuron)
                    BiContraProjectCount = BiContraProjectCount + 1
            elif "midLine" in neuron.annotations:
                if "projection neuron" in neuron.annotations:
                    BiMidProject.append(neuron)
                    BiMidProjectCount = BiMidProjectCount + 1
                elif "local neuron" in neuron.annotations:
                    BiMidLocal.append(neuron)
                    BiMidLocalCount = BiMidLocalCount + 1
        elif "Unilateral" in neuron.annotations:
            if "projection neuron" in neuron.annotations:
                UniProject.append(neuron)
                UniProjectCount = UniProjectCount + 1
            elif "local neuron" in neuron.annotations:
                UniLocal.append(neuron)
                UniLocalCount = UniLocalCount + 1

    labels = []
    values = []
    sum = 0
    counts = []
    counts.append(BiIpsiProjectCount)
    counts.append(BiMidProjectCount)
    counts.append(BiContraProjectCount)
    counts.append(UniProjectCount)
    counts.append(UniLocalCount)
    counts.append(FragmentsCount)
    labels.append("Bilateral Ipsilateral Projection")
    for neuron in BiIpsiProject:
        sum = sum + neuron.GF1synapseCount
    values.append(sum)
    #sum = 0
    #labels.append("Heterolateral Ipsilateral Local")
    #for neuron in HeteroIpsiLocal:
    #    sum = sum + neuron.GF1synapseCount
    #values.append(sum)
    sum = 0
    labels.append("Bilateral MidLine Projection")
    for neuron in BiMidProject:
        sum = sum + neuron.GF1synapseCount
    values.append(sum)
    #sum = 0
    #labels.append("Heterolateral MidLine Local")
    #for neuron in HeteroMidLocal:
    #    sum = sum + neuron.GF1synapseCount
    #values.append(sum)
    sum = 0
    labels.append("Bilateral Contralateral Projection")
    for neuron in BiContraProject:
        sum = sum + neuron.GF1synapseCount
    values.append(sum)
    sum = 0
    labels.append("Unilateral Ipsilateral Projection")
    for neuron in UniProject:
        sum = sum + neuron.GF1synapseCount
    values.append(sum)
    sum = 0
    labels.append("Unilateral Ipsilateral Local")
    for neuron in UniLocal:
        sum = sum + neuron.GF1synapseCount
    values.append(sum)
    sum = 0
    labels.append("Fragment")
    for neuron in Fragments:
        sum = sum + neuron.GF1synapseCount
    values.append(sum)
    # trace = go.Pie(labels=labels, values=values, textinfo='label+value')
    # layout = go.Layout(title=branch)
    # fig = go.Figure(data = trace, layout = layout)
    fig = {
        'data': [{'marker': {'colors': ['rgb(204, 0, 0)',
                                        'rgb(0, 204, 0)',
                                        'rgb(0, 0, 204)',
                                        'rgb(255, 128, 0)',
                                        'rgb(255, 255, 51)',
                                        'rgb(204, 153, 255)']},
                  'type': 'pie', 'labels': labels,
                  'values': values,
                  'text': counts, 'textinfo':'label+value+text'}],
        'layout': {'title': branch}}
    py.plot(fig, filename='Pie Charts/Morphology/by Synapse/' + branch)
     #               'values': counts,
     #               'text': values, 'textinfo': 'label+text+value'}],
     #   'layout': {'title': branch}}
    #py.plot(fig, filename='Pie Charts/Morphology/by Neuron/' + branch)
    return

#makes a bar chart of highest synapse count to lowest
def gfSynapseBars(mySet, filename = 'Figures/General/Synapse Count Bars'):
    mySet = CS.sortBySynH2L(mySet)
    GFSYN = []
    neuronNames = []
    for neuron in mySet:
        GFSYN.append(neuron.GF1synapseCount)
        neuronNames.append(neuron.neuronName)

    trace1 = go.Bar(
        y=GFSYN,
    )
    data = [trace1]
    layout = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        title="Individual Neuron Synapse Count"
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return

# histogram of all inputs to GF
def gfSynapseBarsSoma(mySet, filename = 'Figures/General/Soma Location Synapse Count Bars'):
    mySet = CS.sortBySynH2L(mySet)
    GFSYN = []
    neuronNames = []
    purple = colour.Color("purple").hex
    orange = colour.Color("orange").hex
    cyan = colour.Color("cyan").hex
    black = colour.Color("black").hex
    colors = []
    for neuron in mySet:
        GFSYN.append(neuron.GF1synapseCount)
        neuronNames.append(neuron.neuronName)
        if "contralateral" in neuron.annotations:
            neuron.curColor = purple
        elif "Ipsilateral" in neuron.annotations:
            neuron.curColor = orange
        elif "midLine" in neuron.annotations:
            neuron.curColor = cyan
        else:
            neuron.curColor = black
        colors.append(neuron.curColor)

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
        title="Individual Neuron Synapse Count"
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return


#creates a histograpm of the top input types
def gfSynapseHistogramColoredTop(mySet):
    mySet = CS.sortBySynH2L(mySet)
    GFSYN = []
    neuronNames = []
    colors = []
    mySetCopy = shortenClassNames(mySet)
    for neuron in mySetCopy:
        if neuron.GF1synapseCount > 172:
            if neuron.classification == "type 25":
                colors.append('rgb(255,0,51)')
            elif neuron.classification == "type 10":
                colors.append('rgb(255,153,0)')
            elif neuron.classification == "type 3":
                colors.append('rgb(0,204,102)')
            elif neuron.classification == "type 8":
                colors.append('rgb(255,204,0)')
            elif neuron.classification == "type 66b":
                colors.append('rgb(0,153,204)')
            else:
                colors.append('rgb(64,64,64)')
        else:
            colors.append('rgb(64,64,64)')
        GFSYN.append(neuron.GF1synapseCount)
        neuronNames.append(neuron.neuronName)
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
        title="Synapse Count"
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Figures/General/Synapse Count Histogram with Top Colors')
    return

#creates three bar charts on one page of high, med, and low input counts
def splitBarChart(mySet):
    mySet = CS.sortBySynH2L(mySet)

    lowInputs = []
    medInputs = []
    highInputs = []
    mySetCopy = shortenClassNames(mySet)
    for neuron in mySetCopy:
        if neuron.GF1synapseCount < 11:
            lowInputs.append(neuron)
        elif 10 < neuron.GF1synapseCount < 75:
            medInputs.append(neuron)
        elif neuron.GF1synapseCount > 74:
            highInputs.append(neuron)

    lowKeys = []
    medKeys = []
    highKeys = []
    lowVals = []
    medVals = []
    highVals = []

    for neuron in lowInputs:
        lowKeys.append(neuron.neuronName)
        lowVals.append(neuron.GF1synapseCount)
    for neuron in medInputs:
        medKeys.append(neuron.neuronName)
        medVals.append(neuron.GF1synapseCount)
    for neuron in highInputs:
        highKeys.append(neuron.neuronName)
        highVals.append(neuron.GF1synapseCount)
    trace1 = go.Bar(
        # x=lowKeys,
        y=lowVals,
        text=lowVals,
        textposition='auto'
    )
    trace2 = go.Bar(
        # x=medKeys,
        y=medVals,
        text=medVals,
        textposition='auto'
    )
    trace3 = go.Bar(
        #x=highKeys,
        y=highVals,
        text=highVals,
        textposition='auto'
    )
    titles = ['10 synapses and under, sum = ' + str(len(lowVals)),
              '11 to 74 synapses, sum = ' + str(len(medVals)),
              '75+ synapses, sum = ' + str(len(highVals))]
    fig = tools.make_subplots(rows=3, cols=1, subplot_titles=titles)
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 2, 1)
    fig.append_trace(trace3, 3, 1)

    py.plot(fig, filename='Figures/General/Split Synapse Counts')
    return


#creates gradients of high, med, and low synapse counts
def makeSeparateBarGradients(mySet, filename1='Figures/Gradients/1 - 20 synapses',
                             filename2='Figures/Gradients/21 - 49 synapses',
                             filename3='Figures/Gradients/50+ synapses'):
    mySet = CS.sortBySynH2L(mySet)
    lowInputs = []
    medInputs = []
    highInputs = []
    mySetCopy = shortenClassNames(mySet)
    for neuron in mySetCopy:
        if neuron.GF1synapseCount < 21:
            lowInputs.append(neuron)
        elif 20 < neuron.GF1synapseCount < 51:
            medInputs.append(neuron)
        elif neuron.GF1synapseCount > 50:
            highInputs.append(neuron)

    lowKeys = []
    medKeys = []
    highKeys = []
    lowVals = []
    medVals = []
    highVals = []

    for neuron in lowInputs:
        lowKeys.append(neuron.neuronName)
        lowVals.append(neuron.GF1synapseCount)
    for neuron in medInputs:
        medKeys.append(neuron.neuronName)
        medVals.append(neuron.GF1synapseCount)
    for neuron in highInputs:
        highKeys.append(neuron.neuronName)
        highVals.append(neuron.GF1synapseCount)

    red = colour.Color("red")
    blue = colour.Color("blue")
    allColors1 = list(red.range_to(blue, len(lowVals)))
    allColors2 = list(red.range_to(blue, len(medVals)))
    allColors3 = list(red.range_to(blue, len(highVals)))
    allColors1 = [str(i) for i in allColors1]
    allColors2 = [str(i) for i in allColors2]
    allColors3 = [str(i) for i in allColors3]
    trace1 = go.Bar(
        #x=lowKeys,
        y=lowVals,
        text=lowVals,
        marker=dict(color=allColors1),
        textposition='auto'
    )
    trace2 = go.Bar(
        #x=medKeys,
        y=medVals,
        text=medVals,
        marker=dict(color=allColors2),
        textposition='auto'
    )
    trace3 = go.Bar(
        x=highKeys,
        y=highVals,
        text=highVals,
        marker=dict(color=allColors3),
        textposition='auto'
    )
    layout = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=250
        ),
        title="Synapse Count, 1 to 20"
    )
    layout2 = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=250
        ),
        title="Synapse Count, 21 to 50"
    )
    layout3 = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=250
        ),
        title="Synapse Count, 50+"
    )

    fig1 = go.Figure(data=[trace1], layout=layout)
    fig2 = go.Figure(data=[trace2], layout=layout2)
    fig3 = go.Figure(data=[trace3], layout=layout3)
    py.plot(fig1, filename=filename1)
    py.plot(fig2, filename=filename2)
    py.plot(fig3, filename=filename3)
    return

#same as above but with soma coloration
def makeSeparateBarSoma(mySet, filename1='Figures/Gradients/Soma, 1 - 20 synapses',
                             filename2='Figures/Gradients/Soma, 21 - 49 synapses',
                             filename3='Figures/Gradients/Soma, 50+ synapses'):
    mySet = CS.sortBySynH2L(mySet)
    lowInputs = []
    medInputs = []
    highInputs = []
    purple = colour.Color("purple").hex
    orange = colour.Color("orange").hex
    cyan = colour.Color("cyan").hex
    black = colour.Color("black").hex
    mySetCopy = mySetCopy = shortenClassNames(mySet)
    for neuron in mySetCopy:
        if "contralateral" in neuron.annotations:
            neuron.curColor = purple
        elif "Ipsilateral" in neuron.annotations:
            neuron.curColor = orange
        elif "midLine" in neuron.annotations:
            neuron.curColor = cyan
        else:
            neuron.curColor = black
        if neuron.GF1synapseCount < 21:
            lowInputs.append(neuron)
        elif 20 < neuron.GF1synapseCount < 51:
            medInputs.append(neuron)
        elif neuron.GF1synapseCount > 50:
            highInputs.append(neuron)

    lowKeys = []
    medKeys = []
    highKeys = []
    lowVals = []
    medVals = []
    highVals = []
    lowc = []
    medc = []
    highc = []

    for neuron in lowInputs:
        lowKeys.append(neuron.neuronName)
        lowVals.append(neuron.GF1synapseCount)
        lowc.append(neuron.curColor)
    for neuron in medInputs:
        medKeys.append(neuron.neuronName)
        medVals.append(neuron.GF1synapseCount)
        medc.append(neuron.curColor)
    for neuron in highInputs:
        highKeys.append(neuron.neuronName)
        highVals.append(neuron.GF1synapseCount)
        highc.append(neuron.curColor)

    trace1 = go.Bar(
        #x=lowKeys,
        y=lowVals,
        text=lowVals,
        marker=dict(color=lowc),
        textposition='auto'
    )
    trace2 = go.Bar(
        #x=medKeys,
        y=medVals,
        text=medVals,
        marker=dict(color=medc),
        textposition='auto'
    )
    trace3 = go.Bar(
        x=highKeys,
        y=highVals,
        text=highVals,
        marker=dict(color=highc),
        textposition='auto'
    )
    layout = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=250
        ),
        title="Synapse Count, 1 to 20"
    )
    layout2 = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=250
        ),
        title="Synapse Count, 21 to 50"
    )
    layout3 = go.Layout(
        bargap=0.2,
        margin=go.layout.Margin(
            b=300,
            r=250
        ),
        title="Synapse Count, 50+"
    )

    fig1 = go.Figure(data=[trace1], layout=layout)
    fig2 = go.Figure(data=[trace2], layout=layout2)
    fig3 = go.Figure(data=[trace3], layout=layout3)
    py.plot(fig1, filename=filename1)
    py.plot(fig2, filename=filename2)
    py.plot(fig3, filename=filename3)
    return


#creates a histogram by synapse count - how many neurons have each synapse count
def histogramBySynCount(mySet, filename='Figures/General/Histogram By Synapse Count'):
    mySetCopy = shortenClassNames(mySet)
    synCounts = defaultdict(list)
    for neuron in mySet:
        synCounts[neuron.GF1synapseCount].append(neuron)
    values = []
    for k, v in synCounts.items():
        sum = 0
        for neuron in v:
            sum = sum + 1
        values.append(sum)
    keys = list(synCounts.keys())
    trace = go.Bar(
        x=keys,
        y=values,
        name = "Synapse Counts",
        text=values,
        textposition='outside'
    )
    layout = go.Layout(
        title="Synapse Count",
        yaxis=dict(title='Neuron Count'),
        xaxis=dict(title='Synapse Count'),
        bargap=0.2
    )
    fig = go.Figure(data=[trace], layout=layout)
    py.plot(fig, filename=filename)
    return

#histogram by type
def gfClassHistogram(mySet, filename='Figures/General/Class Synapse Count Histogram'):
    mySet = CS.sortBySynH2L(mySet)
    classes = []
    GF1Syn = []
    mySetCopy = shortenClassNames(mySet)

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


# Binned classes of synapses onto GF
def createBinsbyType(mySet):
    lowKeys = []
    lowValues = []
    medKeys = []
    medValues = []
    highKeys = []
    highValues = []
    lowDict = defaultdict(list)
    medDict = defaultdict(list)
    highDict = defaultdict(list)
    mySetCopy = shortenClassNames(mySet)

    for i in mySetCopy:
        key = i.classification
        synCount = i.GF1synapseCount
        if synCount < 11:
            lowDict[key].append(i.GF1synapseCount)
        if synCount > 11 and synCount < 71:
            medDict[key].append(i.GF1synapseCount)
        if synCount > 70:
            highDict[key].append(i.GF1synapseCount)

    lowKeys = list(lowDict.keys())
    medKeys = list(medDict.keys())
    highKeys = list(highDict.keys())
    for i in lowDict.values():
        count = 0
        for nums in i:
            count = count + nums
        lowValues.append(count)

    for i in medDict.values():
        count = 0
        for nums in i:
            count = count + nums
        medValues.append(count)

    for i in highDict.values():
        count = 0
        for nums in i:
            count = count + nums
        highValues.append(count)

    lowTrace = go.Bar(
        x=lowKeys,
        y=lowValues,
        marker=dict(color="rgb(0,0,225)"),
        name="Low Input (1-10)"
    )
    medTrace = go.Bar(
        x=medKeys,
        y=medValues,
        marker=dict(color="rgb(0,204,0)"),
        name="Med Input (11-70)"
    )
    highTrace = go.Bar(
        x=highKeys,
        y=highValues,
        marker=dict(color="rgb(255,51,51)"),
        name="High Input (70+)"
    )
    data = [lowTrace, medTrace, highTrace]
    layout = go.Layout(
        barmode='group',
        margin=go.layout.Margin(
            b=200,
            r=150
        ),
        xaxis=dict(tickangle=45)
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Figures/General/Synapse Bins by Type')
    return


# creates bins for high, med, low input neurons
# bins for each type
def fourNeuronsBinned(mySet):
    mySetCopy = shortenClassNames(mySet)
    dataDict = defaultdict(list)
    for i in mySetCopy:
        dataDict[i.classification].append(i.GF1synapseCount)
    overData = defaultdict(list)

    for k, v in dataDict.items():
        if len(v) > 3:
            overData[k].append(v)
    overKeys = list(overData.keys())

    lowOver = defaultdict(list)
    medOver = defaultdict(list)
    highOver = defaultdict(list)

    for k, v in overData.items():
        for item in v:
            for val in item:
                if val < 10:
                    lowOver[k].append(val)
                if 9 < val < 71:
                    medOver[k].append(val)
                if val > 70:
                    highOver[k].append(val)

    lowOverSum = []
    medOverSum = []
    highOverSum = []
    lowOverCount = defaultdict(list)
    medOverCount = defaultdict(list)
    highOverCount = defaultdict(list)
    for i in lowOver.values():
        count = 0
        for nums in i:
            count = count + nums
        lowOverSum.append(count)
    for i in medOver.values():
        count = 0
        for nums in i:
            count = count + nums
        medOverSum.append(count)
    for i in highOver.values():
        count = 0
        for nums in i:
            count = count + nums
        highOverSum.append(count)

    for k, v in lowOver.items():
        lowOverCount[k].append(len(v))
    for k, v in medOver.items():
        medOverCount[k].append(len(v))
    for k, v in highOver.items():
        highOverCount[k].append(len(v))

    medOverCountList = []
    for i in medOverCount.values():
        medOverCountList.append(i[0])

    lowOverCountList = []
    for i in lowOverCount.values():
        lowOverCountList.append(i[0])

    highOverCountList = []
    for i in highOverCount.values():
        highOverCountList.append(i[0])
    lowOverKeys = list(lowOver.keys())
    medOverKeys = list(medOver.keys())
    highOverKeys = list(highOver.keys())
    lowOverTrace = go.Bar(
        x=lowOverKeys,
        y=lowOverSum,
        marker=dict(color="rgb(0,0,225)"),
        text=lowOverCountList,
        name="Low Input (1-9)"
    )
    medOverTrace = go.Bar(
        x=medOverKeys,
        y=medOverSum,
        marker=dict(color="rgb(0,204,0)"),
        text=medOverCountList,
        name="Med Input (10-70)"
    )
    highOverTrace = go.Bar(
        x=highOverKeys,
        y=highOverSum,
        marker=dict(color="rgb(255,51,51)"),
        text=highOverCountList,
        name="High Input (70+)"
    )
    layout = go.Layout(
        barmode='group',
        margin=go.layout.Margin(
            b=200,
            r=150
        ),
        xaxis=dict(tickangle=45)
    )
    data = [lowOverTrace, medOverTrace, highOverTrace]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Figures/General/4+ Synapse Sums Binned')

    return

# creates grid of synapse comparisons of 2 and 3 neuron groups
def pairTripletSynapseCompare(mySet, filename='Figures/Synapse Compare/Less Than Four'):
    mySet = CS.sortBySynL2H(mySet)
    mySetCopy = shortenClassNames(mySet)

    dataDict = createDataDict(mySetCopy)
    lessThanFour = defaultdict(list)
    orderedFour = defaultdict(list)
    for v in dataDict.values():
        if 1 < len(v) < 4:
            lessThanFour[v[0].classification].append(v)

    for k, v in lessThanFour.items():
        for neuron in v:
            yellow = colour.Color("yellow")
            purple = colour.Color("purple")
            orange = colour.Color("orange")
            curColor = 0
            synList = []
            colors = []
            for item in neuron:
                if "RIGHT HEMISPHERE" in item.annotations:
                    item.curColor = "purple"
                elif "LEFT HEMISPHERE" in item.annotations:
                    item.curColor = "orange"
                elif "RIGHT HEMISPHERE" not in item.annotations and "LEFT HEMISPHERE" not in item.annotations:
                    item.curColor = "yellow"

    # Orders by colors
    ##further refine to get large gaps first
    for k, v in lessThanFour.items():
        if len(v[0]) == 2:
            if v[0][0].curColor is not v[0][1].curColor:
                orderedFour[k].append(v[0])
    for k, v in lessThanFour.items():
        if len(v[0]) == 2:
            if v[0][0].curColor is v[0][1].curColor:
                orderedFour[k].append(v[0])

    for k, v in lessThanFour.items():
        if len(v[0]) == 3:
            neuron1 = v[0][0]
            neuron2 = v[0][1]
            neuron3 = v[0][2]
            if neuron1.curColor is not neuron2.curColor:
                orderedFour[k].append(v[0])
    for k, v in lessThanFour.items():
        if len(v[0]) == 3:
            neuron1 = v[0][0]
            neuron2 = v[0][1]
            neuron3 = v[0][2]
            if k not in orderedFour.keys():
                orderedFour[k].append(v[0])

    for k, v in orderedFour.items():
        if len(v[0]) == 2:
            val1 = v[0][0].GF1synapseCount
            val2 = v[0][1].GF1synapseCount
            if val1 > val2:
                v[0][0].curColor = 'red'
                v[0][1].curColor = 'blue'
            if val2 > val1:
                v[0][1].curColor = 'red'
                v[0][0].curColor = 'blue'
                # orderedFour[k] = v[0][1], v[0][0]
            if val1 == val2:
                v[0][0].curColor = 'blue'
                v[0][1].curColor = 'red'

    for k, v in orderedFour.items():
        if len(v[0]) == 3:
            v1 = v[0][0].GF1synapseCount
            v2 = v[0][1].GF1synapseCount
            v3 = v[0][2].GF1synapseCount
            if v1 > v2 and v1 > v3:
                v[0][0].curColor = 'red'
                if v2 > v3:
                    v[0][1].curColor = 'green'
                    v[0][2].curColor = 'blue'
                else:
                    v[0][2].curColor = 'green'
                    v[0][1].curColor = 'blue'
            elif v2 > v1 and v2 > v3:
                v[0][1].curColor = 'red'
                if v1 > v3:
                    v[0][0].curColor = 'green'
                    v[0][2].curColor = 'blue'
                else:
                    v[0][2].curColor = 'green'
                    v[0][0].curColor = 'blue'
            elif v3 > v2 and v3 > v1:
                v[0][2].curColor = 'red'
                if v2 > v1:
                    v[0][1].curColor = 'green'
                    v[0][0].curColor = 'blue'
                else:
                    v[0][0].curColor = 'blue'
                    v[0][1].curColor = 'green'
            elif v1 == v2:
                if v3 > v1:
                    v[0][2].curColor = 'red'
                    v[0][1].curColor = 'green'
                    v[0][0].curColor = 'blue'
                if v1 > v3:
                    v[0][0].curColor = 'red'
                    v[0][1].curColor = 'green'
                    v[0][2].curColor = 'blue'
            elif v1 == v3:
                if v2 > v1:
                    v[0][1].curColor = 'red'
                    v[0][2].curColor = 'green'
                    v[0][0].curColor = 'blue'
                if v1 > v2:
                    v[0][0].curColor = 'red'
                    v[0][2].curColor = 'green'
                    v[0][1].curColor = 'blue'
            elif v3 == v2:
                if v1 > v2:
                    v[0][0].curColor = 'red'
                    v[0][1].curColor = 'green'
                    v[0][2].curColor = 'blue'
                if v2 > v1:
                    v[0][1].curColor = 'green'
                    v[0][2].curColor = 'red'
                    v[0][0].curColor = 'blue'

    keys = list(orderedFour.keys())
    fig = tools.make_subplots(rows=10, cols=5, subplot_titles=keys)
    column = 1
    row = 1
    for k, v in orderedFour.items():
        for neuron in v:
            synList = []
            colors = []
            for item in neuron:
                synList.append(item.GF1synapseCount)
                colors.append(item.curColor)
        Trace = go.Bar(
            y=synList,
            marker=dict(color=colors),
            name=item.classification
        )
        fig.append_trace(Trace, row, column)
        column = column + 1
        if column > 5:
            row = row + 1
            column = 1

    py.plot(fig, filename=filename)

# creates grid of plots comparing GF input types with 4 or more neurons
def fourNeuronSynapseComparePlot(mySet, filename='Figures/Synapse Compare/More Than Four'):
    mySet = CS.sortBySynL2H(mySet)
    mySetCopy = shortenClassNames(mySet)

    dataDict = createDataDict(mySetCopy)
    moreThanFour = defaultdict(list)
    for v in dataDict.values():
        if len(v) > 3:
            moreThanFour[v[0].classification].append(v)

    GF1Syns = []
    data = []
    row = 1
    column = 1
    keys = list(moreThanFour.keys())
    fig = tools.make_subplots(rows=9, cols=5, subplot_titles=keys)
    for k, v in moreThanFour.items():
        for neuron in v:
            red = colour.Color("red")
            blue = colour.Color("blue")
            green = colour.Color("green")
            allColors = list(blue.range_to(red, len(neuron)))
            # print(allColors)
            curColor = 0
            synList = []
            colors = []
            for item in neuron:
                GF1Syns.append(item.GF1synapseCount)
                synList.append(item.GF1synapseCount)
                item.curColor = allColors[curColor].hex
                colors.append(item.curColor)
                curColor += 1
            Trace = go.Bar(
                y=synList,
                marker=dict(color=colors),
                name=item.classification
            )
            fig.append_trace(Trace, row, column)
            column = column + 1
            if column > 5:
                row = row + 1
                column = 1
    py.plot(fig, filename=filename)
    return





def splitFourSynapseCompare(mySet, filename='Tests/More Than Four'):
    mySetCopy = deepcopy(mySet)
    mySetCopy = CS.GFIN_set(mySetCopy)
    dataDict = createDataDict(mySetCopy)
    moreThanFour = defaultdict(list)
    for v in dataDict.values():
        if len(v) > 3:
            moreThanFour[v[0].classification].append(v)

    classifs = list(moreThanFour.keys())
    mySetCI = []
    for neuron in mySetCopy:
        if neuron.classification in classifs:
            mySetCI.append(neuron)
    mySetCI = CS.GFIN_set(mySetCI)
    mySetCI = shortenClassNames(mySetCI)
    for neuron in mySetCI:
        if "contralateral" in neuron.annotations:
            neuron.neuronName = str(neuron.neuronName) + " - contralateral"
            neuron.classification = str(neuron.classification) + " - Contralateral"
        elif "Ipsilateral" in neuron.annotations:
            neuron.neuronName = str(neuron.neuronName) + " - Ipsilateral"
            neuron.classification = str(neuron.classification) + " - Ipsilateral"
        elif "midLine" in neuron.annotations:
            neuron.neuronName = str(neuron.neuronName) + " - Midline"
            neuron.classification = str(neuron.classification) + " - Midline"
    mySetCI = CS.sortBySynL2H(mySetCI)
    splitMoreThanFour = defaultdict(list)
    for neuron in mySetCI:
        splitMoreThanFour[neuron.classification].append(neuron)

    splitMoreThanFour = OrderedDict(sorted(splitMoreThanFour.items(), key=lambda item: item[0]))
    GF1Syns = []
    data = []
    row = 1
    column = 1
    keys = list(splitMoreThanFour.keys())
    fig = tools.make_subplots(rows=12, cols=5, subplot_titles=keys)
    red = colour.Color("red")
    blue = colour.Color("blue")
    for k, v in splitMoreThanFour.items():
        curColor = 0
        synList = []
        colors = []
        for item in v:
            allColors = list(blue.range_to(red, len(v)))
            GF1Syns.append(item.GF1synapseCount)
            synList.append(item.GF1synapseCount)
            item.curColor = allColors[curColor].hex
            colors.append(item.curColor)
            curColor += 1
        Trace = go.Bar(
            y=synList,
            marker=dict(color=colors),
            name=item.classification
            )
        fig.append_trace(Trace, row, column)
        column = column + 1
        if column > 5:
            row = row + 1
            column = 1
    py.plot(fig, filename="Test/ContrIpsi")
    return


# creates same grid as above
# colors bars based on contra/ipsi/neither
def fourNeuronContraIpsi(mySet):
    mySet = CS.sortBySynL2H(mySet)
    mySetCopy = shortenClassNames(mySet)

    dataDict = createDataDict(mySetCopy)
    moreThanFour = defaultdict(list)

    for v in dataDict.values():
        if len(v) > 3:
            moreThanFour[v[0].classification].append(v)

    data = []
    row = 1
    column = 1
    keys = list(moreThanFour.keys())
    fig = tools.make_subplots(rows=9, cols=5, subplot_titles=keys)
    for k, v in moreThanFour.items():
        for neuron in v:
            yellow = colour.Color("yellow")
            purple = colour.Color("purple")
            orange = colour.Color("orange")
            curColor = 0
            synList = []
            colors = []
            for item in neuron:
                synList.append(item.GF1synapseCount)
                if "RIGHT HEMISPHERE" in item.annotations:
                    item.curColor = "purple"
                elif "LEFT HEMISPHERE" in item.annotations:
                    item.curColor = "orange"
                elif "RIGHT HEMISPHERE" not in item.annotations and "LEFT HEMISPHERE" not in item.annotations:
                    item.curColor = "yellow"
                colors.append(item.curColor)
                curColor += 1
            Trace = go.Bar(
                y=synList,
                marker=dict(color=colors),
                name=item.classification
            )
            fig.append_trace(Trace, row, column)
            column = column + 1
            if column > 5:
                row = row + 1
                column = 1
    py.plot(fig, filename='Figures/Contra_Ipsi/More Than Four')
    return

# creates a grid of paired/triplet types
# colored based on contra/ipsi/neither
def pairTripletContraIpsi(mySet):
    mySet = CS.sortBySynL2H(mySet)
    mySetCopy = shortenClassNames(mySet)

    dataDict = createDataDict(mySetCopy)
    lessThanFour = defaultdict(list)
    orderedFour = defaultdict(list)
    for v in dataDict.values():
        if 1 < len(v) < 4:
            lessThanFour[v[0].classification].append(v)

    for k, v in lessThanFour.items():
        for neuron in v:
            yellow = colour.Color("yellow")
            purple = colour.Color("purple")
            orange = colour.Color("orange")
            curColor = 0
            synList = []
            colors = []
            for item in neuron:
                if "RIGHT HEMISPHERE" in item.annotations:
                    item.curColor = "purple"
                elif "LEFT HEMISPHERE" in item.annotations:
                    item.curColor = "orange"
                elif "RIGHT HEMISPHERE" not in item.annotations and "LEFT HEMISPHERE" not in item.annotations:
                    item.curColor = "yellow"

    # Orders by colors
    ##further refine to get large gaps first
    for k, v in lessThanFour.items():
        if len(v[0]) == 2:
            if v[0][0].curColor is not v[0][1].curColor:
                orderedFour[k].append(v[0])
    for k, v in lessThanFour.items():
        if len(v[0]) == 2:
            if v[0][0].curColor is v[0][1].curColor:
                orderedFour[k].append(v[0])

    for k, v in lessThanFour.items():
        if len(v[0]) == 3:
            neuron1 = v[0][0]
            neuron2 = v[0][1]
            neuron3 = v[0][2]
            if neuron1.curColor is not neuron2.curColor:
                orderedFour[k].append(v[0])
    for k, v in lessThanFour.items():
        if len(v[0]) == 3:
            neuron1 = v[0][0]
            neuron2 = v[0][1]
            neuron3 = v[0][2]
            if k not in orderedFour.keys():
                orderedFour[k].append(v[0])
    keys = list(orderedFour.keys())
    fig = tools.make_subplots(rows=10, cols=5, subplot_titles=keys)
    column = 1
    row = 1
    for k, v in orderedFour.items():
        for neuron in v:
            synList = []
            colors = []
            for item in neuron:
                synList.append(item.GF1synapseCount)
                colors.append(item.curColor)
        Trace = go.Bar(
            y=synList,
            marker=dict(color=colors),
            name=item.classification
        )
        fig.append_trace(Trace, row, column)
        column = column + 1
        if column > 5:
            row = row + 1
            column = 1

    py.plot(fig, filename='Figures/Contra_Ipsi/Less Than Four')
    return


# in progress - color by distribution
# grid of plots
def colorFourByDistrib(mySet):
    mySet = CS.sortBySynL2H(mySet)
    mySetCopy = shortenClassNames(mySet)

    dataDict = createDataDict(mySetCopy)
    moreThanFour = defaultdict(list)

    for v in dataDict.values():
        if len(v) > 3:
            moreThanFour[v[0].classification].append(v)

    data = []
    row = 1
    column = 1
    keys = list(moreThanFour.keys())
    fig = tools.make_subplots(rows=9, cols=5, subplot_titles=keys)
    for k, v in moreThanFour.items():
        for neuron in v:
            synList = []
            colors = []
            for item in neuron:
                synList.append(item.GF1synapseCount)
                if item.distribution is "Anterior":
                    item.curColor = 'rgb(220,20,60)'
                elif item.distribution is "AnteriorDescending":
                    item.curColor = "rgb(0,100,0)"
                elif item.distribution is "AnteriorLateral":
                    item.curColor = "rgb(0,255,255)"
                elif item.distribution is "AnteriorLateralSoma":
                    item.curColor = "rgb(255,0,255)"
                elif item.distribution is "AnteriorMedial":
                    item.curColor = "rgb(107,142,35)"
                elif item.distribution is "AnteriorMedialLateral":
                    item.curColor = "rgb(0,255,0)"
                elif item.distribution is "AnteriorMedialLateralSoma":
                    item.curColor = "rgb(0,0,255)"
                elif item.distribution is "AnteriorMedialSoma":
                    item.curColor = "rgb(139,69,19)"
                elif item.distribution is "Descending":
                    item.curColor = "rgb(70,130,180)"
                elif item.distribution is "Lateral":
                    item.curColor = "rgb(255,165,0)"
                elif item.distribution is "LateralSoma":
                    item.curColor = "rgb(147,112,219)"
                elif item.distribution is "Medial":
                    item.curColor = "rgb(255,255,0)"
                elif item.distribution is "MedialDescending":
                    item.curColor = "rgb(218,165,32)"
                elif item.distribution is "MedialLateral":
                    item.curColor = "rgb(105,105,105)"
                elif item.distribution is "MedialLateralSoma":
                    item.curColor = "rgb(128,0,128)"
                elif item.distribution is "MedialSoma":
                    item.curColor = "rgb(250,128,114)"
                elif item.distribution is "Soma":
                    item.curColor = "rgb(0,0,0)"

                colors.append(item.curColor)
            Trace = go.Bar(
                y=synList,
                marker=dict(color=colors),
                name=item.classification
            )
            fig.append_trace(Trace, row, column)
            column = column + 1
            if column > 5:
                row = row + 1
                column = 1
    py.plot(fig, filename='Tests/TestDistrib')
    return


# creates plot of 10 top inputting types
def createTopInputtingPlot(mySet, filename='Figures/General/Top 10 Types'):
    mySetCopy = shortenClassNames(mySet)
    summedDict = synapseDict(mySetCopy)
    summedDict.pop("putative LC4 neuron")
    summedDict.pop("JONeuron")
    summedDict.pop("LPLC2")

    top10 = {k: summedDict[k] for k in list(summedDict)[:10]}
    colors = ['rgb(255,0,51)', 'rgb(255,153,0)', 'rgb(255,204,0)',
              'rgb(255,255,0)', 'rgb(153,255,0)', 'rgb(0,204,102)',
              'rgb(0,255,255)', 'rgb(0,153,204)', 'rgb(0,0,255)',
              'rgb(102,0,204)']
    keys = list(top10.keys())
    values = list(top10.values())
    trace1 = go.Bar(
        x=keys,
        y=values,
        text=values,
        textposition='auto',
        marker=dict(color=list(colors))
    )
    data = [trace1]
    layout = go.Layout(
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        xaxis=dict(tickangle=45),
        title="Top 10 Count"
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return

def createTopInputtingPlotAll(mySet, filename='Figures/General/Top 10 Types_All'):
    mySetCopy = shortenClassNames(mySet)
    summedDict = synapseDict(mySetCopy)


    top10 = {k: summedDict[k] for k in list(summedDict)[:10]}
    colors = ['rgb(255,0,51)', 'rgb(255,153,0)', 'rgb(255,204,0)',
              'rgb(255,255,0)', 'rgb(153,255,0)', 'rgb(0,204,102)',
              'rgb(0,255,255)', 'rgb(0,153,204)', 'rgb(0,0,255)',
              'rgb(102,0,204)']
    keys = list(top10.keys())
    values = list(top10.values())
    trace1 = go.Bar(
        x=keys,
        y=values,
        text=values,
        textposition='auto',
        marker=dict(color=list(colors))
    )
    data = [trace1]
    layout = go.Layout(
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        xaxis=dict(tickangle=45),
        title="Top 10 Count with Visual and JO"
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return


def overHunderedNeurons(mySet, filename='Figures/General/Over 100 Synapses'):
    mySet = CS.sortBySynH2L(mySet)
    mySetCopy = shortenClassNames(mySet)
    neuronName = []
    neurons = []
    syns = []
    for i in mySetCopy:
        if i.GF1synapseCount > 99:
            neuronName.append(i.neuronName)
            neurons.append(i)
            syns.append(i.GF1synapseCount)

    red = colour.Color("red")
    blue = colour.Color("blue")

    allColors = list(red.range_to(blue, len(syns)))
    colors = []
    for col in allColors:
        colors.append(col.hex_l)
    trace1 = go.Bar(
        x=neuronName,
        y=syns,
        text=syns,
        textposition='auto',
        marker=dict(color=list(colors))
    )
    data = [trace1]
    layout = go.Layout(autosize=False,
        margin=go.layout.Margin(
            b=300,
            r=200
        ),
        xaxis=dict(tickangle=45),
        title="Over 100 Synapses"
    )
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)


def makeModalityBars(mySet, filename='Figures/Modality/Neuron Modality'):
    mySetCopy = shortenClassNames(mySet)
    keys = ['VPN', 'Other Visual', 'Visual Interneuron', 'JONeuron',
                  'Mechanosensory Interneuron', 'Non-Visual Interneuron',
                  'Ascending Neuron', 'Descending Neuron']
    modalities = {k:[] for k in keys}
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)
    keys = list(modalities.keys())
    values = []
    for k, v in modalities.items():
        values.append(len(v))
    colors = ['rgb(255,0,0)', 'rgb(255,140,0)', 'rgb(255,255,0)',
                  'rgb(127,255,0)', 'rgb(34,139,34)','rgb(0,255,255)',
                  'rgb(30, 144, 255)', 'rgb(138,43,226)']
    Modalities = go.Bar(
        name='Modalities',
        x = keys,
        y = values,
        text=values,
        textposition='auto',
        marker=dict(color = colors)
    )
    layout = go.Layout(autosize=False,
        showlegend=True,
        margin=dict(b=200),
        title='Modality Bars by Neuron Count',
        xaxis=dict(
            tickfont=dict(size=20),
            range=[-0.5,10]
        ),
        yaxis=dict(title='Neuron Count'),
        legend=dict(
            font=dict(
                size=30
            )
        )
    )
    data = [Modalities]
    fig = go.Figure(data=data,layout=layout)
    py.plot(fig, filename=filename)
    return



def makeStackedModalityByNeuron(mySet, filename='Figures/Modality/Stacked Modalities By Neuron Count'):
    mySetCopy = shortenClassNames(mySet)
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
        MedialModesSummed[k]=(len(v))
    # MedialModesSummed.pop('default_factory')
    DescendingModesSummed = defaultdict(int)
    for k, v in DescendingModes.items():
        DescendingModesSummed[k]=(len(v))
    # DescendingModesSummed.pop('default_factory')
    SomaModesSummed = defaultdict(int)
    for k, v in SomaModes.items():
        SomaModesSummed[k]=(len(v))
    # SomaModesSummed.pop('default_factory')

    VPN = []
    VI = []
    OV = []
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
        if 'Other Visual' in branch:
            OV.append(branch['Other Visual'])
        else:
            OV.append(0)
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
        x=branches,
        y=VPN,
        text=VPN,
        textposition='auto',
        name='VPN',
        marker=dict(color='rgb(255,0,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace2 = go.Bar(
        x=branches,
        y=OV,
        text=OV,
        textposition='auto',
        name='Other Visual',
        marker=dict(color='rgb(255, 128,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace3 = go.Bar(
        x=branches,
        y=VI,
        text=VI,
        textposition='auto',
        name='Visual Interneuron',
        marker=dict(color='rgb(255,255,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace4 = go.Bar(
        x=branches,
        y=JO,
        text=JO,
        textposition='auto',
        name='JONeuron',
        marker=dict(color='rgb(127,255,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace5 = go.Bar(
        x=branches,
        y=MI,
        text=MI,
        textposition='auto',
        name='Mechanosensory Interneuron',
        marker=dict(color='rgb(34,139,34)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace6 = go.Bar(
        x=branches,
        y=NVI,
        text=NVI,
        textposition='auto',
        name='Non-Visual Interneuron',
        marker=dict(color='rgb(0, 255, 255)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace7 = go.Bar(
        x=branches,
        y=AN,
        text=AN,
        textposition='auto',
        name='Ascending Neuron',
        marker=dict(color='rgb(30, 144, 255)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace8 = go.Bar(
        x=branches,
        y=DN,
        text=DN,
        textposition='auto',
        name='Descending Neuron',
        marker=dict(color='rgb(138,43,226)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    layout = go.Layout(
        barmode='stack',
        autosize=False,
        title="Modality by Branch by Neuron Count",
        barnorm='percent',
        yaxis=dict(title='Neuron Count'),
        xaxis=dict(
            tickfont=dict(size=40)
        ),
        legend=dict(
            font=dict(
                size=50
            ),
            traceorder = 'normal'
        )
    )
    data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return


def makeStackedModalityBySynapse(mySet, filename='Figures/Modality/Stacked Modalities by Synapse'):
    mySetCopy = shortenClassNames(mySet)
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
    OV = []
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
        if 'Other Visual' in branch:
            OV.append(branch['Other Visual'])
        else:
            OV.append(0)
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
        x=branches,
        y=VPN,
        text=VPN,
        textposition='auto',
        name='VPN',
        marker=dict(color='rgb(255,0,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace2 = go.Bar(
        x=branches,
        y=OV,
        text=OV,
        textposition='auto',
        name='Other Visual',
        marker=dict(color='rgb(255, 128,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace3 = go.Bar(
        x=branches,
        y=VI,
        text=VI,
        textposition='auto',
        name='Visual Interneuron',
        marker=dict(color='rgb(255,255,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace4 = go.Bar(
        x=branches,
        y=JO,
        text=JO,
        textposition='auto',
        name='JONeuron',
        marker=dict(color='rgb(127,255,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace5 = go.Bar(
        x=branches,
        y=MI,
        text=MI,
        textposition='auto',
        name='Mechanosensory Interneuron',
        marker=dict(color='rgb(34,139,34)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace6 = go.Bar(
        x=branches,
        y=NVI,
        text=NVI,
        textposition='auto',
        name='Non-Visual Interneuron',
        marker=dict(color='rgb(0, 255, 255)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace7 = go.Bar(
        x=branches,
        y=AN,
        text=AN,
        textposition='auto',
        name='Ascending Neuron',
        marker=dict(color='rgb(30, 144, 255)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace8 = go.Bar(
        x=branches,
        y=DN,
        text=DN,
        textposition='auto',
        name='Descending Neuron',
        marker=dict(color='rgb(138,43,226)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    layout = go.Layout(
        barmode='stack',
        autosize=False,
        title="Modality by Branch by Synapse Count",
        barnorm='percent',
        yaxis=dict(title='Neuron Count'),
        xaxis=dict(
            tickfont=dict(size=40)
        ),
        legend=dict(
            font=dict(
                size=50
            ),
            traceorder='normal'
        )
    )
    data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return


def makeStackedMorphologyBySynapse(mySet, filename='Figures/Morphology/Stacked Morphology by Synapse'):
    branches = defaultdict(list)
    for neuron in mySet:
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
        AnteriorModes[neuron.morphology].append(neuron)
    for neuron in branches['Lateral']:
        LateralModes[neuron.morphology].append(neuron)
    for neuron in branches['Medial']:
        MedialModes[neuron.morphology].append(neuron)
    for neuron in branches['Descending Tract']:
        DescendingModes[neuron.morphology].append(neuron)
    for neuron in branches['Soma Tract']:
        SomaModes[neuron.morphology].append(neuron)

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

    BIP = []
    BCP = []
    BMP = []
    BP = []
    UP = []
    UL = []
    Frag = []

    branches = ["Anterior", "Lateral", "Medial", "Descending Tract", "Soma Tract"]
    allBranchesSummed = [AnteriorModesSummed, LateralModesSummed,
                         MedialModesSummed, DescendingModesSummed,
                         SomaModesSummed]

    for branch in allBranchesSummed:
        if 'BiIpsiProject' in branch:
            BIP.append(branch['BiIpsiProject'])
        else:
            BIP.append(0)
        if 'BiContraProject' in branch:
            BCP.append(branch['BiContraProject'])
        else:
            BCP.append(0)
        if 'BiMidProject' in branch:
            BMP.append(branch['BiMidProject'])
        else:
            BMP.append(0)
        if 'BiProject' in branch:
            BP.append(branch['BiProject'])
        else:
            BP.append(0)
        if 'UniProject' in branch:
            UP.append(branch['UniProject'])
        else:
            UP.append(0)
        if 'UniLocal' in branch:
            UL.append(branch['UniLocal'])
        else:
            UL.append(0)
        if 'Fragment' in branch:
            Frag.append(branch['Fragment'])
        else:
            Frag.append(0)

    trace1 = go.Bar(
        x=branches,
        y=BIP,
        text=BIP,
        textposition='auto',
        name='Bilateral Ipsilateral Projection',
        marker=dict(color='rgb(255,0,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace2 = go.Bar(
        x=branches,
        y=BCP,
        text=BCP,
        textposition='auto',
        name='Bilateral Contralateral Projection',
        marker=dict(color='rgb(255, 128,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace3 = go.Bar(
        x=branches,
        y=BMP,
        text=BMP,
        textposition='auto',
        name='Bilateral Midline Projection',
        marker=dict(color='rgb(255,255,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace4 = go.Bar(
        x=branches,
        y=BP,
        text=BP,
        textposition='auto',
        name='Bilateral Projection',
        marker=dict(color='rgb(127,255,0)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace5 = go.Bar(
        x=branches,
        y=UP,
        text=UP,
        textposition='auto',
        name='Unilateral Projection',
        marker=dict(color='rgb(34,139,34)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace6 = go.Bar(
        x=branches,
        y=UL,
        text=UL,
        textposition='auto',
        name='Unilateral Local',
        marker=dict(color='rgb(0, 255, 255)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )
    trace7 = go.Bar(
        x=branches,
        y=Frag,
        text=Frag,
        textposition='auto',
        name='Fragment',
        marker=dict(color='rgb(30, 144, 255)'),
        width=[0.3, 0.3, 0.3, 0.3, 0.3]
    )

    layout = go.Layout(
        barmode='stack',
        autosize=False,
        title="Morphology by Branch by Synapse Count",
        barnorm='percent',
        yaxis=dict(title='Neuron Count'),
        xaxis=dict(
            tickfont=dict(size=40)
        ),
        legend=dict(
            font=dict(
                size=50
            ),
            traceorder='normal'
        )
    )
    data = [trace1, trace2, trace3, trace4, trace5, trace6, trace7]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename=filename)
    return


def makeModalityPlot(mySet):
    mySetCopy = shortenClassNames(mySet)
    modalities = defaultdict(list)
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)

    keys = list(modalities.keys())
    values = []
    for k, v in modalities.items():
        values.append(len(v))

    UnilateralModalities = defaultdict(list)
    BilateralModalities = defaultdict(list)

    for k, v in modalities.items():
        for neuron in v:
            if "Unilateral" in neuron.annotations:
                UnilateralModalities[k].append(neuron)
            elif "Bilateral" in neuron.annotations:
                BilateralModalities[k].append(neuron)

    UnilatKeys = list(UnilateralModalities.keys())
    BilatKeys = list(BilateralModalities.keys())
    UnilatVals = []
    BilatVals = []

    for k, v in UnilateralModalities.items():
        UnilatVals.append(len(v))
    for k, v in BilateralModalities.items():
        BilatVals.append(len(v))

    BilateralSyn = []
    GFSum = []
    total = 0
    for k, v in BilateralModalities.items():
        GFSum = []
        for neuron in v:
            total = total + neuron.GF1synapseCount
            GFSum.append(total)
            total = 0
        summed = sum(GFSum)
        BilateralSyn.append(summed)
    UnilateralSyn = []
    GFSum = []
    total = 0
    for k, v in UnilateralModalities.items():
        GFSum = []
        for neuron in v:
            total = total + neuron.GF1synapseCount
            GFSum.append(total)
            total = 0
        summed = sum(GFSum)
        UnilateralSyn.append(summed)


    UniText = []
    BiText = []
    count = 0
    for i in BilateralSyn:
        BiText.append("Synapses:" + str(i) + '\n' + "Neurons:" + str(BilatVals[count]))
        count = count + 1
    count = 0
    for i in UnilateralSyn:
        UniText.append("Synapses:" + str(i) + '\n' + "Neurons:" + str(UnilatVals[count]))
        count = count + 1

    trace1 = go.Bar(
        x = UnilatKeys,
        y = UnilatVals,
        text = UniText,
        opacity = 0.8,
        textposition='outside',
        marker=dict(color ='cyan'),
        name = "Unilateral",
        textfont=dict(
            size = 12,
            color = 'rgb(0,0,0)'
        ),
        outsidetextfont=dict(color = 'black')
    )

    trace2 = go.Bar(
        x = BilatKeys,
        y = BilatVals,
        text = BiText,
        opacity=0.8,
        marker=dict(color='purple'),
        textposition='outside',
        name = "Bilateral",
        textfont=dict(
            size = 12,
            color = 'rgb(0,0,0)'
        ),
       outsidetextfont=dict(color = 'black')
    )
    layout = go.Layout(title="Neuron Count by Modality and Morphology",
                       legend=dict(
                           font=dict(
                               size=50
                           )
                       )
                       )
    fig = go.Figure(data = [trace2, trace1], layout = layout)
    py.plot(fig, filename='Figures/Combination Plots/Neuron Count by Modality and Morphology')
    return


def makeModalityPlot2(mySet):
    mySetCopy = shortenClassNames(mySet)
    modalities = defaultdict(list)
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)

    keys = list(modalities.keys())
    values = []
    for k, v in modalities.items():
        values.append(len(v))

    UnilateralModalities = defaultdict(list)
    BilateralModalities = defaultdict(list)

    for k, v in modalities.items():
        for neuron in v:
            if "Unilateral" in neuron.annotations:
                UnilateralModalities[k].append(neuron)
            elif "Bilateral" in neuron.annotations:
                BilateralModalities[k].append(neuron)

    UnilatKeys = list(UnilateralModalities.keys())
    BilatKeys = list(BilateralModalities.keys())
    UnilatVals = []
    BilatVals = []

    for k, v in UnilateralModalities.items():
        UnilatVals.append(len(v))
    for k, v in BilateralModalities.items():
        BilatVals.append(len(v))

    BilateralSyn = []
    GFSum = []
    total = 0
    for k, v in BilateralModalities.items():
        GFSum = []
        for neuron in v:
            total = total + neuron.GF1synapseCount
            GFSum.append(total)
            total = 0
        summed = sum(GFSum)
        BilateralSyn.append(summed)
    UnilateralSyn = []
    GFSum = []
    total = 0
    for k, v in UnilateralModalities.items():
        GFSum = []
        for neuron in v:
            total = total + neuron.GF1synapseCount
            GFSum.append(total)
            total = 0
        summed = sum(GFSum)
        UnilateralSyn.append(summed)


    UniText = []
    BiText = []
    count = 0
    for i in BilateralSyn:
        BiText.append("Synapses:" + str(i) + '\n' + "Neurons:" + str(BilatVals[count]))
        count = count + 1
    count = 0
    for i in UnilateralSyn:
        UniText.append("Synapses:" + str(i) + '\n' + "Neurons:" + str(UnilatVals[count]))
        count = count + 1

    trace1 = go.Bar(
        x = UnilatKeys,
        y = UnilatVals,
        text = UniText,
        opacity = 0.8,
        textposition='outside',
        marker=dict(color ='cyan'),
        name = "Unilateral",
        textfont=dict(
            size = 12,
            color = 'rgb(0,0,0)'
        ),
        outsidetextfont=dict(color = 'black')
    )

    trace2 = go.Bar(
        x = BilatKeys,
        y = BilatVals,
        text = BiText,
        opacity=0.8,
        marker=dict(color='purple'),
        textposition='outside',
        name = "Bilateral",
        textfont=dict(
            size = 12,
            color = 'rgb(0,0,0)'
        ),
       outsidetextfont=dict(color = 'black')
    )




    somaLocation = defaultdict(list)
    for neuron in mySet:
        somaLocation[neuron.IpsiContraMid].append(neuron)

    keys = list(somaLocation.keys())
    values = []
    for k, v in somaLocation.items():
        values.append(len(v))

    projectionSoma = defaultdict(list)
    localSoma = defaultdict(list)

    for k, v in somaLocation.items():
        for neuron in v:
            if "projection neuron" in neuron.annotations:
                projectionSoma[k].append(neuron)
            elif "local neuron" in neuron.annotations:
                localSoma[k].append(neuron)

    ProjectKeys = list(projectionSoma.keys())
    LocalKeys = list(localSoma.keys())
    ProjectVals = []
    LocalVals = []

    for k, v in projectionSoma.items():
        ProjectVals.append(len(v))
    for k, v in localSoma.items():
        LocalVals.append(len(v))

    projectionSyn = []
    GFSum = []
    total = 0
    for k, v in projectionSoma.items():
        GFSum = []
        for neuron in v:
            total = total + neuron.GF1synapseCount
            GFSum.append(total)
            total = 0
        summed = sum(GFSum)
        projectionSyn.append(summed)
    localSyn = []
    GFSum = []
    total = 0
    for k, v in localSoma.items():
        GFSum = []
        for neuron in v:
            total = total + neuron.GF1synapseCount
            GFSum.append(total)
            total = 0
        summed = sum(GFSum)
        localSyn.append(summed)

    projectText = []
    localText = []
    count = 0
    for i in projectionSyn:
        projectText.append("Synapses:" + str(i) + '\n' + "Neurons:" + str(ProjectVals[count]))
        count = count + 1
    count = 0
    for i in localSyn:
        localText.append("Synapses:" + str(i) + '\n' + "Neurons:" + str(LocalVals[count]))
        count = count + 1

    trace3 = go.Bar(
        x = ProjectKeys,
        y = ProjectVals,
        text = projectText,
        opacity = 0.8,
        textposition='outside',
        marker=dict(color ='pink'),
        name = "Projection",
        textfont=dict(
            size = 12,
            color = 'rgb(0,0,0)'
        ),
        outsidetextfont=dict(color = 'black')
    )

    trace4 = go.Bar(
        x = LocalKeys,
        y = LocalVals,
        text = localText,
        opacity=0.8,
        marker=dict(color='orange'),
        textposition='outside',
        name = "Local",
        textfont=dict(
            size = 12,
            color = 'rgb(0,0,0)'
        ),
       outsidetextfont=dict(color = 'black')
    )

    fig = tools.make_subplots(rows=2, cols=2, subplot_titles=('Unilateral Modalities', 'Bilateral Modalities',
                                                              'Projection Soma Locations', 'Local Soma Locations'))
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 2)
    fig.append_trace(trace3, 2, 1)
    fig.append_trace(trace4, 2, 2)
    #data = [trace1, trace2, trace3, trace4]
    layout1 = go.Layout(title="Neuron Count by Modality and Morphology")
    # = go.Layout(title="Neuron Count by Soma Location and Morphology")
    #fig = go.Figure(data=data, layout=layout1)
   # fig2 = go.Figure(data=[trace3, trace4], layout=layout2)

    py.plot(fig, filename='Figures/Combination Plots/Neuron Count by Modality and Morphology')
    return



def makeRefinedModalityBars(mySet, filename='Figures/Modality/Refined Neuron Modality'):
    mySetCopy = deepcopy(mySet)
    mySetCopy = shortenClassNames(mySetCopy)
    for neuron in mySetCopy:
        if "Unclassified GF input neuron - Fragment" in neuron.annotations:
            neuron.modality = "Fragment"
        if neuron.modality == "VPN":
            neuron.modality = "Optic Lobe Projection Neurons"
        elif neuron.modality == "Other Visual":
            neuron.modality = "Optic Lobe Projection Neurons"
        elif neuron.modality == "JONeuron":
            neuron.modality = "Antennael Mechanosensory Projection Neurons"
        elif neuron.modality == "Non-Visual Interneuron":
            if "local neuron" in neuron.annotations:
                neuron.modality = "Local Interneurons"
            elif "projection neuron" in neuron.annotations:
                neuron.modality = "Other Projection Neurons"
        elif neuron.modality == "Visual Interneuron":
            if "local neuron" in neuron.annotations:
                neuron.modality = "Local Interneurons"
            elif "projection neuron" in neuron.annotations:
                neuron.modality = "Other Projection Neurons"
        elif neuron.modality == "Mechanosensory Interneuron":
            if "local neuron" in neuron.annotations:
                neuron.modality = "Local Interneurons"
            elif "projection neuron" in neuron.annotations:
                neuron.modality = "Other Projection Neurons"
        elif neuron.modality == "Descending Neuron":
            neuron.modality = "Descending Neurons"
        elif neuron.modality == "Ascending Neuron":
            neuron.modality = "Ascending Neurons"

    keys = ['Optic Lobe Projection Neurons', 'Antennael Mechanosensory Projection Neurons',
            'Other Projection Neurons', 'Local Interneurons', 'Descending Neurons', 'Ascending Neurons', 'Fragment']
    modalities = {k:[] for k in keys}
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)
    modalities.pop('Fragment')
    keys = list(modalities.keys())
    values = []
    for k, v in modalities.items():
        values.append(len(v))
    colors = ['rgb(255,0,0)', 'rgb(255,140,0)', 'rgb(255,255,0)',
                  'rgb(127,255,0)', 'rgb(34,139,34)','rgb(0,255,255)',
                  'rgb(30, 144, 255)', 'rgb(138,43,226)']
    Modalities = go.Bar(
        name='Modalities',
        x = keys,
        y = values,
        text=values,
        textposition='auto',
        marker=dict(color = colors)
    )
    layout = go.Layout(autosize=False,
        showlegend=True,
        margin=dict(b=200),
        title='Modality Bars by Neuron Count',
        xaxis=dict(
            tickfont=dict(size=20),
            range=[-0.5,10]
        ),
        yaxis=dict(title='Neuron Count'),
        legend=dict(
            font=dict(
                size=30
            )
        )
    )
    data = [Modalities]
    fig = go.Figure(data=data,layout=layout)
    py.plot(fig, filename=filename)
    return



def makeOpticLobePie(mySet, filename='Optic Lobe Pie'):
    mySetCopy = deepcopy(mySet)
    mySetCopy = shortenClassNames(mySetCopy)
    for neuron in mySetCopy:
        if "Unclassified GF input neuron - Fragment" in neuron.annotations:
            neuron.modality = "Fragment"
        if neuron.modality == "VPN":
            neuron.modality = "Optic Lobe Projection Neurons"
        elif neuron.modality == "Other Visual":
            neuron.modality = "Optic Lobe Projection Neurons"
        elif neuron.modality == "JONeuron":
            neuron.modality = "Antennael Mechanosensory Projection Neurons"
        elif neuron.modality == "Non-Visual Interneuron":
            if "local neuron" in neuron.annotations:
                neuron.modality = "Local Interneurons"
            elif "projection neuron" in neuron.annotations:
                neuron.modality = "Other Projection Neurons"
        elif neuron.modality == "Visual Interneuron":
            if "local neuron" in neuron.annotations:
                neuron.modality = "Local Interneurons"
            elif "projection neuron" in neuron.annotations:
                neuron.modality = "Other Projection Neurons"
        elif neuron.modality == "Mechanosensory Interneuron":
            if "local neuron" in neuron.annotations:
                neuron.modality = "Local Interneurons"
            elif "projection neuron" in neuron.annotations:
                neuron.modality = "Other Projection Neurons"
        elif neuron.modality == "Descending Neuron":
            neuron.modality = "Descending Neurons"
        elif neuron.modality == "Ascending Neuron":
            neuron.modality = "Ascending Neurons"

    keys = ['Optic Lobe Projection Neurons', 'Antennael Mechanosensory Projection Neurons',
            'Other Projection Neurons', 'Local Interneurons', 'Descending Neurons', 'Ascending Neurons', 'Fragment']
    modalities = {k: [] for k in keys}
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)
    opticLobe = modalities['Optic Lobe Projection Neurons']

    classes = defaultdict(list)

    for neuron in opticLobe:
        classes[neuron.classification].append(neuron)

    keys = list(classes.keys())
    values = []

    for k, v in classes.items():
        sum = 0
        for item in v:
            sum = sum + item.GF1synapseCount
        values.append(sum)

    colors = ['rgb(153,50,204)', 'rgb(255,140,0)', 'rgb(128,0,128)', 'rgb(255,255,0)','rgb(50,205,50)',
              'rgb(100,149,237)', 'rgb(220,20,60)']
    trace = go.Pie(labels=list(keys),
                    values=list(values),
                    hoverinfo='label+percent', textinfo='label+value',
                    textfont=dict(size=20),
                    name='Optic Lobe Projection Neurons',
                    marker=dict(
                        colors = colors
                    ))

    py.plot([trace], filename=filename)
    return



"""
twoNeurons = defaultdict(list)
for k,v in dataDict.items():
    if len(v) == 2:
        twoNeurons[k].append(v)

for k, v in twoNeurons.items():
    for neuron in v:
        yellow = colour.Color("yellow")
        purple = colour.Color("purple")
        orange = colour.Color("orange")
        allColors = list(blue.range_to(red, len(neuron) + 1))
        curColor = 0
        synList = []
        colors = []
        for item in neuron:
            synList.append(item.GF1synapseCount)
            if "RIGHT HEMISPHERE" in item.annotations:
                item.curColor = "purple"
            elif "LEFT HEMISPHERE" in item.annotations:
                item.curColor = "orange"
            elif "RIGHT HEMISPHERE" not in item.annotations and "LEFT HEMISPHERE" not in item.annotations:
                item.curColor = "yellow"
            colors.append(item.curColor)

twoLowTrace = go.Bar(
    x = twoKeys,
    y = twoVals1,
    marker=dict(color="rgb(0,0,225)"),
    name = "Low Value"
)
twoHighTrace = go.Bar(
    x = twoKeys,
    y = twoVals2,
    marker=dict(color = "rgb(255,51,51)"),
    name = "High Value"
)
layout = go.Layout(
    barmode='group',
    margin=go.layout.Margin(
        b=200,
        r = 150
    ), 
    xaxis = dict(tickangle = 45)
)
data = [twoLowTrace, twoHighTrace]
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='Two Neuron Soma Comparison')
"""


def testDotPlot(mySet):
    mySetCopy = shortenClassNames(mySet)
    colors = []
    for item in mySetCopy:
        if "RIGHT HEMISPHERE" in item.annotations:
            item.curColor = "purple"
        elif "LEFT HEMISPHERE" in item.annotations:
            item.curColor = "orange"
        elif "RIGHT HEMISPHERE" not in item.annotations and "LEFT HEMISPHERE" not in item.annotations:
            item.curColor = "yellow"
        colors.append(item.curColor)

    GF1Syn = []
    for item in mySetCopy:
        GF1Syn.append(item.GF1synapseCount)

    classList = []
    for item in mySetCopy:
        classList.append(item.classification)

    trace = {"x": GF1Syn,
             "y": classList,
             "marker": {"color": colors, "size": 12},
             "mode": "markers",
             "type": "scatter", }

    data = [trace]
    layout = {"title": "GF1 Synapse by Class",
              "xaxis": {"title": "GF1 Synapse Count", },
              "yaxis": {"title": "Classification"}}

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filenmae="Tests/Dot_Plot")


# compares GF input types with three neurons
# GF1 synapse counts for each neuron
def threeNeuronSynapseComparePlot(mySet):
    mySetCopy = shortenClassNames(mySet)
    dataDict = createDataDict(mySetCopy)
    threeSyns = defaultdict(list)
    for k, v in dataDict.items():
        if len(v) == 3:
            threeSyns[k].append(v)
    threeKeys = list(threeSyns.keys())
    threeVals1 = []
    threeVals2 = []
    threeVals3 = []
    for i in threeSyns.values():
        v1 = i[0][0].GF1synapseCount
        v2 = i[0][1].GF1synapseCount
        v3 = i[0][2].GF1synapseCount
        if v1 > v2 and v1 > v3:
            threeVals3.append(v1)
            if v2 > v3:
                threeVals2.append(v2)
                threeVals1.append(v3)
            else:
                threeVals2.append(v3)
                threeVals1.append(v2)
        elif v2 > v1 and v2 > v3:
            threeVals3.append(v2)
            if v1 > v3:
                threeVals2.append(v1)
                threeVals1.append(v3)
            else:
                threeVals2.append(v3)
                threeVals1.append(v1)
        elif v3 > v2 and v3 > v1:
            threeVals3.append(v3)
            if v2 > v1:
                threeVals2.append(v2)
                threeVals1.append(v1)
            else:
                threeVals2.append(v1)
                threeVals1.append(v2)
        elif v1 == v2:
            if v3 > v1:
                threeVals3.append(v3)
                threeVals2.append(v2)
                threeVals1.append(v1)
            if v1 > v3:
                threeVals3.append(v1)
                threeVals2.append(v2)
                threeVals1.append(v3)
        elif v1 == v3:
            if v2 > v1:
                threeVals3.append(v2)
                threeVals2.append(v3)
                threeVals1.append(v1)
            if v1 > v2:
                threeVals3.append(v1)
                threeVals2.apppend(v3)
                threeVals1.append(v2)
        elif v3 == v2:
            if v1 > v2:
                threeVals3.append(v1)
                threeVals2.append(v2)
                threeVals1.append(v3)
            if v2 > v1:
                threeVals3.append(v2)
                threeVals2.append(v3)
                threeVals1.append(v1)

    threeVals3Copy, threeVals2Copy, threeVals1Copy, threeKeysCopy = zip(
        *sorted(zip(threeVals3, threeVals2, threeVals1, threeKeys)))

    threeVals1Copy = reversed(threeVals1Copy)
    threeVals1Copy = list(threeVals1Copy)
    threeVals2Copy = reversed(threeVals2Copy)
    threeVals2Copy = list(threeVals2Copy)
    threeKeysCopy = reversed(threeKeysCopy)
    threeKeysCopy = list(threeKeysCopy)
    threeVals3Copy = reversed(threeVals3Copy)
    threeVals3Copy = list(threeVals3Copy)

    threeTrace1 = go.Bar(
        x=threeKeysCopy,
        y=threeVals1Copy,
        marker=dict(color="rgb(0,0,225)"),
        name="Low Value"
    )
    threeTrace2 = go.Bar(
        x=threeKeysCopy,
        y=threeVals2Copy,
        marker=dict(color="rgb(0,204,0)"),
        name="Med Value"
    )
    threeTrace3 = go.Bar(
        x=threeKeysCopy,
        y=threeVals3Copy,
        marker=dict(color="rgb(255,51,51)"),
        name="High Value"
    )
    data = [threeTrace1, threeTrace2, threeTrace3]
    layout = go.Layout(
        barmode='group',
        margin=go.layout.Margin(
            b=200,
            r=150
        ),
        xaxis=dict(tickangle=45)
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Three Neuron Synapse Comparison')
    return


# compares GF input types with two neurons
# GF1 synapse counts for each neuron
def twoNeuronSynapseComparePlot(mySet):
    mySetCopy = shortenClassNames(mySet)
    dataDict = createDataDict(mySetCopy)
    twoNeurons = defaultdict(list)
    for k, v in dataDict.items():
        if len(v) == 2:
            twoNeurons[k].append(v)

    twoKeys = list(twoNeurons.keys())
    twoVals1 = []
    twoVals2 = []
    for i in twoNeurons.values():
        val1 = i[0][0].GF1synapseCount
        val2 = i[0][1].GF1synapseCount
        if val1 > val2:
            twoVals2.append(val1)
            twoVals1.append(val2)
        if val2 > val1:
            twoVals1.append(val1)
            twoVals2.append(val2)
        if val1 == val2:
            twoVals1.append(val1)
            twoVals2.append(val2)

    twoVals2Copy, twoVals1Copy, twoKeysCopy = zip(*sorted(zip(twoVals2, twoVals1, twoKeys)))
    twoVals1Copy = reversed(twoVals1Copy)
    twoVals1Copy = list(twoVals1Copy)
    twoVals2Copy = reversed(twoVals2Copy)
    twoVals2Copy = list(twoVals2Copy)
    twoKeysCopy = reversed(twoKeysCopy)
    twoKeysCopy = list(twoKeysCopy)
    twoLowTrace = go.Bar(
        x=twoKeysCopy,
        y=twoVals1Copy,
        marker=dict(color="rgb(0,0,225)"),
        name="Low Value"
    )
    twoHighTrace = go.Bar(
        x=twoKeysCopy,
        y=twoVals2Copy,
        marker=dict(color="rgb(255,51,51)"),
        name="High Value"
    )
    layout = go.Layout(
        barmode='group',
        margin=go.layout.Margin(
            b=200,
            r=150
        ),
        xaxis=dict(tickangle=45)
    )
    data = [twoLowTrace, twoHighTrace]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Two Neuron Synapse Comparison')

    return
# creates XYZ plots of synapse locations vv

# creates input plots of full branches
# colored by distribution
def createInputPlots(mySet, allInfo):
    Structure = createStructure()
    Anterior = PB.getDistributionTrace(mySet, allInfo, "Anterior", 'rgb(220,20,60)')
    AnteriorDescending = PB.getDistributionTrace(mySet, allInfo, "AnteriorDescending", "rgb(0,100,0)")
    AnteriorLateral = PB.getDistributionTrace(mySet, allInfo, "AnteriorLateral", "rgb(0,255,255)")
    AnteriorLateralSoma = PB.getDistributionTrace(mySet, allInfo, "AnteriorLateralSoma", "rgb(255,0,255)")
    AnteriorMedial = PB.getDistributionTrace(mySet, allInfo, "AnteriorMedial", "rgb(107,142,35)")
    AnteriorMedialLateral = PB.getDistributionTrace(mySet, allInfo, "AnteriorMedialLateral", "rgb(0,255,0)")
    AnteriorMedialLateralSoma = PB.getDistributionTrace(mySet, allInfo, "AnteriorMedialLateralSoma", "rgb(0,0,255)")
    AnteriorMedialSoma = PB.getDistributionTrace(mySet, allInfo, "AnteriorMedialSoma", "rgb(139,69,19)")
    Descending = PB.getDistributionTrace(mySet, allInfo, "Descending", "rgb(70,130,180)")
    Lateral = PB.getDistributionTrace(mySet, allInfo, "Lateral", "rgb(255,165,0)")
    LateralSoma = PB.getDistributionTrace(mySet, allInfo, "LateralSoma", "rgb(147,112,219)")
    Medial = PB.getDistributionTrace(mySet, allInfo, "Medial", "rgb(255,255,0)")
    MedialDescending = PB.getDistributionTrace(mySet, allInfo, "MedialDescending", "rgb(218,165,32)")
    MedialLateral = PB.getDistributionTrace(mySet, allInfo, "MedialLateral", "rgb(105,105,105)")
    MedialLateralSoma = PB.getDistributionTrace(mySet, allInfo, "MedialLateralSoma", "rgb(128,0,128)")
    MedialSoma = PB.getDistributionTrace(mySet, allInfo, "MedialSoma", "rgb(250,128,114)")
    Soma = PB.getDistributionTrace(mySet, allInfo, "Soma", "rgb(0,0,0)")
    alldata = [Structure, Anterior, AnteriorDescending, AnteriorLateral, AnteriorLateralSoma, AnteriorMedial,
               AnteriorMedialLateral, AnteriorMedialLateralSoma, AnteriorMedialSoma, Descending, Lateral, LateralSoma,
               Medial, MedialDescending, MedialLateral, MedialLateralSoma, MedialSoma, Soma]
    anteriordata = [Structure, Anterior, AnteriorDescending, AnteriorLateral, AnteriorLateralSoma, AnteriorMedial,
                    AnteriorMedialLateral, AnteriorMedialLateralSoma, AnteriorMedialSoma]
    medialdata = [Structure, AnteriorMedial, AnteriorMedialLateral, AnteriorMedialLateralSoma, AnteriorMedialSoma,
                  Medial, MedialDescending, MedialLateral, MedialLateralSoma, MedialSoma]
    lateraldata = [Structure, AnteriorLateral, AnteriorLateralSoma, AnteriorMedialLateral, AnteriorMedialLateralSoma,
                   Lateral, LateralSoma, MedialLateral, MedialLateralSoma]
    descendingdata = [Structure, AnteriorDescending, Descending, MedialDescending]
    somadata = [Structure, AnteriorLateralSoma, AnteriorMedialLateralSoma, AnteriorMedialSoma, LateralSoma, MedialSoma,
                Soma]
    PB.createPlotlyPlot(alldata, "Synapse Scatter Plots/Input Scatter Plots/Full Branch/All Branches")
    PB.createPlotlyPlot(medialdata, "Synapse Scatter Plots/Input Scatter Plots/Full Branch/Medial Inputs")
    PB.createPlotlyPlot(lateraldata, "Synapse Scatter Plots/Input Scatter Plots/Full Branch/Lateral Inputs")
    PB.createPlotlyPlot(anteriordata, "Synapse Scatter Plots/Input Scatter Plots/Full Branch/Anterior Inputs")
    PB.createPlotlyPlot(descendingdata, "Synapse Scatter Plots/Input Scatter Plots/Full Branch/Descending Inputs")
    PB.createPlotlyPlot(somadata, "Synapse Scatter Plots/Input Scatter Plots/Full Branch/Soma Inputs")
    return


# creates input plots of branches only
# colored by distribution
def createBranchPlots(mySet, allInfo):
    Structure = createStructure()
    soma = PB.createBranchTrace(mySet, allInfo, 'soma tract', "Soma", "rgb(0,0,0)")
    antlatsoma = PB.createBranchTrace(mySet, allInfo, 'soma tract', "AnteriorLateralSoma", "rgb(255,0,255)")
    antmedlatsoma = PB.createBranchTrace(mySet, allInfo, 'soma tract', "AnteriorMedialLateralSoma", "rgb(0,0,255)")
    medlatsoma = PB.createBranchTrace(mySet, allInfo, 'soma tract', "MedialLateralSoma", "rgb(128,0,128)")
    latsoma = PB.createBranchTrace(mySet, allInfo, 'soma tract', "LateralSoma", "rgb(147,112,219)")
    medsoma = PB.createBranchTrace(mySet, allInfo, 'soma tract', "MedialSoma", "rgb(250,128,114)")
    somdata = [Structure, soma, antlatsoma, antmedlatsoma, medlatsoma, latsoma, medsoma]
    PB.createPlotlyPlot(somdata, "Synapse Scatter Plots/Input Scatter Plots/Branch Only/Soma Tract Only")

    desc = PB.createBranchTrace(mySet, allInfo, 'descending tract', "Descending", "rgb(70,130,180)")
    antdesc = PB.createBranchTrace(mySet, allInfo, 'descending tract', "AnteriorDescending", "rgb(0,100,0)")
    meddesc = PB.createBranchTrace(mySet, allInfo, 'descending tract', "MedialDescending", "rgb(218,165,32)")
    descdata = [Structure, desc, antdesc, meddesc]
    PB.createPlotlyPlot(descdata, "Synapse Scatter Plots/Input Scatter Plots/Branch Only/Descending Tract Only")

    lat = PB.createBranchTrace(mySet, allInfo, 'lateral', "Lateral", "rgb(255,165,0)")
    antlat = PB.createBranchTrace(mySet, allInfo, 'lateral', "AnteriorLateral", "rgb(0,255,255)")
    antlatsoma = PB.createBranchTrace(mySet, allInfo, 'lateral', "AnteriorLateralSoma", "rgb(255,0,255)")
    antmedlat = PB.createBranchTrace(mySet, allInfo, 'lateral', "AnteriorMedialLateral", "rgb(0,255,0)")
    antmedlatsoma = PB.createBranchTrace(mySet, allInfo, 'lateral', "AnteriorMedialLateralSoma", "rgb(0,0,255)")
    latsoma = PB.createBranchTrace(mySet, allInfo, 'lateral', "LateralSoma", "rgb(147,112,219)")
    medlat = PB.createBranchTrace(mySet, allInfo, 'lateral', "MedialLateral", "rgb(105,105,105)")
    medlatsoma = PB.createBranchTrace(mySet, allInfo, 'lateral', "MedialLateralSoma", "rgb(128,0,128)")
    latdata = [Structure, lat, antlat, antlatsoma, antmedlat, antmedlatsoma, latsoma, medlat, medlatsoma]
    PB.createPlotlyPlot(latdata, "Synapse Scatter Plots/Input Scatter Plots/Branch Only/Lateral Branch Only")

    ant = PB.createBranchTrace(mySet, allInfo, 'anterior', "Anterior", "rgb(220,20,60)")
    antdesc = PB.createBranchTrace(mySet, allInfo, 'anterior', "AnteriorDescending", "rgb(0,100,0)")
    antlat = PB.createBranchTrace(mySet, allInfo, 'anterior', "AnteriorLateral", "rgb(0,255,255)")
    antlatsoma = PB.createBranchTrace(mySet, allInfo, 'anterior', "AnteriorLateralSoma", "rgb(255,0,255)")
    antmed = PB.createBranchTrace(mySet, allInfo, 'anterior', "AnteriorMedial", "rgb(107,142,35)")
    antmedlat = PB.createBranchTrace(mySet, allInfo, 'anterior', "AnteriorMedialLateral", "rgb(0,255,0)")
    antmedlatsoma = PB.createBranchTrace(mySet, allInfo, 'anterior', "AnteriorMedialLateralSoma", "rgb(0,0,255)")
    antmedsoma = PB.createBranchTrace(mySet, allInfo, 'anterior', "AnteriorMedialSoma", "rgb(139,69,19)")
    antdata = [Structure, ant, antdesc, antlat, antlatsoma, antmed, antmedlat, antmedlatsoma, antmedsoma]
    PB.createPlotlyPlot(antdata, "Synapse Scatter Plots/Input Scatter Plots/Branch Only/Anterior Branch Only")

    med = PB.createBranchTrace(mySet, allInfo, 'medial', "Medial", "rgb(255,255,0)")
    antmed = PB.createBranchTrace(mySet, allInfo, 'medial', "AnteriorMedial", "rgb(107,142,35)")
    antmedlat = PB.createBranchTrace(mySet, allInfo, 'medial', "AnteriorMedialLateral", "rgb(0,255,0)")
    antmedlatsoma = PB.createBranchTrace(mySet, allInfo, 'medial', "AnteriorMedialLateralSoma", "rgb(0,0,255)")
    antmedsoma = PB.createBranchTrace(mySet, allInfo, 'medial', "AnteriorMedialSoma", "rgb(139,69,19)")
    meddesc = PB.createBranchTrace(mySet, allInfo, 'medial', "MedialDescending", "rgb(218,165,32)")
    medlat = PB.createBranchTrace(mySet, allInfo, 'medial', "MedialLateral", "rgb(105,105,105)")
    medlatsoma = PB.createBranchTrace(mySet, allInfo, 'medial', "MedialLateralSoma", "rgb(128,0,128)")
    medsoma = PB.createBranchTrace(mySet, allInfo, 'medial', "MedialSoma", "rgb(250,128,114)")
    meddata = [Structure, antmed, antmedlat, antmedlatsoma, antmedsoma, med, meddesc, medlat, medlatsoma, medsoma]
    PB.createPlotlyPlot(meddata, "Synapse Scatter Plots/Input Scatter Plots/Branch Only/Medial Branch Only")
    return


# makes gradient plot with given distribution
# Uses all synapses of neuron
# Anterior, AnteriorDescending, AnteriorLateral, AnteriorLateralSoma, AnteriorMedial, AnteriorMedialLateral
# AnteriorMedialLateralSoma, AnteriorMedialSoma, Descending, Lateral, LateralSoma, Medial
# MedialDescending, MedialLateral, MedialLateralSoma, MedialSoma, Soma
def makeDistributionGradientPlot(mySet, allInfo, distribution):
    distributionConnects = PB.distributionSynapses(mySet, allInfo, distribution)
    x_vals = []
    y_vals = []
    z_vals = []
    pres = []
    for item in distributionConnects:
        x_vals.append(item[1]['x'])
        y_vals.append(item[1]['y'])
        z_vals.append(item[1]['z'])
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                pres.append(partner['skeleton_id'])
    distributionColors = []
    distributionH2L = PB.makeDistributionColorGradient(mySet, allInfo, distribution)
    for item in pres:
        for item2 in distributionH2L:
            if item == item2['skeleton_id']:
                distributionColors.append(item2['color'])
    layout = go.Layout(
        title=distribution + "H2L",
        legend=dict(x=-.05, y=0.5),
        scene=dict(
            xaxis=dict(
                title='x Axis'),
            yaxis=dict(
                title='y Axis'),
            zaxis=dict(
                title='z Axis')),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0))
    H2LTrace = go.Scatter3d(
        x=x_vals,
        y=y_vals,
        z=z_vals,
        text=pres,
        mode='markers',
        marker=dict(
            size=5,
            color=distributionColors),
        name=distribution + "H2L")
    x_s = [401000, 550000, 401000, 550000, 401000, 550000, 401000, 550000]
    y_s = [192000, 192000, 298000, 298000, 192000, 192000, 298000, 298000]
    z_s = [40960, 40960, 40960, 40960, 222320, 222320, 222320, 222320]

    Structure = go.Scatter3d(
        x=x_s,
        y=y_s,
        z=z_s,
        mode='markers',
        marker=dict(
            size=1,
            color="rgb(255,255,255)"),
        name="STRUCTURE")
    fig = go.Figure(data=[Structure, H2LTrace], layout=layout)
    py.plot(fig, filename="Synapse Scatter Plots/Distribution Colored Scatter Plots/" + distribution + "_DistributionH2L")
    return


# makes gradient plot with given branch
# takes GF synapse count for ENTIRE neuron, not just H2L of branch synapses
# medial, lateral, descending tract, soma tract, anterior
def makeBranchGradientPlot(mySet, allInfo, branch):
    branchInfo = mySet.connectorInfo.get(branch)
    branchConnects = []

    for i in allInfo.items():
        cid = i[0]
        if cid in branchInfo:
            branchConnects.append(i)

    x_vals = []
    y_vals = []
    z_vals = []
    pres = []
    for item in branchConnects:
        x_vals.append(item[1]['x'])
        y_vals.append(item[1]['y'])
        z_vals.append(item[1]['z'])
        for partner in item[1]['partners']:
            if partner['relation_name'] == 'presynaptic_to':
                pres.append(partner['skeleton_id'])
    branchColors = []
    branchH2L = PB.makeBranchColorGradient(mySet, allInfo, branch)
    for item in pres:
        for item2 in branchH2L:
            if item == item2['skeleton_id']:
                branchColors.append(item2['color'])
    layout = go.Layout(
        title=branch + "H2L",
        legend=dict(x=-.05, y=0.5),
        scene=dict(
            xaxis=dict(
                title='x Axis'),
            yaxis=dict(
                title='y Axis'),
            zaxis=dict(
                title='z Axis')),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0))
    H2LTrace = go.Scatter3d(
        x=x_vals,
        y=y_vals,
        z=z_vals,
        text=pres,
        mode='markers',
        marker=dict(
            size=5,
            color=branchColors),
        name=branch + "H2L")
    x_s = [401000, 550000, 401000, 550000, 401000, 550000, 401000, 550000]
    y_s = [192000, 192000, 298000, 298000, 192000, 192000, 298000, 298000]
    z_s = [40960, 40960, 40960, 40960, 222320, 222320, 222320, 222320]

    Structure = go.Scatter3d(
        x=x_s,
        y=y_s,
        z=z_s,
        mode='markers',
        marker=dict(
            size=1,
            color="rgb(255,255,255)"),
        name="STRUCTURE")
    fig = go.Figure(data=[Structure, H2LTrace], layout=layout)
    py.plot(fig, filename="Synapse Scatter Plots/Branch Gradient Scatter Plots/" + branch + "H2L")
    return


def makeModalityBars(mySet, filename='Figures/Modality/Neuron Modality'):
    mySetCopy = shortenClassNames(mySet)
    keys = ['VPN', 'Other Visual', 'Visual Interneuron', 'JONeuron',
                  'Mechanosensory Interneuron', 'Non-Visual Interneuron',
                  'Ascending Neuron', 'Descending Neuron']
    modalities = {k:[] for k in keys}
    for neuron in mySetCopy:
        modalities[neuron.modality].append(neuron)
    keys = list(modalities.keys())
    values = []
    for k, v in modalities.items():
        values.append(len(v))
    colors = ['rgb(255,0,0)', 'rgb(255,140,0)', 'rgb(255,255,0)',
                  'rgb(127,255,0)', 'rgb(34,139,34)','rgb(0,255,255)',
                  'rgb(30, 144, 255)', 'rgb(138,43,226)']
    Modalities = go.Bar(
        name='Modalities',
        x = keys,
        y = values,
        text=values,
        textposition='auto',
        marker=dict(color = colors)
    )
    layout = go.Layout(autosize=False,
        showlegend=True,
        margin=dict(b=200),
        title='Modality Bars by Neuron Count',
        xaxis=dict(
            tickfont=dict(size=20),
            range=[-0.5,10]
        ),
        yaxis=dict(title='Neuron Count'),
        legend=dict(
            font=dict(
                size=30
            )
        )
    )
    data = [Modalities]
    fig = go.Figure(data=data,layout=layout)
    py.plot(fig, filename=filename)
    return