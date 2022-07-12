# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:46:14 2021

@author: anmorrow
"""

from bitarray import bitarray
from bitarray.util import strip
import math
import time
import sys
import numpy as np

start_time = time.time()
#parameters to diddle with
#max length is the max length of either the left or right leaf without zero trimming
maxLength = 14
gapSize=4
justOne=False #just take the 1st solution or find all and report the shortest
#

if gapSize<=1 | (not isinstance(gapSize,int)):
        print("c'mon")
        sys.exit()

#precalc the list of patterns to find
numGapBytes = math.ceil(gapSize/8)
inFieldPatterns = []
for i in range(1,(2**gapSize)-1):
    patternByte = i.to_bytes(numGapBytes,'big')
    tempBA = bitarray()
    tempBA.frombytes(patternByte)
    inFieldPatterns.append(tempBA[-gapSize:])
numPatterns = len(inFieldPatterns)

#precalc the gap bits
gaps=[]
for gap in range (gapSize+1):
    gaps.append(bitarray(gap*str('0')))

#create some special blocks that can reduce total time to search
fullBlock = bitarray()  #a pattern with 2 leaves abutted must have a full block otherwise skip it.  done later in code
fBI = (2**gapSize)-1
fBIByte = fBI.to_bytes(numGapBytes,'big')
fullBlock.frombytes(fBIByte)
fullBlock=fullBlock[-gapSize:]
#edge cases will happen in every case per the way we construct leaves that we test, so we dont need to look for them
edgeBlock10=bitarray('1')       
edgeBlock10.extend(gaps[gapSize-1])
edgeBlock01=bitarray(gaps[gapSize-1])
edgeBlock01.extend(bitarray('1'))
edgeBlock101 = bitarray('1')
edgeBlock101.extend(gaps[gapSize-2])
edgeBlock101.extend(bitarray('1'))
inFieldPatterns.remove(edgeBlock01)
inFieldPatterns.remove(edgeBlock10)
inFieldPatterns.remove(edgeBlock101)

groupedPats =[]
iFPC = inFieldPatterns.copy()
for i in range(gapSize-2):
    thisGroup=[]
    j=0
    while len(iFPC)>0:
       if len(iFPC[j].search(gaps[gapSize-2-i]))>0:
           thisGroup.append(iFPC[j])
           iFPC.remove(iFPC[j])
           j-=1
       j+=1
       if j==len(iFPC):
           break
    groupedPats.insert(0,thisGroup)
groupOrder = np.argsort([len(s) for s in groupedPats])#search smallest first!

#create all leaf pattern attempts, throw out definitely bad ones
skipSeq0 = bitarray('1')
skipSeq0.extend(bitarray((gapSize)*str('0')))
skipSeq1 = bitarray((gapSize+1)*str('1'))
#add the first value.  im too lazy to figure out why the loops below dont add it right now
leavesToTryL =[]
leavesToTryR =[]
first = bitarray((gapSize-1)*str('0'))
first.extend(bitarray('1'))
leavesToTryL.append(first)
leavesToTryR.append(first[::-1])

for leafLength in range(1,maxLength+1):
    minLeafLength = min([leafLength+gapSize-1,maxLength])
    numLeafBytes = math.ceil(minLeafLength/8)
    #if the lowest bit is 0 skip it.  kinda what we do a few lines down but this saves some cycles
    for leafTry in range((2**(leafLength-1))+1, 2**leafLength,2):    
        tempTry = leafTry.to_bytes(numLeafBytes,'big')
        tryLeaf = bitarray()
        tryLeaf.frombytes(tempTry)
        tryLeaf = tryLeaf[-minLeafLength:]
        #if there is a gap as wide as or wider than the gap, throw it out
        gapSearch = strip(tryLeaf, mode='left')
        skipL0 = len(gapSearch.search(skipSeq0,1))
        if skipL0==1:
            continue 
        #if there is a block wider than the gap throw it out
        skipL1 = len(tryLeaf.search(skipSeq1,1)) 
        if skipL1==1:
            continue 
        leavesToTryL.append(tryLeaf)
        leavesToTryR.append(tryLeaf[::-1])
numLeavesToTry = len(leavesToTryL)

solutions=[]
oldTimePassed = (time.time()-start_time)
for L in range(numLeavesToTry):       
    leftLeaf=leavesToTryL[L]
    timePassed = (time.time()-start_time)
    lll=len(leftLeaf)
    leftOfGap = min([gapSize-1,lll])
    startIndex=max([len(leftLeaf)-leftOfGap,0])
    if timePassed-oldTimePassed > 10:
        timePassed = round(timePassed)
        percentDone = round(10000*L/numLeavesToTry)/100
        print("--- %s percent---" % percentDone)
        print("--- %s seconds---" % timePassed)
        oldTimePassed = timePassed
    for R in range(numLeavesToTry):
        rightLeaf = leavesToTryR[R]
        testPatterns=[] #infuriating bug has to be handled this way
        for temp in range(len(groupedPats)):
            testPatterns.append(groupedPats[temp][:])
        #search for full block in 1st iteration.  if its not there skip all
        fullPattern = bitarray()
        fullPattern.extend(leftLeaf)
        fullPattern.extend(rightLeaf)   
        if not(len(fullPattern.search(fullBlock,1))):       
            continue
        rightOfGap = min([gapSize-1, len(rightLeaf)])
        
        #we handle the 0 gap a little differently than the rest as we will check the entire length of it.
        group = 0
        while group <len(testPatterns):
            pat=0
            while pat<len(testPatterns[group]):        
                if len(fullPattern.search(testPatterns[group][pat],1)):        
                    del testPatterns[group][pat]
                    pat-=1
                pat+=1
            group+=1
        if not(sum(len(row) for row in testPatterns)):
            solutions.append([leftLeaf,rightLeaf])
            if justOne:
                print("first solution:")
                print(solutions[0])
                print("--- %s seconds---" % timePassed)
                sys.exit()
            continue
        for gap in range(len(groupOrder)): #dont need the last gap where len(gap)=gapsize or edge cases, we build them in
            thisGap = groupOrder[gap]+1
            thisGroup = groupOrder[gap]
            fullPattern = bitarray()
            fullPattern.extend(leftLeaf)
            fullPattern.extend(gaps[thisGap])
            fullPattern.extend(rightLeaf)
            #after searching the entire length, we only need to worry around the gap
            stopIndex = min([len(fullPattern)-1,lll+thisGap+rightOfGap])
            fullPattern=fullPattern[startIndex:stopIndex]
            pat=0
            while pat<len(testPatterns[thisGroup]):        
                if len(fullPattern.search(testPatterns[thisGroup][pat],1)):        
                    del testPatterns[thisGroup][pat]
                    pat-=1
                pat+=1
                
            if not(sum(len(row) for row in testPatterns)):
                solutions.append([leftLeaf,rightLeaf])
                if justOne:
                    print("first solution:")
                    print(solutions[0])
                    print("--- %s seconds---" % timePassed)
                    sys.exit()
                continue
            if len(testPatterns[thisGroup])>0:#if you cant find all of the patterns that you need to find at this gap, stop checking these 2 leaf patterns
                break
                
if len(solutions) != 0:            
    lengths=len(solutions)*[0]
    for i in range(len(solutions)):
        lengths[i]=len(strip(solutions[i][0],mode='both'))+len(strip(solutions[i][1],mode='both'))
    print("first best solution:")
    print(solutions[lengths.index(min(lengths))])
else:
    print("no solutions")
print("--- %s seconds---" % timePassed)





