# coding: utf-8



import random
import gzip
from util.text import *
from gensim.models import doc2vec
from threading import Thread
from util.duration import *
from util.system import *
from sts import stsparser
from datastructure.hashmap import SerializableHashMap
import pymongo
from pymongo import MongoClient
from random import randint
    

class FileIndex():
    def __init__(self):
        self.indexes = [None] * 9
    
    def getIndexId(self, intTag):
        return intTag * 9 / 89741664
    
    def getIndexFile(self, id):
        return "~/d2vindex/d2vindex_compresslevel0_nopunct_ukwac_" + str(id) + ".bin"
    
    def getIndex(self, tagId):
        # Get the id of the index :
        id = None
        if isinstance(tagId, int):
            id = self.getIndexId(tagId)
        else:
            id = 0
        
        # Get the index :
        index = self.indexes[id]
        if index is None:
            tt = TicToc()
            tt.tic("Loading of the index " + str(id) + "...")
            index = SerializableHashMap(self.getIndexFile(id))
            tt.toc("Index " + str(id) + " loaded.")
            self.indexes[id] = index
        return index
    
    def getSentence(self, tagId):
        index = self.getIndex(tagId)
        if stout():
            return index.getOne(tagId)[0]
        else:
            return "test"
    
    def printMostSimilar(self, model, tagId, max=10):
        # Get the most similar :
        tt = TicToc()
        tt.tic("Getting most similars...")
        mostSimilar = model.docvecs.most_similar(positive=[tagId])
        tt.toc("Getting most similars done.")
        
        # Print the sentence :
        i = 1
        sentence = self.getSentence(tagId)
        print 'Most similar of "' + sentence + '":'
        for result in mostSimilar:
            if self.getIndex(result[0]) == 0:
                print "\t" + str(result[1]) + ' --> "' + self.getSentence(result[0]) + '"'
            if i == max:
                break
            i += 1

class MongoD2VGetter():
    def __init__(self, dbId="d2vindex", collectionId="nopunct_ukwac"):
        self.client = MongoClient()
        self.db = self.client[dbId]
        self.collection = self.db[collectionId]
    
    def getSentence(self, id):
        result = self.collection.find_one({"id": id})
        if result is not None:
            return result["text"]
        else:
            return "--------- Not yet stored -----------"
    
    def printMostSimilar(self, model, tagId, max=10):
        # Get the most similar :
        tt = TicToc()
        tt.tic("Getting most similars...")
        mostSimilar = model.docvecs.most_similar(positive=[tagId])
        tt.toc("Getting most similars done.")
        
        # Print the sentence :
        i = 1
        sentence = self.getSentence(tagId)
        print 'Most similar of "' + sentence + '":'
        for result in mostSimilar:
            print "\t" + str(result[1]) + ' --> "' + self.getSentence(result[0]) + '"'
            if i == max:
                break
            i += 1
        print
    
    def printSimilarity(self, model, tagId1, tagId2):
        sentence1 = self.getSentence(tagId1)
        sentence2 = self.getSentence(tagId2)
        sim = model.docvecs.similarity(tagId1, tagId2)
        print 'Similarity ' + str(sim) + ' between:'
        print sentence1
        print sentence2
        print

def loadD2vModel(modelFilePath=None, normalize=True):
    # Time :
    tt = TicToc()
    tt.tic("Loading the model...")
    
    # Model :
    model = doc2vec.Doc2Vec.load(modelFilePath)
    if normalize:
        model.init_sims(replace=True)
    tt.toc("Model loaded.")
    
    return model
    



if __name__ == '__main__':
    model = loadD2vModel()
    
    # Print most similar :
    mongoIndex = MongoD2VGetter()
    
#     maxTag = 10000000
    maxTag = 1000000
    
    for i in range(30):
        ri = randint(1, maxTag)
        ri2 = randint(1, maxTag)
        mongoIndex.printSimilarity(model, ri, ri2)
    
    for i in range(30):
        ri = randint(1, maxTag)
        mongoIndex.printMostSimilar(model, ri)
    
    
    
    mongoIndex.printMostSimilar(model, "sts_120d01764a058657eb82c95cbf4f8c94")

    


