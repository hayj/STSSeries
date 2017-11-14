# coding: utf-8

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

import nltk
from nltk.corpus import stopwords
import nltk
import numpy as np
from gensim import corpora, models, similarities
import os
import cPickle as pickle
import psutil
import re
import random
import subprocess
from stsparser import *
from stsevaluation import *
from word2vecloader import *
from util.text import *
from util.system import *
from scipy import spatial
import re
from aligner import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
import math
from util.duration import *
import random
from gensim.models import doc2vec
from gensim import utils, matutils
from numpy import dot
from machinelearning.feature import Feature
from sts.d2vloader import *
from machinelearning.optimizer import *
from util.shape import *
from sts.stsfeatures import *
from sts.stsparameters import *
import sys
import gc
from sklearn.svm import *
from sklearn.kernel_ridge import KernelRidge
from sts.mongohandler import *
from machinelearning.stat import *
import datetime

"""
Depends on Sultan sultanAligner and Stanford CoreNLP server interface.
"""

############################################################
####################### TRAINER ############################
############################################################

# globalD2vModelCache = None

class STSRegresser():
    def __init__ \
    (
        self,
        memoryUsageMax=40.0,
        autoManageMemory=True,
        stanfordParse=False,
        verbose=True,
        qualitativeAnalysis=False,
        saveD2vScore=False,
        saveD2vModels=True,
        saveMultiD2vScore=False,
        multiD2vHierarchicalTop=None,
        multiD2vModelType=None,
        multiD2vDbNameSource=None,
        multiD2vCollectionNameSource=None,
        randomFolderd2vBrown=False,
        featureAblationMod=False
    ):
        global globalD2vModelCache
    
        self.hmCache = dict()
        self.w2vModel = None
        self.d2vModel = None
        self.sultanAligner = None
        self.hmTrain = None
        self.hmTest = None
        self.hmAll = None
        self.w2vModelCache = dict()
        
        self.d2vModelCache = dict()
        
        self.featuresCache = dict()
        self.trainingSets = None
        self.testSets = None
        self.autoManageMemory = autoManageMemory
        self.featureAblationMod = featureAblationMod
        self.memoryUsageMax = memoryUsageMax
        self.verbose = verbose
        self.multiD2vModel = []
        self.qualitativeAnalysis = qualitativeAnalysis
        self.trainSetRegex = None
        self.testSetRegex = None
        self.saveD2vScore = saveD2vScore
        self.d2vMongo = None
        self.saveD2vModels = saveD2vModels
        self.d2vMongoAddCount = 0
        
        self.randomFolderd2vBrown = randomFolderd2vBrown
        
        self.multiD2vModelType = multiD2vModelType
        self.saveMultiD2vScore = saveMultiD2vScore
        self.multiD2vHierarchicalTop = multiD2vHierarchicalTop
        self.multiD2vDbNameSource = multiD2vDbNameSource
        self.multiD2vCollectionNameSource = multiD2vCollectionNameSource
        
        
        
        originalAGParser = AgirreParser(verbose=False, removeStopWords=False, removePunct=False, toLowerCase=False, lemma=False)
        self.originalSTS = originalAGParser.loadSTS()
                
        loweredAGParser = AgirreParser(verbose=False, removeStopWords=False, removePunct=False, toLowerCase=True, lemma=False)
        self.loweredSTS = loweredAGParser.loadSTS()
        
        onlyLoweredLemmaAGParser = AgirreParser(verbose=False, removeStopWords=True, removePunct=True, toLowerCase=True, lemma=True)
        self.onlyLoweredLemmaSTS = onlyLoweredLemmaAGParser.loadSTS()
        
        self.lemmaLoNpWithoutSwSTS = self.onlyLoweredLemmaSTS
        
        currentAgParser = AgirreParser(verbose=False, removeStopWords=False, removePunct=True, toLowerCase=True, lemma=True)
        self.lemmaLoNpWithSwSTS = currentAgParser.loadSTS()
        
        currentAgParser = AgirreParser(verbose=False, removeStopWords=True, removePunct=True, toLowerCase=True, lemma=False)
        self.loNpWithoutSwSTS = currentAgParser.loadSTS()
        
        currentAgParser = AgirreParser(verbose=False, removeStopWords=False, removePunct=True, toLowerCase=True, lemma=False)
        self.loNpWithSwSTS = currentAgParser.loadSTS()
            
        
        # Global inits :
        ## Init the Sultan sultanAligner :
        if self.sultanAligner is None:
            self.sultanAligner = SultanAligner(verbose=False)
        ## Parse all sentences (comment these lines if all sentences are already parsed entirely to save 8 seconds) :
        if stanfordParse:
            tt = TicToc()
            tt.tic("Stanford parsing...")
            hmAll = self.originalSTS
            sentences = []
            for sentencePair, (_, _, _) in hmAll.items():
                sentences.append(sentencePair.s1)
                sentences.append(sentencePair.s2)
            self.sultanAligner.parseAll(sentences)
            tt.toc("Stanford parsing for all sentences done.")
    
    def manageMemory(self, config):
        caches = [(self.d2vModelCache, Doc2VecFeature, 0), (self.w2vModelCache, Word2VecFeature, 1)]
        
        # While there is not enough memory :
        while psutil.virtual_memory().percent > self.memoryUsageMax:
            print "Purging memory..."
            freeOne = False
            # For all caches :
            for cache, Feature, minToDelete in caches:
                # We get items :
                cacheItems = cache.items()
                # And if there are enough items :
                if len(cacheItems) > minToDelete:
                    # We get the type :
                    (key0, value0) = cacheItems[0]
                    strClass = str(value0.__class__.__name__)
                    # We delete a good one (according to the current we will use :
                    for key, value in cacheItems:
