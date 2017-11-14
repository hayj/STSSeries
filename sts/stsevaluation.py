# coding: utf-8

import os
import subprocess
import stsparser
from util.system import *
import numpy
from scipy.stats.stats import pearsonr

def getAgirrePearsonCorrelation(prediction, scores):
    # Check the length :
    assert(len(prediction) == len(scores))
    
    # Handle the output folder :
    currentDirectory = getRootDirectory(__file__)
    outputPath = currentDirectory + "/output"
    
    # Check if the output directory exists :
    assert(os.path.exists(outputPath))
    
    # Right the output file :
    gsFile = open(outputPath + "/" + "gs.txt", "w")
    outputFile = open(outputPath + "/" + "output.txt", "w")
    for score in prediction:
        outputFile.writelines([str(stsparser.normalizeFrom1To5(score)) + "\n"])
    outputFile.close()
    for score in scores:
        gsFile.writelines([str(stsparser.normalizeFrom1To5(score)) + "\n"])
    gsFile.close()
    
    # Get the Pearson correlation :
    p = subprocess.Popen(["perl", outputPath + "/" + "correlation-noconfidence.pl", outputPath + "/" + "gs.txt", outputPath + "/" + "output.txt"], stdout=subprocess.PIPE)
    line = p.stdout.readline()
    line = line.split(" ")
    pearsonCorrelation = float(line[-1])
    return pearsonCorrelation

def getNumpyPearsonCorrelation(prediction, scores):
    return numpy.corrcoef(prediction, scores)[0][1]

def getScipyPearsonCorrelation(prediction, scores):
    return pearsonr(prediction, scores)[0]

def getMeanDifference(prediction, scores):
    meanDiff = 0.0
    for i in range(len(prediction)):
        trueScore = scores[i]
        computedScore = prediction[i]
        meanDiff += abs(trueScore - computedScore)
    meanDiff = meanDiff / len(prediction)
    return meanDiff

def getMeanLeastSquares(prediction, scores):
    leastSquares = 0.0
    for i in range(len(prediction)):
        trueScore = scores[i]
        computedScore = prediction[i]
        leastSquares += (trueScore - computedScore)**2
    leastSquares = leastSquares / len(prediction)
    return leastSquares
