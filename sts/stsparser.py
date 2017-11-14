# coding: utf-8

import nltk
from nltk.corpus import stopwords
import os
import pickle
import re
from util.text import *
import numpy as np
from os.path import expanduser
import codecs
import io
from util.system import *
from util.parser import *
from datastructure import *
from sts.agirresets import *



def dataSelector(strList, regex):
    """
    This function select all string which match with the given regex in the str list.
    For example, to select all datas but 2015, use : r"(.*201[1-4].*|.*2016.*)"
    """
    return [current for current in strList if re.match(regex, current) is not None]

def dataSelectorMultiRegex(strList, regexList):
    l = []
    for str in strList:
        for regex in regexList:
            if regex is not None:
                if re.match(regex, str) is not None:
                    l.append(str)
                    break
    return l

def normalizeVector(prediction):
    min = np.min(prediction)
    max = np.max(prediction)
    prediction = np.asarray(prediction)
    prediction = np.subtract(prediction, min)
    newPrediction = []
    for score in prediction:
        newPrediction.append(normalizeUpperBound(score, max - min, 1))
    prediction = newPrediction
    return prediction

def normalizeUpperBound(number, fromUpperBound, toUpperBound):
    """
    This function convert a number wich is under the upper bound fromUpperBound to under the
    upper bound toUpperBound.
    """
    return number * toUpperBound / fromUpperBound

def normalizeFrom1To5(number):
    return normalizeUpperBound(number, 1, 5)

def normalizeFrom5To1(number):
    return normalizeUpperBound(number, 5, 1)

class STSSentencesGenerator_deprecated(object):
    """
    This class is a generator for the parsed structure of the sts corpus.
    """
    def __init__(self, parsedSTS):
        self.parsedSTS = parsedSTS

    def __iter__(self):
        for s1, s2, score in self.parsedSTS:
            yield s1
            yield s2

class STSSentencesGenerator2(object):
    """
    This class is a generator for the parsed structure of the sts corpus.
    """
    def __init__(self, hmSTS):
        self.hmSTS = hmSTS

    def __iter__(self):
        for sentencePair, (parsed1, parsed2, score) in self.hmSTS.items():
            yield parsed1
            yield parsed2

class XuParser():
    XU_STS_CORPUS_FOLDERS = ["sts-2015-task1-en-testset", "sts-2015-task1-en-trainingset"]


class AgirreParser():
    
    defaultAddSMT2013 = False
    
    AGIRRE_STS_FOLDERS = ["sts-2012-task6-en-testset", "sts-2012-task6-en-trainingset", "sts-2013-task6-en-testset", "sts-2014-task10-en-testset", "sts-2015-task2-en-testset", "sts-2016-task1-en-testset"]
    
    def __init__(self, verbose=True,
                 dataPath=None,
                 workingPath=None,
                 removeStopWords=True,
                 removePunct=True,
                 toLowerCase=True,
                 lemma=False,
                 setName="",
                 setNameTypeYear="",
                 swList=None):
        # Instance vars :
        self.dataPath = dataPath
        self.workingDirectory = workingPath
        self.verbose = verbose
        self.removeStopWords = removeStopWords
        self.removePunct = removePunct
        self.toLowerCase = toLowerCase
        self.lemma = lemma
        self.setName = setName
        self.setNameTypeYear = setNameTypeYear
        self.addSMT2013 = AgirreParser.defaultAddSMT2013
        
        self.swList = swList
        
        # Get the data path :
        if self.dataPath is None:
            if stout():
                self.dataPath = "~/similarity/sts-en"
            else:
                homePath = expanduser("~")
                self.dataPath = homePath + "/Data/similarity/sts-en"
        
        # Get the working directory :
        if self.workingDirectory is None:
            self.workingDirectory = getWorkingDirectory(__file__)
        
        # Create the hashmap :
        self.parser = None
        
        
    
    def loadFolder(self, absoluteCorpusPath):
        """
        This function return a structured list of the sts corpus in the given folder.
        The function take all "*input*.txt" files (sentences) in the folder and all "*gs*.txt" files (scores)
        in the folder (but whitout files like "*ALL*") to make the structured result.
        Exemple of output : [("sentence1" "sentence2", 0.8), ("sentence3" "sentence2", 5.0)]
        """
        if self.setName is None or self.setName == "":
            if self.verbose : print "Loading " + absoluteCorpusPath + "..."
        else:
            if self.verbose : print "Loading " + absoluteCorpusPath + " for only " + self.setName + "-" + self.setNameTypeYear
    
        # Get all files in the folder :
        if self.setName == "smt" and self.setNameTypeYear == "test2013":
            inputPaths = sortedGlob(absoluteCorpusPath + '/*additionalinp*' + self.setName + '*.txt', caseSensitive=False)
        else:
            inputPaths = sortedGlob(absoluteCorpusPath + '/*input*' + self.setName + '*.txt', caseSensitive=False)
        if self.addSMT2013 and (self.setName is None or self.setName == ""):
            inputPaths += sortedGlob(absoluteCorpusPath + '/*additionalinp*' + self.setName + '*.txt', caseSensitive=False)
        gsPaths = sortedGlob(absoluteCorpusPath + '/*gs*.txt')
        
        # We delete file containing "*ALL*" :
        inputPaths = [path for path in inputPaths if "ALL" not in path]
        gsPaths = [path for path in gsPaths if "ALL" not in path]
        
        # Check if we have the same length :
        # assert len(inputPaths) == len(gsPaths) # SMT to get https://catalog.ldc.upenn.edu/LDC2013T18
        