#                         if minToDelete == 0 or key != Feature.getDataHashConfig(config):
                        if key != Feature.getDataHashConfig(config):
                            del cache[key]
                            freeOne = True
                            print "Memory manager: " + key + " (" + strClass + ") deleted"
                            break
                    # Here there is a item deleted, so we can continue the while
                    break
                # Else we check the next cache...
            
            # To manage the feature cache :
            if not freeOne:
                featureCacheItems = self.featuresCache.items()
                if len(featureCacheItems) > 1:
                    (key, value) = self.featuresCache.items()[0]
                    del self.featuresCache[key]
                    freeOne = True
            
            # We can collect the garbage or stop :
            if freeOne:
                gc.collect()
            else:
                break
            
                
            
    def printMemoryUsage(self):
        print "w2vModelCache"
        print getMemoryUsage(self.w2vModelCache)
        print "d2vModelCache"
        print getMemoryUsage(self.d2vModelCache)
        print "featuresCache"
        print getMemoryUsage(self.featuresCache)
        print "hmCache"
        print getMemoryUsage(self.hmCache)
        print "mem usage"
        print psutil.virtual_memory().percent

    
    def init(self, config):
        # Some inits :
        tt = TicToc()
        tt.tic("Regresser init...")
        
        # Set regex to select folder for all set for the regressor :
        if 'data' not in config or config['data'] == 'Normal2016':
            self.trainSetRegex = r".*201[1-5].*"
            self.testSetRegex = r".*2016.*test.*"
        elif config['data'] == 'NormalSets2016':
            self.trainSetRegex = r".*201[1-5].*"
            self.testSetRegex = r".*2016.*test.*"
        elif config['data'] == 'NormalSets2015':
            self.trainSetRegex = r".*201[1-4].*"
            self.testSetRegex = r".*2015.*test.*"
        elif config['data'] == 'SamsungPolandMappingSets2016':
            self.trainSetRegex = r".*201[1-5].*"
            self.testSetRegex = None
        elif config['data'] == 'DLSMappingSets2015':
            self.trainSetRegex = r".*201[1-4].*"
            self.testSetRegex = None
        elif config['data'] == 'Normal2015':
            self.trainSetRegex = r".*201[1-4].*"
            self.testSetRegex = r".*2015.*test.*"
        elif config['data'] == 'Normal2012':
            self.trainSetRegex = r".*2012.*train"
            self.testSetRegex = r".*2012.*test.*"
        elif config['data'] == 'CrossValidation2015':
            self.trainSetRegex = r".*201[1-4].*"
            self.testSetRegex = None
        elif config['data'] == 'CrossValidation2016':
            self.trainSetRegex = r".*201[1-5].*"
            self.testSetRegex = None
        elif config['data'] == 'CrossValidation2017':
            self.trainSetRegex = r".*201[1-6].*"
            self.testSetRegex = None
        else:
            self.trainSetRegex = r".*201[1-2].*"
            self.testSetRegex = r".*2013.*"

        # Get STS datas and cache it :
        hmCacheKey = strToHashCode(listToStr([self.trainSetRegex, self.testSetRegex, config['agParser.removeStopWords'], config['agParser.removePunct'], config['agParser.toLowerCase']]))
        hmTrain = None
        hmTest = None
        hmAll = None
        # If we already have this combinason in the cache :
        if hmCacheKey in self.hmCache:
            (hmTrain, hmTest, hmAll) = self.hmCache[hmCacheKey]
        else:
            # Else we parse all datas (and maybe load it from the disk):
            self.agParser = AgirreParser(verbose=True, removeStopWords=config['agParser.removeStopWords'], removePunct=config['agParser.removePunct'], toLowerCase=config['agParser.toLowerCase'], lemma=config['agParser.lemma'])
            hmTrain = self.agParser.loadSTS(folders = dataSelector(AgirreParser.AGIRRE_STS_FOLDERS, self.trainSetRegex))
            if self.testSetRegex is not None:
                hmTest = self.agParser.loadSTS(folders = dataSelector(AgirreParser.AGIRRE_STS_FOLDERS, self.testSetRegex))
            if hmTest is None:
                hmAll = hmTrain
            else:
                hmAll = dict(hmTrain.items() + hmTest.items())
            self.hmCache[hmCacheKey] = (hmTrain, hmTest, hmAll)
            tt.tic("STS parsing done.")
        self.hmTrain = hmTrain
        self.hmTest = hmTest
        self.hmAll = hmAll
                
#         if "Word2VecFeature" in config and config['Word2VecFeature']:
#             self.updateW2vModel(config)
#             tt.tic("word2vec model training done.")

        if "Doc2VecFeature" in config and config['Doc2VecFeature']:
            self.updateD2vModel(config)
            tt.tic("doc2vec model done.")

        tt.toc("Init done.")
        
        return True
    
    def updateW2vModel(self, config):
        # Train a word2vec :
        w2vModelCacheKey = Word2VecFeature.getDataHashConfig(config)
        self.w2vModel = self.w2vModelCache.get(w2vModelCacheKey)
        if self.w2vModel is None:
            if 'brown' in config['Word2VecFeature.data'] or 'stsall' in config['Word2VecFeature.data']:
                self.w2vModel = trainWord2VecModel(config)
#             if config['Word2VecFeature.data'] == 'stsall':
#                 word2VecLoader = Word2VecLoader()
#                 self.w2vModel = word2VecLoader.loadAndStore("w2v_model_stsall.bin", erase=True, sentences=stsparser.STSSentencesGenerator2(self.hmAll))
            elif config['Word2VecFeature.data'] == 'ststrain':
#                 word2VecLoader = Word2VecLoader()
#                 self.w2vModel = word2VecLoader.loadAndStore("w2v_model_ststrain.bin", erase=True, sentences=stsparser.STSSentencesGenerator2(self.hmTrain))
                print "error w2v ststrain"
                exit()
