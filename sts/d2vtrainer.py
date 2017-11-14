# coding: utf-8


import random
import gzip
from util.text import *
from gensim.models import doc2vec
from threading import Thread
from util.duration import *
from util.system import *
from sts import stsparser
from sts.maltconverter import *
from datastructure.hashmap import SerializableHashMap
from sts.d2vloader import *

def getRandomIndexes(count, length):
    """
    This function return a list of indexes in a range [0, length[
    The list returned has the size "count"
    """
    if length < count:
        count = length
    randomIndexes = []
    for _ in range(count):
        currentRandom = random.randint(0, length -1)
        if currentRandom in randomIndexes:
            ok = False
            for u in range(currentRandom + 1, length):
                if u not in randomIndexes:
                    currentRandom = u
                    ok = True
                    break
            if not ok:
                for u in range(currentRandom - 1, -1, -1):
                    if u not in randomIndexes:
                        currentRandom = u
                        break
        randomIndexes.append(currentRandom)
    return randomIndexes



class MaltSentenceGenerator(object):
    """
    This class is a generator for the parsed structure of the sts corpus.
    """
    def __init__(self, dataDirectories, generateIndex=False, test=False, verbose=True, defaultFileCount=1, lemma=False, removeStopWords=False, removePunct=False, toLowerCase=False, id=None, dataPart=1.0, data=None):
        self.dataDirectories = dataDirectories
        self.verbose = verbose
        self.defaultFileCount = defaultFileCount
        self.test = test
        self.data = data
        self.lemma = lemma
        self.removeStopWords = removeStopWords
        self.removePunct = removePunct
        self.toLowerCase = toLowerCase
        self.dataPart = dataPart
        self.filesPath = []
        self.counter = 0
        self.log = ""
        self.id = ""
        self.generateIndex = generateIndex
        if id is not None:
            self.id = id + "> "
        # For all dataDirectories :
        for directory in self.dataDirectories:
            # We add the '/' if not exist at the end :
            if directory[-1] != '/':
                directory += '/'
            # We get all filesPath in :
            currentFiles = sortedGlob(directory + "*")
            # If there are filesPath :
            if (len(currentFiles) > 0):
                if test :
                    # We set the number of filesPath to take :
                    fileCount = self.defaultFileCount
                    # We get some filesPath with random :
                    randomIndexes = getRandomIndexes(fileCount, len(currentFiles))
                    # And we set the filesPath in the current directory :
                    currentFiles_tmp = []
                    for currentIndex in randomIndexes:
                        currentFiles_tmp.append(currentFiles[currentIndex])
                    currentFiles = currentFiles_tmp
                    # Verbose :
                    if verbose:
                        print "We take only " + str(currentFiles) + " in " + directory
                # We add all these filesPath :
                for currentFile in currentFiles:
                    self.filesPath.append(currentFile)
            elif verbose:
                print "Empty folder!"
            
        # We retain only a part of all files :
        if (self.dataPart < 1.0):
            filesPathTmp = []
            for i in range(int(float(len(self.filesPath)) * self.dataPart)):
                filesPathTmp.append(self.filesPath[i])
            self.filesPath = filesPathTmp
            

    def __iter__(self):
        self.counter = 0
        fileCounter = 0
        self.log = ""
        
        if self.verbose:
            print "files: " + str(self.filesPath)
                
        self.removeSWFunct = removeStopWords
        if self.toLowerCase:
            self.removeSWFunct = removeStopWordsAlreadyLowered
        
        # For all files :
        for filePath in self.filesPath:
            fileCounter += 1
            if self.verbose and fileCounter % 30 == 0:
                print self.id + str((float(fileCounter) / float(len(self.filesPath))) * 100.0) + '%' + ' on ' + filePath
            # We open the file :
            with gzip.open(filePath, 'rb') as file:
                previousSentenceIndex = 0
                currentSentence = []
                # For all lines in the current file :
                lineCount = 0
                for currentLine in file:
                    lineCount += 1
                    # We split it :
                    splitedLine = currentLine.split('\t')
                    # If we have something :
                    if len(splitedLine) >= 2:
                        # And the first element is a int :
                        if representsInt(splitedLine[0]):
                            # We get the generateIndex of the sentence :
                            currentSentenceIndex = int(splitedLine[0])
                            # If this is a new sentence :
                            if (previousSentenceIndex > 0) and (currentSentenceIndex == 1):
                                # We set the sentence according to some parameters :
                                (originalSentence, currentSentence) = self.parseSentence(currentSentence)
                                
                                # If there is something to yield :
                                if len(currentSentence) > 0:
                                    if self.generateIndex:
                                        yield (originalSentence, currentSentence)
                                    else:
                                        yield currentSentence
                                    self.counter += 1
                                # Now we start a new sentence :
                                currentSentence = []
                                previousSentenceIndex = 0
                            # If the generateIndex is the next word :
                            if currentSentenceIndex == (previousSentenceIndex + 1):
                                # We get the word :
                                word = trim(splitedLine[1])
                                # If we want all lemmas :
                                if self.lemma:
                                    # We check if it exists and if it is a word :
                                    if (len(splitedLine) >= 3) and (isWord(splitedLine[2])):
                                        word = trim(splitedLine[2])
                                # We add the token if it is not empty :
                                if len(word) > 0:
                                    currentSentence.append(word)
                                # And we set the previous to be the current :
                                previousSentenceIndex = currentSentenceIndex
                            # else wtf :
                            else:
                                self.lineError(filePath, currentLine, lineCount)
                # At the end of the current file :
                if len(currentSentence) > 0:
                    (originalSentence, currentSentence) = self.parseSentence(currentSentence)
                    if self.generateIndex:
                        yield (originalSentence, currentSentence)
                    else:
                        yield currentSentence
                    self.counter += 1
            # Disp all errors :
            if self.verbose and self.log is not None and self.log != "":
                print self.log

    def lineError(self, file, textLine, lineNumber):
        message= "Warning: file=" + file + ", line=" + str(lineNumber) + ", text=" + textLine + "\n"
        # self.log += message
    
    def parseSentence(self, currentSentence):
        # We set the sentence according to some parameters :
        originalSentence = currentSentence[:]
        if self.removePunct:
            currentSentence = removePunct(currentSentence)
        if self.toLowerCase:
            currentSentence = toLower(currentSentence)
        if self.removeStopWords:
            currentSentence = self.removeSWFunct(currentSentence)
        return (originalSentence, currentSentence)

