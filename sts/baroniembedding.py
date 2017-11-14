# coding: utf-8

import gzip
from util.text import listToStr
import numpy as np
from scipy import spatial
from sklearn.metrics.pairwise import cosine_similarity
import math
from itertools import imap
from math import sqrt
from operator import mul
from itertools import izip

class BaroniVectorsEnum():
    (
        BEST_PREDICT,
#         REDUCED_COUNT
    ) = range(1)

class CosineSimilarityEnum():
    (
        HOME_MADE1,
        HOME_MADE2,
#         SKLEARN,
        SCIPY,
#         HOME_MADE3,
#         HOME_MADE4,
    ) = range(3)
    
class BaroniAggregationEnum():
    (
        CENTROID,
        MAX,
    ) = range(2)

baroniVectors = [None] * 3

class BaroniLoader():
    def __init__(self, verbose=False,
                 folder="~/word2vec",
                 vectorsType=BaroniVectorsEnum.BEST_PREDICT,
                 autoload=True,
                 defaultSimilarity=0.0,
                 cosineSimilarityType=CosineSimilarityEnum.SCIPY,
                 vocabMaxCount=None):
        self.verbose = verbose
        self.vocabMaxCount = vocabMaxCount
        self.cosineSimilarityType = cosineSimilarityType
        self.vectorsType = vectorsType
        self.vectorsType = vectorsType
        self.defaultSimilarity = defaultSimilarity
        self.vectorSize = None
        self.vectors = None
        if folder[-1] != "/":
            folder += "/"
        if vectorsType == BaroniVectorsEnum.BEST_PREDICT:
            fileName="EN-wform.w.5.cbow.neg10.400.subsmpl.txt.gz"
            self.initVectors(vectorsType)
            self.vectorSize = 400
#         elif vectorsType == BaroniVectorsEnum.REDUCED_COUNT:
#             fileName="EN-wform.w.2.ppmi.svd.500.txt.gz"
#             self.initVectors(vectorsType)
        self.path = folder + fileName
        if self.verbose:
            print "Baroni vector " + self.path + " initialised."
        if autoload:
            self.load()
    
    def cosineSimilarity(self, v1, v2):
        assert len(v1) == len(v2)
        if self.cosineSimilarityType == CosineSimilarityEnum.HOME_MADE1:
            sumxx, sumxy, sumyy = 0, 0, 0
            for i in range(len(v1)):
                x = v1[i]; y = v2[i]
                sumxx += x*x
                sumyy += y*y
                sumxy += x*y
            return sumxy/math.sqrt(sumxx*sumyy)
        elif self.cosineSimilarityType == CosineSimilarityEnum.HOME_MADE2:
            def square_rooted(x):
                return round(sqrt(sum([a*a for a in x])),3)
            numerator = sum(a*b for a,b in zip(v1, v2))
            denominator = square_rooted(v1)*square_rooted(v2)
            return round(numerator/float(denominator),3)
#         elif self.cosineSimilarityType == CosineSimilarityEnum.SKLEARN:
#             return 1.0 - cosine_similarity(v1, v2)
        elif self.cosineSimilarityType == CosineSimilarityEnum.SCIPY:
            return 1.0 - spatial.distance.cosine(v1, v2)
#         elif self.cosineSimilarityType == CosineSimilarityEnum.HOME_MADE3:
#             return 1 - (sum(imap(mul, v1, v2))
#                 / sqrt(sum(imap(mul, v1, v1))
#                        * sum(imap(mul, v2, v2))))
#         elif self.cosineSimilarityType == CosineSimilarityEnum.HOME_MADE4:
#             ab_sum, a_sum, b_sum = 0, 0, 0
#             for ai, bi in izip(v1, v2):
#                 ab_sum += ai * bi
#                 a_sum += ai * ai
#                 b_sum += bi * bi
#             return 1 - ab_sum / sqrt(a_sum * b_sum)

    
    def initVectors(self, vectorsType):
        global baroniVectors
        if baroniVectors[vectorsType] is None:
            self.vectors = dict()
            baroniVectors[vectorsType] = self.vectors
            if self.verbose:
                print "Vectors are not yet loaded."
        else:
            self.vectors = baroniVectors[vectorsType]
            if self.verbose:
                print "Vectors already loaded."
    
    def load(self):
        if len(self.vectors.items()) == 0:
            with gzip.open(self.path,'r') as fin:
                i = 0
                for line in fin:
                    line = line.strip().split("\t")
                    word = line[0]
                    vector = [0.0] * (len(line) - 1)
                    for u in range(1, len(line)):
                        vector[u - 1] = float(line[u])
                    self.vectors[word] = vector
                    i += 1
                    if self.vocabMaxCount is not None and i > self.vocabMaxCount:
                        break
                self.addWords()
            if self.verbose:
                print "Vectors loaded."