#             elif config['Word2VecFeature.data'] == 'brown':
#                 self.w2vModel = getBrownVectors()
#             elif config['Word2VecFeature.data'] == 'brown_stsall':
#                 self.w2vModel = getBrownSTSAllVectors(self.hmAll, config)
            elif config['Word2VecFeature.data'] == 'BaroniVectors':
                self.w2vModel = getBaroniVectors()
            elif config['Word2VecFeature.data'] == 'GoogleNews':
                self.w2vModel = getGoogleNewsVectors()
            if self.w2vModel is None:
                return False
            self.w2vModel.init_sims(replace=True)
            self.w2vModelCache[w2vModelCacheKey] = self.w2vModel
        return self.w2vModel
                
        
        
    def updateD2vModel(self, config, swList=None, fileId=None):
        # Train the doc2vec model :
        d2vModelCacheKey = Doc2VecFeature.getDataHashConfig(config)
        self.d2vModel = self.d2vModelCache.get(d2vModelCacheKey)
        if self.d2vModel is None:
            if config['Doc2VecFeature.data'] in ['brown', 'stsall', 'enwiki2']:
                self.d2vModel = trainDoc2VecModel(config, save=self.saveD2vModels, swList=swList, fileId=fileId)
            else:
                self.d2vModel = loadConditionalD2VModel(config)
            if self.d2vModel is None:
                return False
            self.d2vModel.init_sims(replace=True)
            self.d2vModelCache[d2vModelCacheKey] = self.d2vModel
#         else:
#             print "Doc2Vec model loaded from the cache: " + configToFileId(config)
        return self.d2vModel
                 
    
    
    def getFeatures(self, hmSTS, config, cacheId=""):
        if len(hmSTS.items()) == 0:
            return None
        
        # init the baroni :
#         if self.baroniSTS is None and \
#                 "BaroniVectorsFeature" in config and \
#                 config["BaroniVectorsFeature"]:
#             currentAGParser = AgirreParser(verbose=False,
#                                            removeStopWords=config["BaroniVectorsFeature.removeStopWords"],
#                                            removePunct=config["BaroniVectorsFeature.removePunct"],
#                                            toLowerCase=config["BaroniVectorsFeature.toLowerCase"],
#                                            lemma=config["BaroniVectorsFeature.lemma"])
#             self.baroniSTS = currentAGParser.loadSTS()
        
        
        tt = TicToc()
        tt.tic("Getting features...")
        
        # We get all features according to the config :
        allFeatures = []
        if 'LengthFeature' in config and config['LengthFeature']:
            allFeatures.append(LengthFeature)
        if 'SentencePairFeature' in config and config['SentencePairFeature']:
            allFeatures.append(SentencePairFeature)
        if 'Word2VecFeature' in config and config['Word2VecFeature']:
            allFeatures.append(Word2VecFeature)
        if 'SultanAlignerFeature' in config and config['SultanAlignerFeature']:
            allFeatures.append(SultanAlignerFeature)
        if 'RandomFeature' in config and config['RandomFeature']:
            allFeatures.append(RandomFeature)
        if 'Doc2VecFeature' in config and config['Doc2VecFeature']:
            allFeatures.append(Doc2VecFeature)
        if 'MultiDoc2VecFeature' in config and config['MultiDoc2VecFeature']:
            allFeatures.append(MultiDoc2VecFeature)
        if 'BaroniVectorsFeature' in config and config['BaroniVectorsFeature']:
            allFeatures.append(BaroniVectorsFeature)
        if 'JacanaAlignFeature' in config and config['JacanaAlignFeature']:
            allFeatures.append(JacanaAlignFeature)
        if len(allFeatures) == 0:
            return None
        
        if self.featureAblationMod and len(allFeatures) > 1:
            return None
        
#         w2vSTS = None
#         if 'Word2VecFeature' in config and config['Word2VecFeature']:
#             if "brown" in config['Word2VecFeature.data'] or "stsall" in config['Word2VecFeature.data']:
#                 currentAGParser = AgirreParser(verbose=False, removeStopWords=config['Word2VecFeature.data.removeStopWords'], removePunct=config['Word2VecFeature.data.removePunct'], toLowerCase=config['Word2VecFeature.data.toLowerCase'], lemma=config['Word2VecFeature.data.lemma'])
#                 w2vSTS = currentAGParser.loadSTS()
                
#         if 'JacanaAlignFeature' in config and config['JacanaAlignFeature']:
#             if self.hmSTSJacana is None:
#                 currentAGParser = AgirreParser(verbose=False,
#                                                removeStopWords=config['JacanaAlignFeature.removeStopWords'],
#                                                removePunct=config['JacanaAlignFeature.removePunct'],
#                                                toLowerCase=config['JacanaAlignFeature.toLowerCase'],
#                                                lemma=config['JacanaAlignFeature.lemma'])
#                 self.hmSTSJacana = currentAGParser.loadSTS()
        
        
        # We create all helpers for these features :
        featuresHelpers = \
        {
            'd2vModel': self.d2vModel,
            'sultanAligner': self.sultanAligner,
            'config': config,
            'parsed1': None,
            'parsed2': None,
            'd2vModelCache': self.d2vModelCache,
            'manageMemoryFunct': self.manageMemory,
            'updateD2vModelFunct': self.updateD2vModel,
            'originalSTS': self.originalSTS,
            'loweredSTS': self.loweredSTS,
            'onlyLoweredLemmaSTS': self.onlyLoweredLemmaSTS,
            'lemmaLoNpWithoutSwSTS': self.lemmaLoNpWithoutSwSTS,
            'lemmaLoNpWithSwSTS': self.lemmaLoNpWithSwSTS,
            'loNpWithoutSwSTS': self.loNpWithoutSwSTS,
            'loNpWithSwSTS': self.loNpWithSwSTS,
            'hmSTS': hmSTS,
            'stsRegressor': self,
        }
        
        # And for each feature, we compute the result :
        results = []
        for CurrentFeature in allFeatures:
            # We get the feature already computed in memory
            hashConfig = CurrentFeature.getFeatureHashConfig(config) + cacheId
            currentResult = self.featuresCache.get(hashConfig)
            if currentResult is None:
                currentResult = []
                feature = CurrentFeature(erase=False, config=config)
                
                # Init the feature :
                initParsingResult = None
                if feature.needInit():
                    toInit = False
                    # Check if all are already computed :
                    for sentencePair, (_, _, _) in hmSTS.items():
                        if sentencePair not in feature.hm.dict:
                            toInit = True
                            break
                    if toInit:
                        print "Initialisation of " + CurrentFeature.__name__ + ":"
                        initParsingResult = feature.initParsing(**(featuresHelpers))
                
                featuresHelpers['initParsingResult'] = initParsingResult
                for sentencePair, (parsed1, parsed2, _) in hmSTS.items():
                    featuresHelpers['parsed1'] = parsed1
                    featuresHelpers['parsed2'] = parsed2
                    currentResult.append(feature.parse(sentencePair, **(featuresHelpers)))
