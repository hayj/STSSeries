# coding: utf-8

from gensim.models import doc2vec
from util.text import *
from util.duration import *
from util.system import *
from gensim import utils, matutils
from gensim import corpora, models, similarities
from util import text
from util import system
from sts.maltconverter import *
from sts.d2vconfigconverter import *
from sts.stsparser import *
from sts.word2vecloader import *
import os.path
import collections
from nltk.corpus import brown

def trainDoc2VecModel(config, save=True, load=True, featureName="Doc2VecFeature", swList=None, fileId=None, verbose=True):
    # For time printing :
    tt = TicToc()
    
    # Init the STS data according to the config and a potential stop word list :
    agParser = AgirreParser(verbose=False,
                            removeStopWords=config['Doc2VecFeature.data.removeStopWords'],
                            removePunct=config['Doc2VecFeature.data.removePunct'],
                            toLowerCase=config['Doc2VecFeature.data.toLowerCase'],
                            lemma=config['Doc2VecFeature.data.lemma'],
                            swList=swList)
    hmSTS = agParser.loadSTS()
    
    # Choose a right number of workers :
    if "enwiki2" in config[featureName + '.data']:
        workers = 20
    else:
        workers = 3
    
    # if we train the big model enwiki2, we allow news sentence SMT 2013 :
    previousDefaultAddSMT2013 = AgirreParser.defaultAddSMT2013
    if "enwiki2" in config[featureName + '.data']:
        AgirreParser.defaultAddSMT2013 = True
        
    # The default fileId is from the config :
    if fileId is None:
        fileId = configToFileId(config)
    
    # We find the right model path :
    modelPath = None
    if "enwiki2" in config[featureName + '.data']:
        assert stout()
        modelPath = "~/d2venwiki2" + "/" + "doc2vec_model" + fileId + ".bin"
    else:
        if not stout():
            modelPath = system.getWorkingDirectory() + "/" + "doc2vec_model" + fileId + ".bin"
        else:
            modelPath = "~/d2vbrown" + "/" + "doc2vec_model" + fileId + ".bin"
   
    # This is the model :
    model = None
    
    # Get the already generated model :
    if load and (len(system.sortedGlob(modelPath)) > 0):
        model = models.Doc2Vec.load(modelPath)
        print "Doc2Vec model loaded from the disk : " + str(modelPath)
    # Or create it :
    else:
        # For enwiki2, we have to init the sentence generator and train the model :
        if "enwiki2" in config[featureName + '.data']:
            if verbose:
                print "Starting trainnig enwiki2 model: " + str(modelPath)
            dataDirectories = None
            parsingConfig = parsingStringToParsingConfig(fileId)
            
            cmsg = ConvertedMaltSentenceGeneratorForD2V(hmSTS,
                                                        parsingConfig,
                                                        dataDirectories,
                                                        dataPart=config[featureName + ".data.dataPart"],
                                                        verbose=True)
            
            model = doc2vec.Doc2Vec(cmsg, workers=workers, **(configToD2vParams(config)))
            
        # Else we get STS sentences and brown sentences :
        else:
            print "Starting trainnig " + str(modelPath)
            i = 0
            documents = []
            tt.tic()
            if "brown" in config[featureName + '.data']:
                brownDocs = loadBrown(config, featureName)
                for currentSentence in brownDocs:
                    documents.append(doc2vec.LabeledSentence(words=(currentSentence), tags=[i]))
                    i += 1
                tt.tic("--------------------> brownSents parsing done.")
                
            for sentencePair, (parsed1, parsed2, _) in hmSTS.items():
                documents.append(doc2vec.LabeledSentence(words=(parsed1), tags=["sts_" + strToHashCode(sentencePair.s1)]))
                documents.append(doc2vec.LabeledSentence(words=(parsed2), tags=["sts_" + strToHashCode(sentencePair.s2)]))
            
            print "--------------------> Workers = " + str(workers)
            model = doc2vec.Doc2Vec(documents, workers=workers, **(configToD2vParams(config)))
        
        # Then we save the model :
        if save:
            model.save(modelPath)
        tt.tic("--------------------> Training done.")
    
    # We replace the default smt 2013 :
    AgirreParser.defaultAddSMT2013 = previousDefaultAddSMT2013
    
    # We freeze the model for better perf :
    model.init_sims(replace=True)
    
    # Return the model generated or loaded :
    return model



def loadHalfUkwacDoc2VecModel(path):
    model = models.Doc2Vec.load(path)
    return model



def loadWikipediaUkwacDoc2VecModel(path):
    model = models.Doc2Vec.load(path)
    return model


def loadConditionalD2VModel(config):
    # We create the id :
    id = configToFileId(config)
    fileName = fileIdToFileName(id)
    filePath = fileNameToFilePath(fileName)
    
    if not fileExists(filePath):
        return None
    
    model = models.Doc2Vec.load(filePath)
    return model


def loadConditionalD2VModelTest():
    fileName = "doc2vec_model_s100_w8_mc7_nopunct_lowercase_test.bin"
    folder = ""
    folder = getWorkingDirectory(__file__)
    model = models.Doc2Vec.load(folder + "/" + fileName)
    return model