#         print listToStr(inputPaths)
#         print listToStr(gsPaths)
        
        # For all files :
        stsCorpus = []
        for i in range(len(inputPaths)):
            # We get current files paths :
            currentInputPath = inputPaths[i]
            # We get the corresponding gs file :
            currentGsPath = [path for path in gsPaths if currentInputPath.split('.')[-2] in path][0]
            # We open files :
            currentInput = codecs.open(currentInputPath, 'r', 'utf-8')
            # currentInput = io.open(currentInputPath, 'r', encoding='utf-8')
            currentGs = open(currentGsPath, 'r')
            # For all lines in the current file :
            for inputLine in currentInput:                
                # Strip accents :
                # inputLine = text.strip_accents(inputLine)
                # Non ascii :
                # inputLine = text.removeNonASCII(inputLine)
                # We get all sentences :
                splitedLine = inputLine.split('\t')
                # We get the score :
                scoreLine = currentGs.readline().strip()
                # If there is a score, we add the line :
                if len(scoreLine) > 0:
                    score = float(scoreLine)
                    # We add this triplet in the list :
                    # stsCorpus.append((splitedLine[0].strip().decode('utf-8'), splitedLine[1].strip().decode('utf-8'), score))
                    stsCorpus.append((splitedLine[0].strip(), splitedLine[1].strip(), score))