#                 print "||||||||||| 1 " + str(len(currentResult))
#                 print "||||||||||| 2 " + str(len(currentResult[0]))
                feature.serializeIfChanged()
                self.featuresCache[hashConfig] = currentResult
            else:
                print "features " + CurrentFeature.__name__.lower() + " loaded from the cache"
            results.append(currentResult)
            tt.tic(str(CurrentFeature.__name__.lower()) + " done.")
        if len(results) == 0:
            return None
        
        if 'MultiDoc2VecFeature' in config and config['MultiDoc2VecFeature']:
            if MultiDoc2VecFeature.similarityParser is not None:
                MultiDoc2VecFeature.similarityParser.serializeIfChanged()
        
        # Manage the shape of results :
        parsedResult = []
        for i in range(len(results[0])):
            currentFeatures = []
            for u in range(len(results)):
                currentFeatures += results[u][i]
            parsedResult.append(currentFeatures)
        
        tt.toc("Getting features done for the current set.")
        
        # Return the result :
        return parsedResult
    
    def compute(self, config):
        if self.randomFolderd2vBrown:
            # Find all d2v and shuffle :
            fileModelList = sortedGlob("~/d2vbrown/doc2vec_model_*.bin")
            random.shuffle(fileModelList)
            
            # Remove extension and the beginning :
            for i in range(len(fileModelList)):
                current = fileModelList[i]
                current = current[len("~/d2vbrown/doc2vec_model"):]
                current = re.sub('\.bin$', '', current)
                fileModelList[i] = current
            
            
            print "There are " + str(len(fileModelList)) + " models."
            
            thereIsOne = False
            
            for currentFileId in fileModelList:
                config = OrderedDict(config.items() + fileIdToConfig(currentFileId).items())
                scoreTypeAndFeatures = configToCollectionName(config)
                print scoreTypeAndFeatures
                self.d2vMongo = MongoD2VScore(version=1, scoreTypeAndFeatures=scoreTypeAndFeatures)
                if not self.d2vMongo.exists(config):
                    thereIsOne = True
                    print "This fileId will be stored in mongo db :"
                    print currentFileId
                    break
                else:
                    print "This fileId is already in d2vscore mongo db :"
                    print currentFileId
            
            if not thereIsOne:
                print "all already in mongo_db..."
                exit()
            
            print "Starting this config"
            print listToStr(config)
            
                
        # Data and dataPart coherence :
        if "Doc2VecFeature.data.dataPart" in config and config['Doc2VecFeature.data.dataPart'] == 0.0:
            config['Doc2VecFeature.data'] = "stsall"
        if "Doc2VecFeature.data.dataPart" in config and config['Doc2VecFeature.data'] == "stsall":
            config['Doc2VecFeature.data.dataPart'] = 0.0
        
        # We create the score saver :
        if self.saveD2vScore:
            scoreTypeAndFeatures = configToCollectionName(config)
            print scoreTypeAndFeatures
            self.d2vMongo = MongoD2VScore(version=1, scoreTypeAndFeatures=scoreTypeAndFeatures)
            if self.d2vMongo.exists(config):
                print "This config already exists"
                return self.d2vMongo.getFirstScore(config)
            else:
                print "This config is not yet in the database"
        
        # We create the multid2v score saver :
        multiD2vPost = dict()
        md2vCollection = None
        
        if self.saveMultiD2vScore:
            scoreTypeAndFeatures = configToCollectionName(config)
            print scoreTypeAndFeatures
            
            multiD2vScoreDbName = "multid2vscore"
            multiD2vPost["dbNameSource"] = self.multiD2vDbNameSource
            multiD2vPost["collectionNameSource"] = self.multiD2vCollectionNameSource
            multiD2vPost["fileIdSet"] = config["MultiDoc2VecFeature.fileIdSet"]
            multiD2vPost["notEqualsParams"] = self.multiD2vHierarchicalTop
            if self.multiD2vModelType == "random":
                multiD2vPost["notEqualsParamsStr"] = None
                multiD2vPost["type"] = "random"
            elif self.multiD2vModelType == "topdef":
                multiD2vPost["notEqualsParamsStr"] = Graph.notEqualsParamToStr(self.multiD2vHierarchicalTop)
                multiD2vPost["type"] = "topdef" # or "topdelta"
            elif self.multiD2vModelType == "topdelta":
                multiD2vPost["type"] = "topdelta"
                multiD2vPost["notEqualsParamsStr"] = None
                multiD2vPost["topdeltaParameters"] = configToTopdeltaDict(config)
                multiD2vPost["topdeltaParametersStr"] = str(multiD2vPost["topdeltaParameters"])
                
                # Set the fileIdSet :
                m = MongoMultiD2VSerieFusion(maxTopDelta=config["MultiDoc2VecFeature.topdelta.maxTopDelta"], **configToTopdeltaDict(config))
                config["MultiDoc2VecFeature.fileIdSet"] = m.getTopDeltaFusion()
                multiD2vPost["fileIdSet"] = config["MultiDoc2VecFeature.fileIdSet"]
            
            multiD2vPost["lastFileId"] = config["MultiDoc2VecFeature.fileIdSet"][-1]
            multiD2vPost["count"] = len(config["MultiDoc2VecFeature.fileIdSet"])
            
            version = 4
            md2vClient = MongoClient()
            md2vDb = md2vClient[multiD2vScoreDbName]
            md2vCollection = md2vDb[scoreTypeAndFeatures + "-" + str(version)]
            
