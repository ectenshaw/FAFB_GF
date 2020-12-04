import CustomNeuronClassSet as CS



def getBranchDistribution():
    #builds GF input set
    GiantFiberSet = CS.builder()

    anterior = []
    anteriormedial = []
    anteriorlateral = []
    anteriorsoma = []
    anteriordescending = []
    medial = []
            for i in GiantFiberSet:
                # print(i.annotations)
                for j in i.annotations:
                    # print(j)
                    if "Input to GF1 anterior" in j:
                        anterior.append(i)
                    if "Input to GF1 medial" in j:
                        medial.append(i)
                for k in anterior:
                    if "Input to GF1 medial" in k.annotations:
                        anterior.remove(k)
                        anteriormedial.append(k)
                for k in anterior:
                    if "Input to GF1 lateral" in k.annotations:
                        anterior.remove(k)
                        anteriorlateral.append(k)
                for k in anterior:
                    if "Input to GF1 soma tract" in k.annotations:
                        anterior.remove(k)
                        anteriorsoma.append(k)
                for k in anterior:
                    if "Input to GF1 descending tract" in k.annotations:
                        anterior.remove(k)
                        anteriordescending.append(k)


