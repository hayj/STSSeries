# coding: utf-8

from gensim import corpora, models, similarities
import os
from os.path import expanduser
from util import text
from util import system
from util import duration
from sts import stsparser
from sts.d2vconfigconverter import *
from nltk.corpus import brown

brownSents = None
parsedBrownCache = dict()
def loadBrown(config, featureName):
    global brownSents
    
    documents = []
    i = 0

    if "brown" in config[featureName + '.data']:
        if brownSents is None:
            brownSents = []
            for sentence in brown.sents():
                brownSents.append(sentence)
    
    # We get the already parsed brown if exists:
    hash = strToHashCode \
    (
        "removePunct" + str(config[featureName + '.data.removePunct']) + 
        "toLowerCase" + str(config[featureName + '.data.toLowerCase']) + 
        "removeStopWords" + str(config[featureName + '.data.removeStopWords']) + 
        "lemma" + str(config[featureName + '.data.lemma']) + 
        "dataPart" + str(config[featureName + '.data.dataPart'])
    )
    
    if parsedBrownCache.get(hash, None) is not None:
        print "Brown sentences loaded from the cache"
        return parsedBrownCache[hash]
    else:
    
        # Choose the right funct for sw :
        removeSWFunct = text.removeStopWords
        if config[featureName + '.data.toLowerCase']:
            removeSWFunct = text.removeStopWordsAlreadyLowered
        
        # The part of brown :
        if featureName + ".data.dataPart" in config and config[featureName + '.data.dataPart'] < 1.0:
            maxCount = int(config[featureName + '.data.dataPart'] * float(len(brownSents)))
        else:
            maxCount = len(brownSents)
        
        
        # For each sentence WITH THE RIGHT ORDER :
        if "brown" in config[featureName + '.data']:
            for sentence in brownSents:
                # sentence = removePunct(sentence, lower=True)
                if config[featureName + '.data.removePunct']:
                    sentence = removePunct(sentence)
                if config[featureName + '.data.toLowerCase']:
                    sentence = toLower(sentence)
                if config[featureName + '.data.removeStopWords']:
                    sentence = removeSWFunct(sentence)
                if config[featureName + '.data.lemma']:
                    sentence = lemmatize(sentence)
                documents.append(sentence)
                i += 1
                if i > maxCount:
                    break
        
        # Store and return :
        parsedBrownCache[hash] = documents
        print "Brown sentences stored in the cache"
        return documents


def trainWord2VecModel(config, save=True, load=True, featureName="Word2VecFeature"):
    tt = duration.TicToc()
    
    tt.tic()
    
    agParser = stsparser.AgirreParser(verbose=True, removeStopWords=config['Word2VecFeature.data.removeStopWords'], removePunct=config['Word2VecFeature.data.removePunct'], toLowerCase=config['Word2VecFeature.data.toLowerCase'], lemma=config['Word2VecFeature.data.lemma'])
    hmSTS = agParser.loadSTS(folders=stsparser.AgirreParser.AGIRRE_STS_FOLDERS)
    
    modelPath = None
    if not system.stout():
        modelPath = system.getWorkingDirectory() + "/" + "word2vec_model" + configToFileId(config, featureName="Word2VecFeature") + ".bin"
    else:
        modelPath = "~/w2vbrown" + "/" + "word2vec_model" + configToFileId(config, featureName="Word2VecFeature") + ".bin"
    model = None
    
    print "Starting " + str(modelPath)
    
    # Get the already generated model :
    if load and (len(system.sortedGlob(modelPath)) > 0):
        model = models.Doc2Vec.load(modelPath)
        print "---------------> Word2Vec model loaded from the disk."
    # Or create it :
    else:
        documents = []

        if "brown" in config[featureName + '.data']:
            documents += loadBrown(config, featureName)
            tt.tic("--------------------> brownSents parsing done.")
        
        if "stsall" in config['Word2VecFeature.data']:
            for sentencePair, (parsed1, parsed2, _) in hmSTS.items():
                documents.append(parsed1)
                documents.append(parsed2)
        workers = 4
        print "--------------------> Workers = " + str(workers)
        model = models.Word2Vec(documents, workers=workers,
                                min_count=config["Word2VecFeature.data.min_count"],
                                window=config["Word2VecFeature.data.window"],
                                size=config["Word2VecFeature.data.size"])
        if save:
            model.save(modelPath)
        tt.tic("--------------------> Training done.")
    return model



def loadConditionnalWord2Vec(hmSTS=None, erase=False, verbose=True):
    """
    This function load the Google News vectors if we are on stout.
    Else it load a word2vec model according to the parsed sts given.
    """
    model = None
    word2VecLoader = Word2VecLoader(verbose=verbose)
    if system.stout():