#             cursor = md2vCollection.find({})
#             for current in cursor:
#                 print current
            
            
            if self.multiD2vModelType == "random":
                for currentRow in md2vCollection.find({"count": multiD2vPost["count"]}):
                    equals = True
                    u = 0
                    for currentFileId in currentRow["fileIdSet"]:
                        fileIdSetToCompare = multiD2vPost["fileIdSet"][u]
                        if fileIdSetToCompare != currentFileId:
                            equals = False
                            break
                        u += 1
                    if equals:
                        print "----------> MultiDoc2Vec already computed and stored in mongo-db."
                        return currentRow["score"]
                    
                print "Starting multi-doc2vec"                    
            elif self.multiD2vModelType == "topdef":
                multiD2vRow = md2vCollection.find_one({"notEqualsParamsStr": multiD2vPost["notEqualsParamsStr"], "count": multiD2vPost["count"]})
                if multiD2vRow is not None:
                    print "MultiDoc2Vec already computed and stored in mongo-db."
                    return multiD2vRow["score"]
                else:
                    print "Starting multi-doc2vec"
            elif self.multiD2vModelType == "topdelta":
                multiD2vRow = md2vCollection.find_one({"topdeltaParametersStr": multiD2vPost["topdeltaParametersStr"], "count": multiD2vPost["count"]})
                if multiD2vRow is not None:
                    print "MultiDoc2Vec topdelta already computed and stored in mongo-db:"
                    print listToStr(config)
                    return multiD2vRow["score"]
                else:
                    print "Starting topdelta multi-doc2vec"
        

        # Memory manageer :
        if self.autoManageMemory:
            self.manageMemory(config)
            
        # qualitative analysis :
        qualitativeAnalysis = False
        if self.qualitativeAnalysis and config['data'] == 'CrossValidation2017' and config['data.partsCount'] == 3:
            qualitativeAnalysis = True
        
        # If there is a problem about the config, return None :
        if not self.init(config):
            print "Combinason not possible."
            return None
        
        tt = TicToc()
        tt.tic("Compute pearson correlation of:\n" + listToStr(config))
        
#         if not stout():
#             exit()
        
        if self.trainingSets is None and self.testSets is None:
        
            trainingSets = []
            testSets = []
            
            agParserParams = {"removeStopWords": config["agParser.removeStopWords"],
                              "toLowerCase": config["agParser.toLowerCase"],
                              "removePunct": config["agParser.removePunct"],
                              "lemma": config["agParser.lemma"]}
            
            if "NormalSets" in config['data']:
                if "2016" in config['data']:
                    (_, testSets) = hmTrainTestMapping(agParserParams=agParserParams)
                    trainingSets += [self.hmTrain] * len(testSets)
                    realCount =  13171
                    assert(len(testSets) == 5)
#                     assert len(self.hmTrain.items()) == realCount
                elif "2015" in config['data']:
                    (_, testSets) = hmTrainTestMapping(mapping=allMapping2015,
                                                       folderRegex=r".*2015.*",
                                                       agParserParams=agParserParams)
                    trainingSets += [self.hmTrain] * len(testSets)
                    realCount = 10179
                    assert(len(testSets) == 5)
                    # assert len(self.hmTrain.items()) == realCount
                else:
                    raise NotImplementedError
            elif "SamsungPolandMappingSets" in config['data']:
                if "2016" in config['data']:
                    (trainingSets, testSets) = hmTrainTestMapping(agParserParams=agParserParams)
                    assert(len(testSets) == 5)
                    assert(len(trainingSets) == 5)
                else:
                    raise NotImplementedError
            elif "DLSMappingSets" in config['data']:
                if "2015" in config['data']:
                    (trainingSets, testSets) = hmTrainTestMapping(mapping=DLSMapping2015,
                                                                  folderRegex=r".*2015.*",
                                                                  agParserParams=agParserParams)
                    assert(len(testSets) == 5)
                    assert(len(trainingSets) == 5)
#                     for trainingSet in trainingSets:
#                         print len(trainingSet.items())
#                     exit()
                else:
                    raise NotImplementedError
            elif "CrossValidation" in config['data']:
                partsCount = config['data.partsCount']
                (trainingSets, testSets) = crossValidationChunk(self.hmTrain.items(), partsCount)
                for i in range(len(trainingSets)):
                    trainingSets[i] = dict(trainingSets[i])
                for i in range(len(testSets)):
                    testSets[i] = dict(testSets[i])
            elif "FeatureAnalysis2016" in config['data']:
                agParser = AgirreParser(verbose=False, removeStopWords=False, removePunct=False, toLowerCase=False, lemma=False,
                                        setName="deft-news",
                                        setNameTypeYear="test2014")
                hm1 = agParser.loadSTS(folders=dataSelector(AgirreParser.AGIRRE_STS_FOLDERS,
                                        ".*2014.*",))
                
                agParser = AgirreParser(verbose=False, removeStopWords=False, removePunct=False, toLowerCase=False, lemma=False,
                                        setName="deft-forum",
                                        setNameTypeYear="test2014")
                hm2 = agParser.loadSTS(folders=dataSelector(AgirreParser.AGIRRE_STS_FOLDERS,
                                        ".*2014.*",))
                
                agParser = AgirreParser(verbose=False, removeStopWords=False, removePunct=False, toLowerCase=False, lemma=False,
                                        setName="belief",
                                        setNameTypeYear="test2015")
                hm3 = agParser.loadSTS(folders=dataSelector(AgirreParser.AGIRRE_STS_FOLDERS,
                                        ".*2015.*",))


                
                testSets = [hm3]
                
                trainToFusion = [hm1, hm2, hm3]
                trainingSets = dict()
                for current in trainToFusion:
                    if current != testSets[0]:
                        trainingSets = dict(trainingSets.items() + current.items())
                
                
                trainingSets = [trainingSets]

            else:
                trainingSets.append(self.hmTrain)
                testSets.append(self.hmTest)
            
            self.trainingSets = trainingSets
            self.testSets = testSets
        
        meanScore = None
        setsScores = []
        setsSizes = []
        
        allScorePrediction = []
        allScoreTest = []
        
        
        for i in range(len(self.trainingSets)):
            
            # Set the config :
            if "data.featureAnalysis" in config and config["data.featureAnalysis"]:
                currentFeatures = samsungPolandFeatureAnalysis2016[i]
                for key, value in currentFeatures.items():
                    config[key] = value
                print "featureAnalysis config :"
                print listToStr(config)
            
            
