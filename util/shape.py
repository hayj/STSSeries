# coding: utf-8

import math

def chunkList(l, partsCount):
    chunkedList = []
    partsItemNumber = int(math.ceil(float(len(l)) / float(partsCount)))
    for i in range(partsCount):
        left = l[:partsItemNumber]
        right = l[partsItemNumber:]
        chunkedList.append(left)
        l = right
    return chunkedList

def crossValidationChunk(l, partsCount):
    chunkedSet = chunkList(l, partsCount)
    trainingSets = []
    testSets = []
    for i in range(len(chunkedSet)):
        testSets.append(chunkedSet[i])
        currentMatrixTrainingSet = []
        for u in range(len(chunkedSet)):
            if u != i:
                currentMatrixTrainingSet.append(chunkedSet[u])
        currentListTrainingSet = []
        for current in currentMatrixTrainingSet:
            currentListTrainingSet += current
        trainingSets.append(currentListTrainingSet)
    return (trainingSets, testSets)
        
        