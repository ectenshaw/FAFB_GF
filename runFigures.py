import createPlots as CP

def runAllFigures(mySet):

    CP.makeSeparateBarGradients(mySet, 'ForPaper/Fig8a - 1 to 30 Synapse Neurons',
                                'ForPaper/Fig8b - 31 to 70 Synapse Neurons',
                                'ForPaper/Fig8c - 71+ Synapse Neurons')
    CP.pairTripletSynapseCompare(mySet, 'ForPaper/Fig7c - Pair and Triplet Class Synapse Comparison')
    CP.splitFourSynapseCompare(mySet, 'ForPaper/Fig7b - Contra/Ipsi 4+ Neurons Class Synapse Comparison')
    CP.fourNeuronSynapseComparePlot(mySet, 'ForPaper/Fig7a - 4+ Neurons Class Synapse Comparison')
    CP.makeStackedModalityBySynapse(mySet, 'ForPaper/Fig6b - Modality By Branch By Synapse Count')
    CP.makeStackedModalityByNeuron(mySet, 'ForPaper/Fig6a - Modality By Branch By Neuron Count')
    CP.makeModalityBars(mySet, 'ForPaper/Fig5 - Modality Bar Chart')
    CP.overHunderedNeurons(mySet, 'ForPaper/Fig4 - Over 100 Synapse Neurons')
    CP.createTopInputtingPlotAll(mySet, 'ForPaper/Fig3b - Top 10 Inputs With Visual and JO')
    CP.createTopInputtingPlot(mySet, 'ForPaper/Fig3a - Top 10 Inputs')
    CP.gfSynapseBars(mySet, 'ForPaper/Fig2 - GF1 Individual Synapse Bars')
    CP.gfClassHistogram(mySet, 'ForPaper/Fig1 - GF Histogram by Class Type')

    return