#             print "--------------------------------------------"
#             print i
#             print self.w2vModel is None
#             print "--------------------------------------------"
                
            
            hmTrain = self.trainingSets[i]
            hmTest = self.testSets[i]
        
            # get all scores :
            scoresTrain = []
            for sentencePair, (_, _, score) in hmTrain.items():
                scoresTrain.append(score)
            scoresTest = []
            for sentencePair, (_, _, score) in hmTest.items():
                scoresTest.append(score)
            
            # Get all features from the training set :
            trainCacheIndex = i
            if "NormalSets" in config['data']:
                trainCacheIndex = 0
            featureTrain = self.getFeatures(hmTrain, config, cacheId="train"+str(trainCacheIndex))
            print "features done for the current train set with " + str(len(scoresTrain)) + " sentence pairs"
            # Get all features from the test set :
            featureTest = self.getFeatures(hmTest, config, cacheId="test"+str(i))
            print "features done for the current test set with " + str(len(scoresTest)) + " sentence pairs"
            tt.tic("Getting features done.")
            
            # Ridge with cross validation :
            # regresser = linear_model.RidgeCV(alphas = np.arange(0.01, 3, 0.01))
            # regresser = linear_model.Ridge(alpha = config['regresser.alpha'])
            regressor = None
            if 'regressor' not in config or config['regressor'] == "Ridge":
                regressor = linear_model.Ridge(alpha = config['regressor.alpha'], solver="auto")
            elif config['regressor'] == "RidgeCV":
                regressor = linear_model.RidgeCV(alphas = np.arange(0.01, 3, 0.01))
            elif config['regressor'] == "ElasticNet":
                regressor = linear_model.ElasticNet()
            elif config['regressor'] == "Lasso":
                regressor = linear_model.Lasso()
            elif config['regressor'] == "LinearRegression":
                regressor = linear_model.LinearRegression()
            elif "SVR" in config['regressor'] or config['regressor'] == 'KernelRidge':
                    params = dict()
                    for key, value in config.items():
                        if 'regressor.' in key:
                            theKey = key.split('.')[-1]
                            params[theKey] = value
                    if config['regressor'] == "SVR":
                        regressor = SVR(**params)
                    elif config['regressor'] == "LinearSVR":
                        regressor = LinearSVR(**params)
                    elif config['regressor'] == "NuSVR":
                        regressor = NuSVR(**params)
                    elif config['regressor'] == "KernelRidge":
                        regressor = KernelRidge(**params)
            else:
                return None
            
            # Train the model :
            try:
                regressor.fit(featureTrain, scoresTrain)
                tt.tic("Training done.")
            except ValueError:
                print str(ValueError)
                print("Regressor params combinason not possible.")
                return None
            
            # Print alpha if RidgeCV :
            if config['regressor'] == "RidgeCV":
                print "alpha = " + str(regressor.alpha_)
            
            # Predict test set :
            prediction = regressor.predict(featureTest)
            
            # qualitative analysis :
            if qualitativeAnalysis:
                hmItems = hmTest.items()
                for i in range(len(prediction)):
                    (sentencePair, (parsed1, parsed2, score)) = hmItems[i]
                    predictedScore = prediction[i]
                    print sentencePair.s1
                    print sentencePair.s2
                    print "Golden standard: " + str(score)
                    print "Prediction: " + str(predictedScore)
                    print "Hash: " + "sts_" + strToHashCode(sentencePair.s1)
                    
                    if "Word2VecFeature" in config and config['Word2VecFeature']:
                        w2vFeature = Word2VecFeature(config=config)
                        result = w2vFeature.computeFeature(sentencePair, parsed1=parsed1, parsed2=parsed2, config=config, w2vModel=self.w2vModel)
                        print "Word2Vec similarity: " + str(result)
                    
                    if "Doc2VecFeature" in config and config["Doc2VecFeature"]:
                        d2vFeature = Doc2VecFeature(config=config)
                        result = d2vFeature.computeFeature(sentencePair, config=config, d2vModel=self.d2vModel)
                        print "Doc2Vec similarity: " + str(result)
                    
                    if "SultanAlignerFeature" in config and config["SultanAlignerFeature"]:
                        saFeature = SultanAlignerFeature(config=config)
                        print "Sultan Aligner: " + str(saFeature.parse(sentencePair, sultanAligner=self.sultanAligner))
                        # print "Sultant Aligner: " + str(self.sultanAligner.getAlignmentScore1(sentencePair))
                    print "\n\n"
                    if (stout() and i > 60) or (not stout() and i % 500 == 0):
                        raw_input('Press any key to continue...')
            
            # print featureTest
                
            # Normalize between 0 and 1 (useless because the perl script do this) :
            prediction = normalizeVector(prediction)
            
            score = 0.0
            
            if 'score' not in config or config['score'] == "NumpyPearsonCorrelation":
                # Print the pearson correlation :
                score = getNumpyPearsonCorrelation(prediction, scoresTest)
                print "Numpy Pearson correlation: " + str(score)
            elif config['score'] == "ScipyPearsonCorrelation":
                score = getScipyPearsonCorrelation(prediction, scoresTest)
                print "Scipy Pearson correlation: " + str(score)
            elif config['score'] == "AgirrePearsonCorrelation":
                score = getAgirrePearsonCorrelation(prediction, scoresTest)
                print "Agirre Pearson correlation: " + str(score)
            elif config['score'] == "MeanLeastSquares":
                # Least square :
                score = getMeanLeastSquares(prediction, scoresTest)
                print "Mean Least square: " + str(score)
            elif config['score'] == "MeanDifference":
                # Mean difference :
                score = getMeanDifference(prediction, scoresTest)
                print "Mean difference: " + str(score)
            
            if meanScore is None:
                meanScore = score
            else:
                meanScore += score
            
            setsScores.append(score)
            setsSizes.append(len(scoresTest))
            
            allScorePrediction += prediction
            allScoreTest += scoresTest
        
        
        
        
        if "Sets" in config["data"] or "Mapping" in config["data"]:
             
            print "setsScores = " + str(setsScores)      
             
            print "setsSizes = " + str(setsSizes)      
                   
            paperSetsSize = []
            if "2015" in config["data"]:
                paperSetsSize = [375, 750, 375, 750, 750]
            elif "2016" in config["data"]:
                paperSetsSize = [254, 249, 230, 244, 209]
            if "data.paperPairsCount" in config and config["data.paperPairsCount"]:
                setsSizes = paperSetsSize
             
            print "paperSetsSize = " + str(paperSetsSize)      
             
            meanScore = 0.0
            for i in range(len(setsScores)):
                meanScore = meanScore + (setsScores[i] * setsSizes[i])
            meanScore = float(meanScore) / sum(setsSizes)
             
             
        else:
            meanScore = meanScore / float(len(setsScores))
        
        assert len(setsScores) == len(self.trainingSets)
        
        # Print the score :
        if 'score' not in config:
            print "Score: " + str(meanScore)
        else:
            print "Mean " + config['score'] + ": " + str(meanScore)
        
