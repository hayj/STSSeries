# coding: utf-8

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
from sts.baroniembedding import *
import sys
import gc
from pymongo import MongoClient

############################################################
######################## FEATURES ##########################
############################################################
class MultiDoc2VecFeature(Feature):
    
    sentencePairCount = 0
    
    similarityParser = None
    
    bestTopDeltaCache = dict()
    
    @staticmethod
    def getFeatureHashConfig(config):
        hash = Feature.getNormalHashFeature(MultiDoc2VecFeature, config)
        return hash
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        if MultiDoc2VecFeature.similarityParser is None:
            MultiDoc2VecFeature.similarityParser = SerializableParser(autoSerialize=False, fileId="multidoc2vecfeature_similarity_v1", verbose=False)

        config = kwargs["config"]
        manageMemoryFunct = kwargs["manageMemoryFunct"]
        updateD2vModelFunct = kwargs["updateD2vModelFunct"]
        
        fileIdSet = []
        
        
        if 'MultiDoc2VecFeature.bestTopDelta' in config and \
            config['MultiDoc2VecFeature.bestTopDelta']:
            config['MultiDoc2VecFeature.fileIdSet'] = []
            assert len(config['MultiDoc2VecFeature.fileIdSet']) == 0
#                 or (len(config['MultiDoc2VecFeature.fileIdSet']) == 1 and \
#                      len(config['MultiDoc2VecFeature.fileIdSet'][0]) == 0)
            interval = config['MultiDoc2VecFeature.bestTopDelta.interval']
            intervalStr = str(interval)
            if intervalStr in MultiDoc2VecFeature.bestTopDeltaCache:
                bestTopDeltaFileIdSet = MultiDoc2VecFeature.bestTopDeltaCache[intervalStr]
                fileIdSet += bestTopDeltaFileIdSet
            else:
                scoreTypeAndFeatures = "pc-lf-saf-cv2016"
    #                 scoreTypeAndFeatures = configToCollectionName(config)
                multiD2vScoreDbName = "multid2vscore"
                version = 3
                md2vClient = MongoClient()
                md2vDb = md2vClient[multiD2vScoreDbName]
                md2vCollection = md2vDb[scoreTypeAndFeatures + "-" + str(version)]
                
                # _s726 le dernier fileId pour entre 48 et 52
                bestTopDeltaInterval = md2vCollection.find_one(
                                    {"count": {"$gte": interval[0], "$lte": interval[1]},
                                     "type": "topdelta"},
                                    sort=[("score", -1)])
                bestTopDeltaFileIdSet = bestTopDeltaInterval["fileIdSet"]
                fileIdSet += bestTopDeltaFileIdSet
                MultiDoc2VecFeature.bestTopDeltaCache[intervalStr] = bestTopDeltaFileIdSet
                print "bestTopDeltaInterval:\n" + listToStr(bestTopDeltaFileIdSet)
                assert len(fileIdSet) > 0
        
        fileIdSet += config['MultiDoc2VecFeature.fileIdSet']
        if 'MultiDoc2VecFeature.fileIdAddOn' in config and \
            config['MultiDoc2VecFeature.fileIdAddOn']:
            fileIdSet = config['MultiDoc2VecFeature.fileIdAddOn.first'] \
                        + fileIdSet \
                        + config['MultiDoc2VecFeature.fileIdAddOn.end']
        
        # config['MultiDoc2VecFeature.fileIdSet'] = fileIdSet
        
        
        currentFeatures = []
        fileIdIteration = 0
        for fileId in fileIdSet:
            
            simiDescription =  fileId + \
                               str(config['MultiDoc2VecFeature.d2vSimilarity']) + \
                               str(config.get('MultiDoc2VecFeature.d2vSimilarity.defaultSimilarity')) + \
                               str(config.get('MultiDoc2VecFeature.vector.firstFileIdCount')) + \
                               str(config.get('MultiDoc2VecFeature.vector.substraction')) + \
                               str(config.get('MultiDoc2VecFeature.vector.full')) + \
                               str(config['MultiDoc2VecFeature.vector']) + \
                               str(sentencePair)
            
            hashSimilarity = strToHashCode(simiDescription)
                        
            # print hashSimilarity
            currentParseResult = MultiDoc2VecFeature.similarityParser.parse \
            (
                hashSimilarity,
                self.parseFunct,
                config=config,
                fileId=fileId,
                sentencePair=sentencePair,
                manageMemoryFunct=manageMemoryFunct,
                updateD2vModelFunct=updateD2vModelFunct,
                fileIdIteration=fileIdIteration,
             )
            

            currentFeatures += currentParseResult
            
            fileIdIteration += 1
        

        
        return currentFeatures
    
    def parseFunct(self, hashSimilarity,
                   config=None,
                   fileId=None,
                   sentencePair=None,
                   manageMemoryFunct=None,
                   updateD2vModelFunct=None,
                   fileIdIteration=None):
        id1 = 'sts_' + text.strToHashCode(sentencePair.s1)
        id2 = 'sts_' + text.strToHashCode(sentencePair.s2)
        currentFeatures = []
        # WARNING, to pass to updateD2vModelFunct if want to train any d2v model :
        # swList = parsingStringToSwList(fileId)
        d2vConfig = fileIdToConfig(fileId)
        # d2vConfig = dict(d2vConfig.items() + parsingStringToParsingConfig(fileId).items())
        manageMemoryFunct(d2vConfig)
        d2vModel = updateD2vModelFunct(d2vConfig, fileId=fileId)
        if config['MultiDoc2VecFeature.d2vSimilarity']:
            d2vSimilarity = config['MultiDoc2VecFeature.d2vSimilarity.defaultSimilarity']
            if (id1 in d2vModel.docvecs) and (id2 in d2vModel.docvecs):
                d2vSimilarity = d2vModel.docvecs.similarity(id1, id2)
                assert isinstance(d2vSimilarity, float)
            currentFeatures.append(d2vSimilarity)
        if config['MultiDoc2VecFeature.vector']:
            if fileIdIteration < config['MultiDoc2VecFeature.vector.firstFileIdCount']:
                if id1 in d2vModel.docvecs:
                    v1 = d2vModel.docvecs[id1]
                else:
                    v1 = np.zeros(len(d2vModel["man"]))
                if id2 in d2vModel.docvecs:
                    v2 = d2vModel.docvecs[id2]
                else:
                    v2 = np.zeros(len(d2vModel["man"]))
                
                assert  config['MultiDoc2VecFeature.vector.substraction'] or \
                        config['MultiDoc2VecFeature.vector.full']
                if config['MultiDoc2VecFeature.vector.substraction']:
                    currentFeatures = np.append(currentFeatures, v1 - v2)
                if config['MultiDoc2VecFeature.vector.full']:
                    currentFeatures = np.append(currentFeatures, v1)
                    currentFeatures = np.append(currentFeatures, v2)
                currentFeatures = currentFeatures.tolist()
        
        return currentFeatures 



