import userStatistics as US

#get Num Users
myUserList = US.getUniqueUserIDs()


#get stats
allCatmaidStats = US.getAllUserStats('2018-05-31')
CATstats = US.getCatStats('2018-05-31')
catPercent = US.getCatPercentage('2018-05-31')
allNodes = US.getAllNodes()
CATNodes = US.getCATNodes()

#print(allCatmaidStats)
#print(CATstats)
#print(catPercent)