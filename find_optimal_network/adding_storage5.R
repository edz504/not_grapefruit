
dim(StaticData)

totdist <- rep(0,71)

#find col index of existing storages
grep("S35", colnames(StaticData)) #18
grep("S51", colnames(StaticData)) #33
grep("S59", colnames(StaticData)) #41
grep("S73", colnames(StaticData)) #54


#for each storage
for (i in 3:73) {
  if (((i != 18 && i != 33) && i != 41 ) && i !=54) {
    #for each region, find closest storage among storage[i], S35, S51, S59, S73
    dist = 0
    for (j in 1:100) {
      mindist = min(StaticData[j,i],StaticData[j,18],StaticData[j,33],StaticData[j,41],StaticData[j,54])
      dist = dist + mindist
    }
    totdist[i-2] = dist
  }
  else {
    totdist[i-2] = 100000
  }
}

storage5 = which.min(totdist)

colnames(StaticData)[storage5+2] #S21