class Doc2VecFeature(Feature):
    @staticmethod
    def getFeatureHashConfig(config):
        hashConfig = []
        for key, value in config.items():
            if "Doc2VecFeature" in key and 'Multi' not in key:
                hashConfig.append(key + str(value))
        hashConfig = strToHashCode(listToStr(hashConfig))
        return str(Doc2VecFeature.__name__.lower()) + "_" + hashConfig
    
    @staticmethod
    def getDataHashConfig(config):
        dataConfig = config.copy()
        dataConfig.pop('Doc2VecFeature.d2vSimilarity.defaultSimilarity', None)
        dataConfig.pop('Doc2VecFeature.d2vSimilarity', None)
        dataConfig.pop('Doc2VecFeature.vector', None)
        return Doc2VecFeature.getFeatureHashConfig(dataConfig)
    
    
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        # doc2vec :
        d2vModel = kwargs["d2vModel"]
        config = kwargs["config"]
        ## If sentence already in the train :
        if d2vModel is None:
            return []
        id1 = 'sts_' + text.strToHashCode(sentencePair.s1)
        id2 = 'sts_' + text.strToHashCode(sentencePair.s2)
        
        currentFeatures = []
        
        if config['Doc2VecFeature.d2vSimilarity']:
            d2vSimilarity = config['Doc2VecFeature.d2vSimilarity.defaultSimilarity']
            if (id1 in d2vModel.docvecs) and (id2 in d2vModel.docvecs):
                d2vSimilarity = d2vModel.docvecs.similarity(id1, id2)
            currentFeatures.append(d2vSimilarity)
        if config['Doc2VecFeature.vector']:
            currentFeatures = np.append(currentFeatures, d2vModel.docvecs[id1])
            currentFeatures = np.append(currentFeatures, d2vModel.docvecs[id2])
            currentFeatures = currentFeatures.tolist()
        return currentFeatures   
            