#                     print splitedLine[0]
#                     print splitedLine[1]
#                     print splitedLine[2]
#                     print splitedLine[3]
#                     raw_input('')
        if self.verbose :
            print str(len(stsCorpus)) + " pairs of sentences loaded."
        return stsCorpus
    
    def clean(self, regex=None):
        if regex is None:
            regex = "*computed_sts_*"
        for path in sortedGlob(self.workingDirectory + "/" + regex):
            os.remove(path)
    
    def parsePair(self, sentencePair, score):
        """
        This function parse a pair (tokenisation and stop words).
        Moreover, the score is normalized between 0 to 1.
        """
        # Get both sentence :
        s1 = sentencePair.s1
        s2 = sentencePair.s2
        # Tokenise :
        tokens1 = nltk.word_tokenize(s1)
        tokens2 = nltk.word_tokenize(s2)
        # Stop words and punct :
        if self.removeStopWords and self.swList is not None:
            tokens1 = removeStopWordsSwList(tokens1, self.swList)
            tokens2 = removeStopWordsSwList(tokens2, self.swList)
        elif self.removeStopWords:
            tokens1 = removeStopWords(tokens1)
            tokens2 = removeStopWords(tokens2)
        if self.removePunct:
            tokens1 = removePunct(tokens1)
            tokens2 = removePunct(tokens2)
        if self.toLowerCase:
            tokens1 = toLower(tokens1)
            tokens2 = toLower(tokens2)
        if self.lemma:
            tokens1 = lemmatize(tokens1)
            tokens2 = lemmatize(tokens2)
        # Adding a line :
        parsedPair = (tokens1, tokens2, normalizeFrom5To1(score))
        return parsedPair
    
    def loadSTS(self, folders=AGIRRE_STS_FOLDERS, erase=False):
        # Particular case :
        if self.setName is not None and self.setName != "":
            if len(folders) != 1:
                print "Error: only 1 folder if a setName is specified!"
                exit()
        
        if self.verbose:
            print "Starting to get the Agirre STS data..."
        
        # Get the sts corpus :
        sts = []
        for folder in folders:
            sts += self.loadFolder(self.dataPath + "/" + folder)
        
        # Create the fileId :
        if self.swList is not None:
            fileId= "sts_" + strListToHashCode(folders + self.swList)
        else:
            fileId= "sts_" + strListToHashCode(folders)
        if self.removeStopWords:
            fileId += "_nostopword"
        if self.removePunct:
            fileId += "_nopunct"
        if self.toLowerCase:
            fileId += "_lowercase"
        if self.lemma:
            fileId += "_lemma"
        if self.addSMT2013:
            fileId += "_smt2013"
        if self.setName is not None and self.setName != "":
            fileId += "_" + self.setName + "-" + self.setNameTypeYear
        
        # Create the hm :
        if erase:
            self.clean()
        self.parser = SerializableParser(autoSerialize=False, verbose=False, fileId=fileId, workingPath=self.workingDirectory)
        
        if self.verbose:
            print "Starting to parse all sentences..."
        
        # For all sentence pair, parse it :
        for (s1, s2, score) in sts:
            self.parser.parse(hashmap.SentencePair(s1, s2), self.parsePair, score=score)
        
        # Serialize if it change :
        self.parser.serializeIfChanged()
        
        if self.verbose:
            print "Total of " + str(len(self.parser.getHashMap())) + " sentence pairs loaded."
        
        return self.parser.getHashMap()


def hmTrainTestMapping(mapping=samsungPolandMapping2016, agParserParams=None, folderRegex=r".*2016.*"):
    fastSTSParsingParams = {"removeStopWords": False, "toLowerCase": False, "removePunct": False, "lemma": False}
    if fastSTSParsingParams is not None:
        fastSTSParsingParams = agParserParams
    trainingSets = []
    testSets = []
    for current2016 in mapping:
        # We get the 2016 folder :
        folders2016 = dataSelector(AgirreParser.AGIRRE_STS_FOLDERS, folderRegex)
        # And the current hm 2016 according to the current set :
        agParser = AgirreParser(verbose=False, workingPath=getWorkingDirectory(),
                                setName=current2016["fileDesc"][0],
                                setNameTypeYear=current2016["fileDesc"][1] + current2016["fileDesc"][2],
                                **fastSTSParsingParams)
        testSets.append(agParser.loadSTS(folders=folders2016))
        # Then we aggregate all train set for this current 2016 test set :
        if "trainSet" in current2016 and len(current2016["trainSet"]) > 0:
            currentHmTrain = dict()
            for currentTrainSetName in current2016["trainSet"]:
                # We get the current folder :
                regex = r".*" + currentTrainSetName[2] + ".*" + currentTrainSetName[1] + ".*"
                folders = dataSelector(AgirreParser.AGIRRE_STS_FOLDERS, regex)
                # And the hm :
                agParser = AgirreParser(verbose=False, workingPath=getWorkingDirectory(),
                                        setName=currentTrainSetName[0],
                                        setNameTypeYear=currentTrainSetName[1] + currentTrainSetName[2],
                                        **fastSTSParsingParams)
                previousSize = len(currentHmTrain.items())
                # And we add it to the current 2016 set for training:
                currentHmTrain = dict(currentHmTrain.items() + agParser.loadSTS(folders=folders).items())
                newSize = len(currentHmTrain.items())
            trainingSets.append(currentHmTrain)
    
    return (trainingSets, testSets)