class SentenceGeneratorForDoc2Vec(MaltSentenceGenerator):
    def __iter__(self):
        # Now we train on STS data :
        agParser = stsparser.AgirreParser(verbose=True, removeStopWords=self.removeStopWords, removePunct=self.removePunct, toLowerCase=self.toLowerCase, lemma=self.lemma)
        hmAll = agParser.loadSTS()
        for sentencePair, (parsed1, parsed2, _) in hmAll.items():
            yield doc2vec.LabeledSentence(words=(parsed1), tags=["sts_" + strToHashCode(sentencePair.s1)])
            yield doc2vec.LabeledSentence(words=(parsed2), tags=["sts_" + strToHashCode(sentencePair.s2)])
        # Yield all malt sentences :
        i = 0
        for words in super(SentenceGeneratorForDoc2Vec, self).__iter__():
            yield doc2vec.LabeledSentence(words=(words), tags=[i])
            i += 1

class Doc2VecTrainer(Thread):
    def __init__(self, config, dataDirectories, saveDirectory, test=False, verbose=False, workers=6): 
        Thread.__init__(self)
        
        self.workers = workers
        self.test = test
        self.verbose = verbose
        
        self.d2vParams = configToD2vParams(config)
        self.generatorParams = configToGeneratorParams(config)
        self.id = configToFileId(config)
        self.generatorParams['id'] = self.id
        
        self.dataDirectories = dataDirectories
        # We add the '/' if not exist at the end :
        if saveDirectory[-1] != '/':
            saveDirectory += '/'
        self.saveDirectory = saveDirectory
        
    def run(self):
        self.generateFile()
 
    def generateFile(self):
        # Init duration :
        tt = TicToc()
        tt.tic(msg=self.id)
        # We create the generator :
        mg = SentenceGeneratorForDoc2Vec(self.dataDirectories, test=self.test, verbose=self.verbose, **(self.generatorParams))
        # Train the model :
        model = doc2vec.Doc2Vec(mg, workers=self.workers, **(self.d2vParams))
        # Save it :
        model.save(self.saveDirectory + fileIdToFileName(self.id))
        # Disp the total duration :
        tt.toc(msg=(self.id + " done."))


class Doc2VecMultiTrainer():
    def __init__(self, configs, saveDirectory, threaded=False, test=False, verbose=False, workers=6):
        self.saveDirectory = saveDirectory
        self.configs = configs
        self.test = test
        self.verbose = verbose
        self.workers = workers
        self.threaded = threaded

    def generateFile(self):
        # Create the tictoc :
        tt = TicToc()
        tt.tic(msg="ALL")
        
        # For all doc2vec currentConfig :
        trainers = []
        for currentConfig in self.configs:
            dataDirectories = None
            if not stout():
                dataDirectories = None
            elif currentConfig["Doc2VecFeature.data"] == "enwiki":
                dataDirectories = None
            elif currentConfig["Doc2VecFeature.data"] == "ukwac":
                dataDirectories = None
            elif currentConfig["Doc2VecFeature.data"] == "enwiki_ukwac":
                dataDirectories = None
            
            # We start a trainer in a thread :
            trainer = Doc2VecTrainer(currentConfig, dataDirectories, self.saveDirectory, workers=self.workers, test=self.test, verbose=self.verbose)
            if self.threaded:
                trainer.start() # to use Thread, but not revelante on stout for doc2vec...
            else:
                trainer.generateFile()
            
            # We add the curren thread :
            trainers.append(trainer)
            
        # We display the total duration :
        if self.threaded:
            for trainer in trainers:
                trainer.join()
        tt.toc(msg="ALL")