#         model = word2VecLoader.getGoogleNewsVectors()
        model = word2VecLoader.loadAndStore("sts_model.bin", sentences=stsparser.STSSentencesGenerator2(hmSTS), erase=erase)
    else:
        model = word2VecLoader.loadAndStore("sts_model.bin", sentences=stsparser.STSSentencesGenerator2(hmSTS), erase=erase)
    return model


def getGoogleNewsVectors(vectorsPath=None):
    if vectorsPath is None :
        fileName = "GoogleNews-vectors-negative300.bin.gz"
        folder = "~/word2vec"
        if not system.stout():
            homePath = expanduser("~")
            folder = homePath + "/Data/word2vec"
        vectorsPath = folder + "/" + fileName
    return getVectors(vectorsPath)

def getBaroniVectors(vectorsPath=None):
    if vectorsPath is None :
        fileName = "EN-wform.w.5.cbow.neg10.400.subsmpl.txt.gz"
        folder = "~/word2vec"
        if not system.stout():
            homePath = expanduser("~")
            folder = homePath + "/Data/word2vec"
        vectorsPath = folder + "/" + fileName
    return getVectors(vectorsPath, binary=False)

def getBrownVectors():
    modelPath = system.getWorkingDirectory() + "/" + "w2v_model_brown.bin"
    model = None
    # Get the already generated model :
    if (len(system.sortedGlob(modelPath)) > 0):
        model = models.Doc2Vec.load(modelPath)
    # Or create it :
    else:
        i = 0
        documents = []
        maxCount = int(1.0 * float(len(brown.sents())))
        for sentence in brown.sents():
            documents.append(sentence)
            i += 1
            if i > maxCount:
                break
        model = models.Word2Vec(documents, workers=3)
        model.save(modelPath)
    return model

def getBrownSTSAllVectors(hmSTS, config):
    modelPath = system.getWorkingDirectory() + "/" + "w2v_model_brown_stsall_s" + str(config["Word2VecFeature.data.size"]) + "_w" + str(config["Word2VecFeature.data.window"]) + ".bin"
    print modelPath
    model = None
    # Get the already generated model :
    if False and (len(system.sortedGlob(modelPath)) > 0):
        model = models.Doc2Vec.load(modelPath)
        print "--------> Word2Vec model loaded."
    # Or create it :
    else:
        i = 0
        documents = []
        maxCount = int(1.0 * float(len(brown.sents())))
        for sentence in brown.sents():
            documents.append(sentence)
            i += 1
            if i > maxCount:
                break
        for _, (parsed1, parsed2, _) in hmSTS.items():
            documents.append(parsed1)
            documents.append(parsed2)
        model = models.Word2Vec(documents, workers=3,
                                window=config["Word2VecFeature.data.window"],
                                size=config["Word2VecFeature.data.size"])
        print "--------> Word2Vec model train done."
        model.save(modelPath)
        print "--------> Word2Vec model saved."
    return model

def getVectors(vectorsPath, verbose=True, binary=True):
    """
    This get the already trained vectors from google
    """
    # Load the vectors :
    if verbose : print "Starting to load the model " + vectorsPath + " from the disk..."
    if binary:
        model = models.Word2Vec.load_word2vec_format(vectorsPath, binary=binary)
    else:
        print vectorsPath
        model = models.Word2Vec.load(vectorsPath)
    if verbose : print "Done."
    
    return model

class Word2VecLoader():
    def __init__(self, workingPath=None, verbose=True):
        # Instance vars :
        self.workingDirectory = workingPath
        self.verbose = verbose
        
        # Get the working directory :
        self.workingDirectory = system.getWorkingDirectory()
    
    def loadAndStore(self, fileName="model.bin", sentences=None, erase=False):
        """
        This function store the word2vec train according to the file name given.
        If the file already exists, it will be erased if "erase" is set to True.
        If not, the function return the previous training computation stored in the existing file.
        
        sentences can be a generator or a matrix.
        """
        modelPath = self.workingDirectory + "/" + fileName
        model = None
        # Get the already generated model :
        if (len(system.sortedGlob(modelPath)) > 0) and (erase == False):
            if self.verbose : print "Starting to load " + modelPath + " Word2Vec model from the disk."
            model = models.Word2Vec.load(modelPath)
            if self.verbose : print "Word2Vec model loaded from the disk."
        # Or create it :
        else:
            # We convert the corpus to train a word2vec :
            if self.verbose : print "Starting to create the Word2Vec model."        
            model = models.Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)
            # Save it :
            model.save(modelPath)
            if self.verbose : print "Word2Vec model created and stored on the disk."
        return model
    
    def clean(self):
        for path in system.sortedGlob(self.workingDirectory + "/" + "*model*"):
            os.remove(path)
        
