import CustomNeuronClassSet as CS
import exportToCSV as e2c

mySet = CS.builder()

#connector xyz location and partner info
mySet.getConnectors()

#Get partner info (visual partners)
mySet.getNumPartnersBySkid()

#Breakdown syn count by branch
mySet.getAllGFINSynByBranch()


#export CSV with cleansed data
e2c.makeCSV(mySet, "saveWithAll")

#export CSV with cleansed data and every possible annotation as a column
e2c.makeCSV(mySet, "saveWithAllAndAnnotations")
