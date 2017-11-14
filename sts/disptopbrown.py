# coding: utf-8


from text import *
from duration import *
from sts.mongohandler import *
from sts.baroniembedding import *
import os
import subprocess
import stsparser
from system import *




md2vStateBoth(printCounts=True)

scores = MongoD2VScore(scoreTypeAndFeatures="pc-lf-cv2016")
print scores.toTopString(max=5, dispEndCount=2)
 
  
printDataBases()
printAllCollections()