#         newAllScorePrediction = []
#         for current in allScorePrediction:
#             newAllScorePrediction.append(truncateFloat(current, 3))
#         allScorePrediction = newAllScorePrediction
#         
#         newAllScoreTest = []
#         for current in allScoreTest:
#             newAllScoreTest.append(truncateFloat(current, 3))
#         allScoreTest = newAllScoreTest
        
#         print allScorePrediction
#         print allScoreTest
        
        systemId = "2"
          
        with open(getWorkingDirectory(__file__) + "/significancetestdata_" + systemId + ".py", "w") as f:
            f.write("goldenStandard = " + str(allScoreTest) + "\n")
            f.write("s" + systemId + "Score = " + str(meanScore) + "\n")
            f.write("s" + systemId + "Prediction = " + str(allScorePrediction) + "\n")
         
        
        # Print the total duration :
        tt.toc()
        
        if self.saveD2vScore and stout():
            self.d2vMongo.addScore(meanScore, config)
            self.d2vMongoAddCount += 1
            print "d2v score added in mongodb"
        
        if self.saveMultiD2vScore:
            multiD2vPost["score"] = meanScore
            md2vCollection.insert_one(multiD2vPost)
#             print "Sauvegarde ANNULEE, à remettre... remettre aussi le shuffle"
            print "multid2v score added in mongodb"
            
            
            
            
        
        return meanScore


############################################################
#################### OPTIMIZATION ##########################
############################################################

def setData(parameters, feature, data):
    if not stout():
        for param in parameters:
            if param['name'] == feature:
                for subparam in param['subparams']:
                    if subparam['name'] == 'data':
                        # subparam['force'] = ['brown_stsall', 'brown', 'stsall', 'ststrain']
                        subparam['force'] = [data]

def start():
    tt = TicToc()
    tt.tic("Starting the optimization...")
    
    parametersId = "bestCombsDef"
#     parametersId = "regressorCombsDef"
#     parametersId = "d2vBrownCombsDef"
#     parametersId = "multiDoc2VecCombsDef"
#     parametersId = "alignementCombsDef"
#     parametersId = "sets2016CombsDef"
#     parametersId = "d2vVsW2vCombsDef"
#     parametersId = "randomFolderd2vBrownCombsDef"


    parameters = ""
    if parametersId == "d2vBrownCombsDef":
        parameters = d2vBrownCombsDef
    elif parametersId == "bestCombsDef":
        parameters = bestCombsDef
    elif parametersId == "multiDoc2VecCombsDef":
        parameters = multiDoc2VecCombsDef
    elif parametersId == "alignementCombsDef":
        parameters = alignementCombsDef
    elif parametersId == "sets2016CombsDef":
        parameters = sets2016CombsDef
    elif parametersId == "d2vVsW2vCombsDef":
        parameters = d2vVsW2vCombsDef
    elif parametersId == "randomFolderd2vBrownCombsDef":
        parameters = randomFolderd2vBrownCombsDef
    
    
    addSMT2013 = getDomain(parameters, "data.addSMT2013")
    if addSMT2013 is not None and len(addSMT2013) == 1 and addSMT2013[0]:
        AgirreParser.defaultAddSMT2013 = True
    
    # We change d2v and w2v datas if not stout :
#     if not stout():
#         setData(parameters, 'Doc2VecFeature', 'brown')
#         setData(parameters, 'Word2VecFeature', 'brown_stsall')

    multiD2vHierarchicalTop = None
    multiD2vModelType = "topdelta"
    multiD2vDbNameSource = "d2vscore-archive14"
    multiD2vCollectionNameSource = "pc-lf-cv2016"
    if parametersId == "multiDoc2VecCombsDef":
        if multiD2vModelType == "random":
            multiD2vHierarchicalTop = None
            multiD2vCollectionNameSource = None
            multiD2vDbNameSource = None
            multiD2vTopNEO = getRandomD2vFileIdList(count=60)
                        
            client = MongoClient()
            db = client["multid2vscore"]
            collection = db["pc-lf-saf-cv2016-3"]
            
            # randomList = list(collection.find({"count": 60, "type": "random"}))
            randomListSorted = list(collection.find({"count": 179, "type": "random"}, sort=[("score", -1)]))
            multiD2vTopNEO = randomListSorted[0]["fileIdSet"] + multiD2vTopNEO

            print listToStr(multiD2vTopNEO)
            print len(multiD2vTopNEO)
            
        elif multiD2vModelType == "topdef":
            multiD2vHierarchicalTop = \
            [
                { "fieldList": ["removePunct", "dataPart"], "max": 10, "minDiff": None, "jump": False },
                { "fieldList": ["removeStopWords", "removePunct", "lemma", "toLowerCase"], "max": 4, "minDiff": None, "jump": True },
                { "fieldList": ["dataPart", "negative"], "max": 5, "minDiff": [0.15, 2], "jump": True },
                { "fieldList": ["min_count"], "max": 8, "minDiff": None, "jump": True },
                { "fieldList": ["size", "window"], "max": 50, "minDiff": None, "jump": True },
            ]


            # We update the parameters:
            scores = MongoD2VScore(dbId=multiD2vDbNameSource, scoreTypeAndFeatures=multiD2vCollectionNameSource)
            g = Graph(scores.toDataFrame())
            multiD2vTopNEO = g.topHierarchNotEqualsOn(multiD2vHierarchicalTop, outType=TopOutTypeEnum.LIST_STRING, max=90)
        
        elif multiD2vModelType == "topdelta":
            editParameters(parameters, "MultiDoc2VecFeature.topdelta", [True])
            multiD2vTopNEO = [[]]
        
        # Data :