class SultanAlignerFeature(Feature):
    @staticmethod
    def getFeatureHashConfig(config):
        hash = Feature.getNormalHashFeature(SultanAlignerFeature, config)
        return hash
    
    def needInit(self):
        return False

    def initParsing(self, *args, **kwargs):
        config = kwargs["config"]
        sultanAligner = kwargs["sultanAligner"]
        return None
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        sultanAligner = kwargs["sultanAligner"]
        config = kwargs["config"]
        f = []
        for simName, funct in  [
                                   ("similarity1", sultanAligner.getAlignmentScore1),
                                   ("similarity2", sultanAligner.getAlignmentScore2),
                                   ("similarity3", sultanAligner.getAlignmentScore3),
                               ]:
            if config["SultanAlignerFeature." + simName]:
                for currentParsingString in config["SultanAlignerFeature.parsingConfigs"]:
                    if "isDLS2015SwOrPunct2" in currentParsingString:
                        swList = "isDLS2015SwOrPunct2"
                    elif "isDLS2015SwOrPunct1" in currentParsingString:
                        swList = "isDLS2015SwOrPunct1"
                    else:
                        swList = parsingStringToSwList(currentParsingString)
                    alignmentScore = funct(sentencePair, swList)
                    f.append(alignmentScore)
        
        if config["SultanAlignerFeature.targetedAlignment"]:
            sultanAligner.loadStanfordParser()
            # if config["SultanAlignerFeature.targetedAlignment.namedEntities"]:
            alignmentScore = sultanAligner.getAlignmentNamedEntities \
            (
                sentencePair,
                config=config
            )
                
            if isinstance(alignmentScore, list):
                f += alignmentScore
            else:
                f.append(alignmentScore)
        return f

class RandomFeature(Feature):
    def computeFeature(self, sentencePair, *args, **kwargs):
        return [random.random()]

class Word2VecFeature(Feature):
    @staticmethod
    def getFeatureHashConfig(config):
        hash = Feature.getNormalHashFeature(Word2VecFeature, config)
        return hash
    
    def needInit(self):
        return True
    
    def initParsing(self, *args, **kwargs):
        config = kwargs["config"]
        stsRegressor = kwargs["stsRegressor"]
        w2vModel = stsRegressor.updateW2vModel(config)
        currentAGParser = AgirreParser(verbose=False,
                                       removeStopWords=config['Word2VecFeature.data.removeStopWords'],
                                       removePunct=config['Word2VecFeature.data.removePunct'],
                                       toLowerCase=config['Word2VecFeature.data.toLowerCase'],
                                       lemma=config['Word2VecFeature.data.lemma'])
        w2vSTS = currentAGParser.loadSTS()
        return (w2vSTS, w2vModel)
        
    
    @staticmethod
    def getDataHashConfig(config):
        dataConfig = dict(config.items())
        dataConfig.pop('Word2VecFeature.w2vNSimilarity.defaultSimilarity', None)
        dataConfig.pop('Word2VecFeature.w2vNSimilarity', None)
        dataConfig.pop('Word2VecFeature.homeMadeSimilarity', None)
        dataConfig.pop('Word2VecFeature.vector', None)
        if dataConfig['Word2VecFeature.data'] == "GoogleNews":
            dataConfig.pop('Word2VecFeature.data.removePunct', None)
            dataConfig.pop('Word2VecFeature.data.removeStopWords', None)
            dataConfig.pop('Word2VecFeature.data.lemma', None)
            dataConfig.pop('Word2VecFeature.data.toLowerCase', None)
        return Word2VecFeature.getFeatureHashConfig(dataConfig)
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        # Get params :
        currentFeatures = []
        (w2vSTS, w2vModel) = kwargs["initParsingResult"]
        parsed1, parsed2, _ = w2vSTS[sentencePair]
        
