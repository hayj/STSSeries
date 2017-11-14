# coding: utf-8

import random
from util.text import *
from sts.stsevaluation import *
from sts.significancetestdata_1 import *
from sts.significancetestdata_2 import *

verbose = False

def randomPermutation(s1Prediction, s2Prediction):
    s1PredictionCopy = s1Prediction[:]
    s2PredictionCopy = s2Prediction[:]
    permutationCount = 0
    for i in range(len(s2PredictionCopy)):
        if getRandomFloat(decimalMax=10) > 0.5:
            permutationCount += 1
            tmp = s1PredictionCopy[i]
            s1PredictionCopy[i] = s2PredictionCopy[i]
            s2PredictionCopy[i] = tmp
    
    if verbose:
        print "permutationCount: " + str(permutationCount)
    
    return s1PredictionCopy, s2PredictionCopy
    

global s1Score
global s2Score
global goldenStandard
global s1Prediction
global s2Prediction
gain = s2Score - s1Score
assert len(goldenStandard) == len(s1Prediction)
assert len(s2Prediction) == len(s1Prediction)
assert gain > 0.0


R = 1000
r = 0

if verbose:
    print "xPeasonCorrelation: " + str(s1Score)
    print "yPeasonCorrelation: " + str(s2Score)
    print "currentGain: " + str(gain)
    print "\n\n"

for i in range(R):
    (x, y) = randomPermutation(s1Prediction, s2Prediction)
    xPeasonCorrelation = getNumpyPearsonCorrelation(goldenStandard, x)
    yPeasonCorrelation = getNumpyPearsonCorrelation(goldenStandard, y)
    
    currentGain = abs(xPeasonCorrelation - yPeasonCorrelation)
    if currentGain >= gain:
        r += 1
    
    if verbose:
        print "xPeasonCorrelation: " + str(xPeasonCorrelation)
        print "yPeasonCorrelation: " + str(yPeasonCorrelation)
        print "currentGain: " + str(currentGain)
        print "\n"


significance = (float(r) + 1) / (float(R) + 1)

print "significance: " + str(significance)