#         editParameters(parameters, "data", ["CrossValidation2016"])
#         editParameters(parameters, "data", ["Normal2016"])
        editParameters(parameters, "data", ["Normal2015"])
#         editParameters(parameters, "data", ["SamsungPolandMappingSets2016"])

        print "Starting multiD2v on:"
        print str(multiD2vHierarchicalTop)
        print len(multiD2vTopNEO)
        
        
        multiD2vTopcombinasons = []
        for i in range(len(multiD2vTopNEO)):
            multiD2vTopcombinasons.append(multiD2vTopNEO[:i+1])

#         if not stout():
#             newMultiD2vTopcombinasons = []
#             for currentCombinasons in multiD2vTopcombinasons:
#                 newCurrentCombinasons = []
#                 for currentString in currentCombinasons:
#                     currentString = re.sub(r"part.*$", "part0.001", currentString)
#                     newCurrentCombinasons.append(currentString)
#                 newMultiD2vTopcombinasons.append(newCurrentCombinasons)
#             multiD2vTopcombinasons = newMultiD2vTopcombinasons
                 
        editParameters(parameters, "MultiDoc2VecFeature.fileIdSet", multiD2vTopcombinasons)
#         print listToStr(parameters)

    
    # Init the sts regresser :
    memoryUsageMax = 80.0 # 40.0
    if parametersId == "d2vBrownCombsDef":
        memoryUsageMax = 30.0 # 40.0
    elif parametersId == "multiDoc2VecCombsDef":
        memoryUsageMax = 92.0
    if not stout():
        memoryUsageMax = 90.0
    
    featureAblationMod = False
    if featureAblationMod:
        print "------- WARNING ------- featureAblationMod"
    
    # Init of the regressor:
    stsRegressor = STSRegresser \
    (
        memoryUsageMax=memoryUsageMax,
        qualitativeAnalysis=False,
        featureAblationMod=featureAblationMod,
        saveD2vScore=(parametersId == "d2vBrownCombsDef" or parametersId == "randomFolderd2vBrownCombsDef"),
        saveD2vModels=(not (parametersId == "d2vBrownCombsDef" or parametersId == "randomFolderd2vBrownCombsDef")),
        saveMultiD2vScore=(parametersId == "multiDoc2VecCombsDef"),
        multiD2vHierarchicalTop=multiD2vHierarchicalTop,
        multiD2vModelType=multiD2vModelType,
        multiD2vDbNameSource=multiD2vDbNameSource,
        multiD2vCollectionNameSource=multiD2vCollectionNameSource,
        randomFolderd2vBrown=(parametersId == "randomFolderd2vBrownCombsDef")
    )
    
    # Init the optimizer :
    optimizer = HierarchicalSearch \
    (
        parameters,
        stsRegressor.compute,
        validators=[d2vValidator],
        shuffle=(parametersId == "d2vBrownCombsDef" or (parametersId == "multiDoc2VecCombsDef")) # and multiD2vModelType != "topdelta"
    )
    
    # Optimize :
    (best, results) = optimizer.optimize()
    top10 = optimizer.getTop(results, 10)
    # top5 = optimizer.getTop(results, 5)
    
    # stsRegressor.sultanAligner.alignmentParser.serialize()
    
    
    # Print all :
    # if len(results) < 10:
    if parametersId != "multiDoc2VecCombsDef":
        print "-------------------------- PARAMETERS --------------------------"
#         print listToStr(parameters)
#         if parametersId == "d2vBrownCombsDef":
#             print "-------------------------- ALL DOC2VEC --------------------------"
#             for current in results:
#                 print str(current[1]) + "\t" + configToFileId(current[0])
#         if len(best) < 10 or parametersId == "d2vBrownCombsDef":
#             print "-------------------------- ALL --------------------------"
#             for current in results:
#                 print "Score " + str(current[1]) + " for:"
#                 print listToStr(current[0])
        # Print all best configs :
#         if len(best) < 10:
#             print "-------------------------- BEST --------------------------"
#             for current in best:
#                 print "Score " + str(current[1]) + " for:"
#                 print listToStr(current[0])
        # Print top
        print "-------------------------- TOP --------------------------"
        for current in top10:
            print "Score " + str(current[1]) + " for:"
            print listToStr(current[0])
        # Top regressors :
#         print "-------------------------- TOP REGRESSOR --------------------------"
#         for current in top10:
#             print "Score " + str(current[1]) + " for:"
#             print current[0]["regressor"]
        # Top doc2vec :
        print "-------------------------- TOP DOC2VEC --------------------------"
        if getDomain(parameters, "Doc2VecFeature")[0] == True and (parametersId == "d2vBrownCombsDef" or parametersId == "d2vVsW2vCombsDef"):
            for current in top10:
                print "Score " + str(current[1]) + " for:"
                print configToFileId(current[0])
        tt.tic("Optimization done.")
    
    if stout():
        # Save combinasons done for d2vbrown :
        if parametersId == "d2vBrownCombsDef" and stsRegressor.d2vMongoAddCount > 0:
            mongoCombs = MongoD2VCombinason()
            mongoCombs.addCombinason(parameters, top10, best, results)
            tt.tic("Combinason added to MongoDB.")
        
    tt.toc()


if __name__ == '__main__':
    start()