#         print parsed1
#         print parsed2
#         print sentencePair
        
        config = kwargs["config"]
        if w2vModel is None:
            return []
        # Cosine similarity between the 2 centroid vectors from Word2Vec :
        if config['Word2VecFeature.homeMadeSimilarity']:
            print 'TODO this is a cosine distance, not a cosine similarity'
            exit()
            centroid1 = self.getSentenceCentroid(parsed1, w2vModel)
            centroid2 = self.getSentenceCentroid(parsed2, w2vModel)
            similarity = spatial.distance.cosine(centroid1, centroid2)
            currentFeatures.append(similarity)
        # The word2vec n_similarity :
        if config['Word2VecFeature.w2vNSimilarity']:
            w2vParsed1 = [word for word in parsed1 if word in w2vModel.vocab]
            w2vParsed2 = [word for word in parsed2 if word in w2vModel.vocab]
            w2vSimilarity = config['Word2VecFeature.w2vNSimilarity.defaultSimilarity']
            if (len(w2vParsed1) > 0) and (len(w2vParsed2) > 0):
                w2vSimilarity = w2vModel.n_similarity(w2vParsed1, w2vParsed2)
            currentFeatures.append(w2vSimilarity)
        # Vector as a feature :
        if config['Word2VecFeature.vector']:
            print 'TODO getSentenceCentroid is not good'
            exit()
            centroid1 = self.getSentenceCentroid(parsed1, w2vModel)
            centroid2 = self.getSentenceCentroid(parsed2, w2vModel)            
            currentFeatures = np.append(currentFeatures, centroid1)
            currentFeatures = np.append(currentFeatures, centroid2)
            currentFeatures = currentFeatures.tolist()
        
        return currentFeatures

    def getSentenceCentroid(self, sentence, w2vModel):
        # np.ones because in these 2 sentences [u'two', u'zebras', u'playing'] and [u'zebras', u'socializing'],
        # The second one has only out-of-vocabulary words, and consine similarity can't be calculated with zeros.
        centroid = np.ones(len(w2vModel["man"]))
        oovCount = 0
        for word in sentence:
            if word in w2vModel.vocab:
                centroid = np.add(centroid, w2vModel[word])
            else:
                oovCount += 1 
        if len(sentence) - oovCount > 0:
            centroid = np.divide(centroid, len(sentence) - oovCount)
        return centroid


class LengthFeature(Feature):
    @staticmethod
    def getFeatureHashConfig(config):
        """
        The init method make a specifique hash for the stored file according
        to the config
        """
        hashConfig = []
        for key, value in config.items():
            if "agParser" in key or "LengthFeature" in key:
                hashConfig.append(key + str(value))
        hashConfig = strToHashCode(listToStr(hashConfig))
        return str(LengthFeature.__name__.lower()) + "_" + hashConfig
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        
        # Get params :
        f = []
        parsed1 = kwargs["parsed1"]
        parsed2 = kwargs["parsed2"]
        config = kwargs["config"]
        s1 = sentencePair.s1
        s2 = sentencePair.s2
        
        # List length :
        if config['LengthFeature.tokens']:
            f.append(len(parsed1))
            f.append(len(parsed2))
            f.append(abs(len(parsed1) - len(parsed2)))
         
        # Strings length :
        if config['LengthFeature.string']:
            f.append(len(s1))
            f.append(len(s2))
            f.append(abs(len(s1) - len(s2)))
        
        return f