#         if self.vectorSize is None:
#             for _, vector in self.vectors.items():
#                 self.vectorSize = len(vector)
#                 break
#             if self.verbose:
#                 print "Vectors size: " + str(self.vectorSize)
        return self.vectors

    def setCosineLib(self, cosineSimilarityType):
        self.cosineSimilarityType = cosineSimilarityType
    
    def cosineNSimilarity(self, words1, words2,
                          aggregationType=BaroniAggregationEnum.CENTROID):
        if aggregationType == BaroniAggregationEnum.CENTROID:
            centroid1 = self.getWordsCentroid(words1)
            centroid2 = self.getWordsCentroid(words2)
            if centroid1 is None or centroid2 is None:
                return self.defaultSimilarity
            else:
                return self.cosineSimilarity(centroid1, centroid2)
        elif aggregationType == BaroniAggregationEnum.MAX:
            max1 = self.getWordsMax(words1)
            max2 = self.getWordsMax(words2)
            if max1 is None or max2 is None:
                return self.defaultSimilarity
            else:
                return self.cosineSimilarity(max1, max2)
        else:
            if self.verbose:
                print "Similarity type not found."
    
    def getWordsCentroid(self, words):
        allArray = []
        oovCount = 0
        for word in words:
            if word in self.vectors:
                allArray.append(self.vectors[word])
            else:
                oovCount += 1
                if self.verbose:
                    print word + " not in the vocabulary."
        if self.verbose and oovCount > 0:
            print "oovCount " + str(oovCount) + " for " + str(words)
        if len(allArray) > 0:
            dividerArray = [len(allArray)] * self.vectorSize
#             print "len(allArray) " + str(len(allArray))
#             print "self.vectorSize " + str(self.vectorSize)
#             print "dividerArray " + str(dividerArray)
            return np.divide(np.sum(allArray, axis=0), dividerArray)
        else:
            return None
    
    def getWordsMax(self, words):
        allArray = []
        oovCount = 0
        for word in words:
            if word in self.vectors:
                allArray.append(self.vectors[word])
            else:
                oovCount += 1
                if self.verbose:
                    print word + " not in the vocabulary."
        if self.verbose and oovCount > 0:
            print "oovCount " + str(oovCount) + " for " + str(words)
        if len(allArray) > 0:
            return np.amax(allArray, axis=0)
        else:
            return None
        
        
    
    def addWords(self):
        wordsToAdd1 = \
        [
            ("n't", "not", True),
            ("'d", "had", False),
            ("d", "had", False),
            ("'ll", "will", False),
            ("ll", "will", False),
            ("'s", "is", False),
            ("s", "is", False),
            ("'m", "am", False),
            ("m", "am", False),
            ("'t", "not", False),
            ("t", "not", False),
            ("'re", "are", False),
            ("re", "are", False),
            ("'ve", "have", False),
            ("ve", "have", False),
#             ("don", "do", False),
#             ("won", "won't", False),
        ]
        
        wordsToAdd2 = \
        [
            ("n't", "not", True),
            ("'d", "d", False),
            ("d", "'d", False),
            ("'ll", "ll", False),
            ("ll", "'ll", False),
            ("'s", "s", False),
            ("s", "'s", False),
            ("'m", "m", False),
            ("m", "'m", False),
            ("'t", "t", False),
            ("t", "'t", False),
            ("'re", "re", False),
            ("re", "'re", False),
            ("'ve", "ve", False),
            ("ve", "'ve", False),
        ]
        
        for wordToAdd, word, forceReplace in wordsToAdd1:
            if forceReplace or wordToAdd not in self.vectors:
                if self.verbose:
                    if wordToAdd not in self.vectors: print "The word " + wordToAdd + " does not exist."
                if word in self.vectors:
                    self.vectors[wordToAdd] = self.vectors[word]
                else:
                    print "WARNING: " + word + " does not exist."


# Cosine distance (not cosine similarity)