def train():
    # All configs to train :
    configs = \
    [
        {
            "Doc2VecFeature": True,
            "Doc2VecFeature.data": "enwiki",
            "Doc2VecFeature.data.dataPart": 0.025,
            "Doc2VecFeature.data.size": 100,
            "Doc2VecFeature.data.window": 3,
            "Doc2VecFeature.data.min_count": 7,
            "Doc2VecFeature.data.lemma": False,
            "Doc2VecFeature.data.removeStopWords": False,
            "Doc2VecFeature.data.removePunct": True,
            "Doc2VecFeature.data.toLowerCase": True,
            "Doc2VecFeature.data.alpha": 0.05,
            "Doc2VecFeature.data.negative": 5,
            "Doc2VecFeature.data.sample": 1e-5,
            "Doc2VecFeature.data.iter": 10
        }
    ]
    
    if not stout():
        configs[0]["Doc2VecFeature.data.min_count"] = 0
        configs[0]["Doc2VecFeature.data.dataPart"] = 1.0

    # Set the directory to save all models :
    saveDirectory = "~/tmp/"
    if not stout():
        saveDirectory = getWorkingDirectory()
    
    # Init a multi-trainer :
    multiTrainer = Doc2VecMultiTrainer(configs, saveDirectory, threaded=False, verbose=True, test=False, workers=6)
    
    # Launch it :
    multiTrainer.generateFile()

def train2():
    # Premier fait  :
    # fileId = "_s100_w2_mc0_a0.08_i22_sa6.8e-05_lemma_lowercase_smallsw1_enwiki2_part0.02"
    # Deuxieme fait :
    # fileId = "_s150_w2_mc0_a0.07_i22_sa6.8e-05_lemma_nopunct_lowercase_enwiki2_part0.02"
    # Troisieme  fait :
    # fileId = "_s100_w3_mc0_a0.08_i22_sa0.00012_lemma_nopunct_lowercase_smallsw1_enwiki2_part0.02"
    # 4 fait
    # fileId = "_s1000_w1_mc0_a0.07_i22_sa6e-05_lemma_nopunct_lowercase_enwiki2_part0.02"
    # 5 en cours :
    # fileId = "_s4000_w20_mc0_a0.12_i10_sa1e-05_lemma_nopunct_lowercase_enwiki2_part0.02"
    # 6 en cours
    # fileId = "_s1184_w1_mc6_a0.13_i18_sa4.68e-05_n2_lemma_lowercase_enwiki2_part0.02"
    # 7 en cours
    # fileId = "_s200_w1_mc0_a0.07_i22_sa6e-05_lemma_lowercase_enwiki2_part0.02"
    # 8 en cours
    # fileId = "_s1326_w1_mc3_a0.1_i14_sa0.0001452_lemma_nopunct_lowercase_enwiki2_part0.02"
    # 9 en cours
    # fileId = "_s3000_w8_mc200_a0.1_i20_n5_lemma_nopunct_lowercase_enwiki2_part0.02"
    # 10 en cours
    # fileId = "_s5176_w5_mc145_a0.06_i20_sa5.66e-05_n7_nopunct_smallsw1_enwiki2_part0.02"
    # 11 en cours
    # fileId = "_s100_w2_mc0_a0.1_i22_n29_lemma_nopunct_lowercase_enwiki2_part0.02"
    # Un autre avec un gros negative
    fileId = "_s150_w1_mc0_a0.07_i22_sa6e-05_n200_lemma_nopunct_lowercase_enwiki2_part0.02"
    

    
    print "fileId:\n" + fileId
    config = fileIdToConfig(fileId)
    print "config:\n" + listToStr(config)
    parsingConfig = parsingStringToParsingConfig(fileId)
    print "parsingConfig:\n" + listToStr(parsingConfig)
    swList = parsingConfigToSwList(parsingConfig)
    print "swList:\n" + str(swList)
    model = trainDoc2VecModel(config, swList=swList, fileId=fileId)
    print model["man"]
    print "OK"

if __name__ == '__main__':
    train2()