class SentencePairFeature(Feature):
    @staticmethod
    def getFeatureHashConfig(config):
        hash = Feature.getNormalHashFeature(SentencePairFeature, config)
        return hash

    @staticmethod
    def countOverlap(parsed1, parsed2, ngram):
        if len(parsed1) < ngram or len(parsed2) < ngram:
            return 0
        count = 0
        for i in range(len(parsed1) - (ngram - 1)):
            currentParsed1Ngram = parsed1[i:i + ngram]
            for i in range(len(parsed2) - (ngram - 1)):
                currentParsed2Ngram = parsed2[i:i + ngram]
                if currentParsed1Ngram == currentParsed2Ngram:
                    count += 1
        return count
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        # Get params :
        f = []
        originalSTS = kwargs["originalSTS"]
        loweredSTS = kwargs["loweredSTS"]
        onlyLoweredLemmaSTS = kwargs["onlyLoweredLemmaSTS"]
        
        lemmaLoNpWithoutSwSTS = kwargs["lemmaLoNpWithoutSwSTS"]
        lemmaLoNpWithSwSTS = kwargs["lemmaLoNpWithSwSTS"]
        loNpWithoutSwSTS = kwargs["loNpWithoutSwSTS"]
        loNpWithSwSTS = kwargs["loNpWithSwSTS"]
        
        config = kwargs["config"]
        orParsed1, orParsed2, _ = originalSTS[sentencePair]
        loParsed1, loParsed2, _ = loweredSTS[sentencePair]
        leParsed1, leParsed2, _ = onlyLoweredLemmaSTS[sentencePair]
        
        
        lemmaLoNpWithoutSwParsed1, lemmaLoNpWithoutSwParsed2, _ = lemmaLoNpWithoutSwSTS[sentencePair]
        lemmaLoNpWithSwParsed1, lemmaLoNpWithSwParsed2, _ = lemmaLoNpWithSwSTS[sentencePair]
        loNpWithoutSwParsed1, loNpWithoutSwParsed2, _ = loNpWithoutSwSTS[sentencePair]
        loNpWithSwParsed1, loNpWithSwParsed2, _ = loNpWithSwSTS[sentencePair]
        
        
        
        sameUpperCaseCount = 0
        for word in orParsed1:
            if word.lower() != word:
                if word in orParsed2:
                    sameUpperCaseCount += 1
        
        sameLemmaCount = 0
        for word in leParsed1:
            if word in leParsed2:
                sameLemmaCount += 1
        
        tokenCount = [len(loParsed1), len(loParsed2)]
        punctCount = [0, 0]
        smallsw3Count = [0, 0]
        nltkswCount = [0, 0]
        bigsw1Count = [0, 0]
        
        stringLength = [0, 0]
        punctStringLength = [0, 0]
        smallsw3StringLength = [0, 0]
        bigsw1StringLength = [0, 0]
        nltkswStringLength = [0, 0]
        
        sameCount = 0
        punctSameCount = 0
        smallsw3SameCount = 0
        bigsw1SameCount = 0
        nltkswSameCount = 0
        
        i = 0
        for orParsed in [loParsed1, loParsed2]:
            for word in orParsed:
                stringLength[i] += len(word)
                if i == 0 and word in loParsed2:
                    sameCount += 1
                if not isWord(word):
                    punctCount[i] += 1
                    punctStringLength[i] += 1
                    if i == 0 and word in loParsed2:
                        punctSameCount += 1
                else:
                    if word in StopWord.swDict["smallsw3"]:
                        smallsw3Count[i] += 1
                        smallsw3StringLength[i] += len(word)
                        if i == 0 and word in loParsed2:
                            smallsw3SameCount += 1
                    if word in StopWord.swDict["bigsw1"]:
                        bigsw1Count[i] += 1
                        bigsw1StringLength[i] += len(word)
                        if i == 0 and word in loParsed2:
                            bigsw1SameCount += 1
                    if isStopWord(word):
                        nltkswCount[i] += 1
                        nltkswStringLength[i] += len(word)
                        if i == 0 and word in loParsed2:
                            nltkswSameCount += 1
            i += 1
        
        realTokenCount = list(np.subtract(tokenCount, punctCount))
        realStringLength = list(np.subtract(stringLength, punctStringLength))
        
        if config["SentencePairFeature.nGramOverlap"]:
            grams = []
            if config["SentencePairFeature.nGramOverlap.2gram"]:
                grams.append(2)
            if config["SentencePairFeature.nGramOverlap.3gram"]:
                grams.append(3)
            if config["SentencePairFeature.nGramOverlap.4gram"]:
                grams.append(4)
            if config["SentencePairFeature.nGramOverlap.5gram"]:
                grams.append(5)
            wordType = []
            if config["SentencePairFeature.nGramOverlap.lemma"]:
                wordType.append((lemmaLoNpWithoutSwParsed1, lemmaLoNpWithoutSwParsed2))
            if config["SentencePairFeature.nGramOverlap.word"]:
                wordType.append((loNpWithoutSwParsed1, loNpWithoutSwParsed2))
            if config["SentencePairFeature.nGramOverlap.lemmaWithSw"]:
                wordType.append((lemmaLoNpWithSwParsed1, lemmaLoNpWithSwParsed2))
            if config["SentencePairFeature.nGramOverlap.wordWithSw"]:
                wordType.append((loNpWithSwParsed1, loNpWithSwParsed2))
            for (parsed1, parsed2) in wordType:
                for currentGram in grams:
                    f.append(SentencePairFeature.countOverlap(parsed1, parsed2, currentGram))
        
        if config["SentencePairFeature.sameUpperCaseCount"]:
            f.append(sameUpperCaseCount)
        
        if config["SentencePairFeature.sameLemmaCount"]:
            f.append(sameLemmaCount)
        
        if config["SentencePairFeature.word"]:
            if config["SentencePairFeature.word.tokenCount"]:
                f += realTokenCount
                if config["SentencePairFeature.word.substraction"]:
                    f.append(abs(realTokenCount[0] - realTokenCount[1]))
            if config["SentencePairFeature.word.stringLength"]:
                f += realStringLength
                if config["SentencePairFeature.word.substraction"]:
                    f.append(abs(realStringLength[0] - realStringLength[1]))
            if config["SentencePairFeature.word.sameCount"]:
                f.append(sameCount - punctSameCount)
        
        if config["SentencePairFeature.punct"]:
            if config["SentencePairFeature.punct.tokenCount"]:
                f += punctCount
            if config["SentencePairFeature.punct.sameCount"]:
                f.append(punctSameCount)
        
        if config["SentencePairFeature.stopword"]:
            if config["SentencePairFeature.stopword.smallsw3"]:
                if config["SentencePairFeature.stopword.tokenCount"]:
                    f += list(np.subtract(realTokenCount, smallsw3Count))
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(realTokenCount[0] - realTokenCount[1]))
                if config["SentencePairFeature.stopword.swTokenCount"]:
                    f += smallsw3Count
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(smallsw3Count[0] - smallsw3Count[1]))
                if config["SentencePairFeature.stopword.stringLength"]:
#                     f += list(np.subtract(realStringLength, smallsw3StringLength))
                    f += smallsw3StringLength
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(smallsw3StringLength[0] - smallsw3StringLength[1]))
                if config["SentencePairFeature.stopword.sameCount"]:
                    f.append(smallsw3SameCount)
            
            if config["SentencePairFeature.stopword.bigsw1"]:
                if config["SentencePairFeature.stopword.tokenCount"]:
                    f += list(np.subtract(realTokenCount, bigsw1Count))
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(realTokenCount[0] - realTokenCount[1]))
                if config["SentencePairFeature.stopword.swTokenCount"]:
                    f += bigsw1Count
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(bigsw1Count[0] - bigsw1Count[1]))
                if config["SentencePairFeature.stopword.stringLength"]:
                    f += bigsw1StringLength
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(bigsw1StringLength[0] - bigsw1StringLength[1]))
                if config["SentencePairFeature.stopword.sameCount"]:
                    f.append(bigsw1SameCount)
            
            if config["SentencePairFeature.stopword.nltksw"]:
                if config["SentencePairFeature.stopword.tokenCount"]:
                    f += list(np.subtract(realTokenCount, nltkswCount))
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(realTokenCount[0] - realTokenCount[1]))
                if config["SentencePairFeature.stopword.swTokenCount"]:
                    f += nltkswCount
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(nltkswCount[0] - nltkswCount[1]))
                if config["SentencePairFeature.stopword.stringLength"]:
                    f += nltkswStringLength
                    if config["SentencePairFeature.stopword.substraction"]:
                        f.append(abs(nltkswStringLength[0] - nltkswStringLength[1]))
                if config["SentencePairFeature.stopword.sameCount"]:
                    f.append(nltkswSameCount)
        
        return f


class BaroniVectorsFeature(Feature):
#     sentencePairCount = 0
#     tt = TicToc()
    def needInit(self):
        return True
    
    def initParsing(self, *args, **kwargs):
        config = kwargs["config"]
        
        # Load all STS data :
        baroniSTSList = []
        for currentParsingString in config["BaroniVectorsFeature.parsingConfigs"]:
            if "isDLS2015SwOrPunct" in currentParsingString:
                if "isDLS2015SwOrPunct1" in currentParsingString:
                    dls2015SwPunctList1 = initDls2015SwPunctList1()
                    swList = dls2015SwPunctList1
                else:
                    dls2015SwPunctList2 = initDls2015SwPunctList2()
                    swList = dls2015SwPunctList2
                currentAGParser = AgirreParser(verbose=False,
                                               removeStopWords=True,
                                               removePunct=False,
                                               toLowerCase=("lowercase" in currentParsingString),
                                               lemma=("lemma" in currentParsingString),
                                               swList=swList)
                baroniSTS = currentAGParser.loadSTS()
            else:
                parsingConfig = parsingStringToParsingConfig(currentParsingString)
                swList = parsingStringToSwList(currentParsingString)
                currentAGParser = AgirreParser(verbose=False,
                                               removeStopWords=parsingConfig["removeStopWords"],
                                               removePunct=parsingConfig["removePunct"],
                                               toLowerCase=parsingConfig["toLowerCase"],
                                               lemma=parsingConfig["lemma"],
                                               swList=swList)
                baroniSTS = currentAGParser.loadSTS()
            baroniSTSList.append(baroniSTS)
        
        # Load the model :
        baroniLoader = BaroniLoader()
        # Set the defaultSimilarity of baroni :
        defaultSimilarity = 0.0
        if config["BaroniVectorsFeature.cosinusNSimilarity"]:
            defaultSimilarity = config["BaroniVectorsFeature.cosinusNSimilarity.defaultSimilarity"]
        baroniLoader.defaultSimilarity = defaultSimilarity
        
        return (baroniLoader, baroniSTSList)
    
    @staticmethod
    def getFeatureHashConfig(config):
        hash = Feature.getNormalHashFeature(BaroniVectorsFeature, config)
        return hash
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        

        f = []
        (bl, baroniSTSList) = kwargs["initParsingResult"]
        config = kwargs["config"]
        
        i = 0
        for currentParsingString in config["BaroniVectorsFeature.parsingConfigs"]:
            baroniSTS = baroniSTSList[i]
        
            parsed1, parsed2, _ = baroniSTS[sentencePair]
            
            if config["BaroniVectorsFeature.cosinusNSimilarity"]:
                if config["BaroniVectorsFeature.centroid"]:
                    centroidSim = bl.cosineNSimilarity(parsed1, parsed2,
                                                       aggregationType=BaroniAggregationEnum.CENTROID)   
    #                 print centroidSim             
                    f.append(centroidSim)
                if config["BaroniVectorsFeature.max"]:
                    maxSim = bl.cosineNSimilarity(parsed1, parsed2,
                                                       aggregationType=BaroniAggregationEnum.MAX)
    #                 print maxSim
                    f.append(maxSim)
            if config["BaroniVectorsFeature.vector"]:
                if config["BaroniVectorsFeature.centroid"]:
                    parsedVector1 = bl.getWordsCentroid(parsed1)
                    if parsedVector1 is None:
                        parsedVector1 = [0.0] * bl.vectorSize
                    f += list(parsedVector1)
                    
                    parsedVector2 = bl.getWordsCentroid(parsed2)
                    if parsedVector2 is None:
                        parsedVector2 = [0.0] * bl.vectorSize
                    f += list(parsedVector2)
                if config["BaroniVectorsFeature.max"]:
                    parsedVector1 = bl.getWordsMax(parsed1)
                    if parsedVector1 is None:
                        parsedVector1 = [0.0] * bl.vectorSize
                    f += list(parsedVector1)
                    
                    parsedVector2 = bl.getWordsMax(parsed2)
                    if parsedVector2 is None:
                        parsedVector2 = [0.0] * bl.vectorSize
                    f += list(parsedVector2)
            
            i += 1
                
        return f

class JacanaAlignFeature(Feature):
#     sentencePairCount = 0
#     tt = TicToc()
    
    @staticmethod
    def getFeatureHashConfig(config):
        hash = Feature.getNormalHashFeature(JacanaAlignFeature, config)
        return hash
    
    def initParsing(self, *args, **kwargs):
        config = kwargs["config"]
        hmSTS = kwargs["hmSTS"]
        initParsingResultList = []
        i = 0
        for currentParsingString in config["JacanaAlignFeature.parsingConfigs"]:
            swList = parsingStringToSwList(currentParsingString)
            parsingConfig = parsingStringToParsingConfig(currentParsingString)
                    
            currentAGParser = AgirreParser(verbose=False,
                                           removeStopWords=parsingConfig['removeStopWords'],
                                           removePunct=parsingConfig['removePunct'],
                                           toLowerCase=parsingConfig['toLowerCase'],
                                           lemma=parsingConfig['lemma'],
                                           swList=swList)
            hmSTSJacana = currentAGParser.loadSTS()
            
            
            sentencePairList = []
            parsed1List = []
            parsed2List = []
            for sentencePair, (_, _, _) in hmSTS.items():
                parsed1, parsed2, _ = hmSTSJacana[sentencePair]
                parsed1List.append(parsed1)
                parsed2List.append(parsed2)
                sentencePairList.append(sentencePair)
            initParsingResult = JacanaAlignFeature.getJacanaAlignScore(sentencePairList, parsed1List, parsed2List, config)
            initParsingResultList.append(initParsingResult)
            i += 1
        return initParsingResultList
    
    def computeFeature(self, sentencePair, *args, **kwargs):
        f = []
        config = kwargs["config"]
        initParsingResultList = kwargs["initParsingResult"]
        for initParsingResult in initParsingResultList:
            f.append(initParsingResult[sentencePair])
        return f
    
    def needInit(self):
        return True
    
    # http://stackoverflow.com/questions/2837214/python-popen-command-wait-until-the-command-is-finished
    @staticmethod
    def getJacanaAlignScore(sentencePairList, parsed1List, parsed2List, config):
        path = "~/lib/jacana-align/scripts-align/"
        
        scores = dict()
        
        # remove previous files :
        removeFile(path + "s.txt")
        removeFile(path + "s.json")
        
        # output sentences :
        sentencePairIndexFail = []
        with open(path + "s.txt", "w") as sFile:
            lines = []
            for i in range(len(parsed1List)):
                if len(parsed1List[i]) == 0 or len(parsed2List[i]) == 0:
                    scores[sentencePairList[i]] = config["JacanaAlignFeature.defaultScore"]
                    sentencePairIndexFail.append(i)
                else:
                    line = " ".join(parsed1List[i]) + "\t" + " ".join(parsed2List[i]) + "\n"
                    lines.append(line)
            for line in lines:
                assert isinstance(line, basestring)
                assert len(line) > 2
            sFile.writelines(lines)
        
        # Execute :
        # p = subprocess.Popen(["./alignFile.sh"], stdout=subprocess.PIPE)
        # subprocess.call(["bash", path + "alignFile.sh"], shell=True)
        previousDir = os.getcwd()
        os.chdir(path)
        if stout():
            p = subprocess.Popen(["./alignFileStout.sh"])
        else:
            p = subprocess.Popen(["./alignFile.sh"])
    #     bashOut = p.stdout.readlines()
    #     print listToStr(bashOut)
        p.wait()
        # Read the file :
        print "index fail " + listToStr(sentencePairIndexFail)
        print "len de index fail " + str(len(sentencePairIndexFail))
        with open(path + "s.json", "r") as fp:
            i = 0
            for line in fp:
                while i in sentencePairIndexFail:
                    i += 1
                if '"score": "' in line:
                    try:
                        score = float(re.search('"score": "(.+?)"', line).group(1))
                    except AttributeError:
                        score = None
                    if score is None:
                        print "Parsing error for the Jacana score line"
                    scores[sentencePairList[i]] = score
                    i += 1
            assert i == len(sentencePairList)
        
        os.chdir(previousDir)
        
        return scores
