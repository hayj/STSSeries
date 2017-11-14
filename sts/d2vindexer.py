# coding: utf-8

from sts.d2vtrainer import *
from sts.d2vconfigconverter import *
from datastructure.hashmap import *
import pymongo
from pymongo import MongoClient

class IndexGeneratorForDoc2Vec(MaltSentenceGenerator):
    def __init__(self, *args, **kwargs):
        kwargs['generateIndex'] = True
        super(IndexGeneratorForDoc2Vec, self).__init__(*args, **kwargs)
    
    def __iter__(self):
        # Now we train on STS data :
        agParser = stsparser.AgirreParser(verbose=True, removeStopWords=self.removeStopWords, removePunct=self.removePunct, toLowerCase=self.toLowerCase, lemma=self.lemma);
        hmAll = agParser.loadSTS();
        for sentencePair, (parsed1, parsed2, _) in hmAll.items():
            yield ("sts_" + strToHashCode(sentencePair.s1), sentencePair.s1, parsed1)
            yield ("sts_" + strToHashCode(sentencePair.s2), sentencePair.s2, parsed2)
        # Yield all malt sentences :
        i = 0
        for (originalSentence, currentSentence) in super(IndexGeneratorForDoc2Vec, self).__iter__():
            yield (i, " ".join(originalSentence), currentSentence)
            i += 1

class Doc2VecIndexerFile():
    def __init__(self, params, dataDirectories, saveDirectory, inputPerFile=10000000, compresslevel=0):
        self.id = paramsToId(params)
        self.inputPerFile = inputPerFile
        self.d2vParams = params['doc2vec']
        self.generatorParams = params['generator']
        self.compresslevel = compresslevel
        self.dataDirectories = dataDirectories
        # We add the '/' if not exist at the end :
        if saveDirectory[-1] != '/':
            saveDirectory += '/'
        self.saveDirectory = saveDirectory
 
    def index(self):
        # Init duration :
        tt = TicToc()
        tt.tic(msg="Index " + self.id)
        
        # We create the generator :
        ig = IndexGeneratorForDoc2Vec(self.dataDirectories, **(self.generatorParams));
        
        inputCounter = 0
        fileCounter = 0
        currentHm = None
        for (hash, originalSentence, currentSentence) in ig:
            if inputCounter % self.inputPerFile == 0:
                if currentHm is not None:
                    currentHm.serialize()
                filePath = self.saveDirectory + "d2vindex_compresslevel" + str(self.compresslevel) + self.id + "_" + str(fileCounter) + ".bin"
                currentHm = SerializableHashMap(filePath, compresslevel=self.compresslevel)
                fileCounter += 1
            currentHm.add(hash, (originalSentence, currentSentence))
            inputCounter += 1
        if currentHm is not None:
            currentHm.serialize()
            
        tt.toc(msg=(self.id + " done."));

class MongoD2VIndexer():
    def __init__(self, params, dataDirectories, description=None, dbId="d2vindex", collectionId="nopunct_ukwac", test=False):
        self.id = paramsToId(params)
        self.d2vParams = params['doc2vec']
        self.generatorParams = params['generator']
        self.description = description
        self.dataDirectories = dataDirectories
        self.client = MongoClient()
        self.db = self.client[dbId]
        self.collection = self.db[collectionId]
        self.test = test
 
    def index(self):
        # Init duration :
        tt = TicToc()
        tt.tic("Index " + self.id)
        
        # We create the generator :
        ig = IndexGeneratorForDoc2Vec(self.dataDirectories, **(self.generatorParams));
        
        i = 0
        for (id, originalSentence, _) in ig:
            self.add(id, originalSentence)
            if self.test and i == 60000:
                break
            i += 1
            if isinstance(id, int) and id % 1000000 == 0:
                print "--> " + str(float(id) / float(89741664) * 100.0) + "%"
            
        tt.toc(self.id + " done.");
        
    def add(self, id, originalSentence):
        post = {"id": id, "text": originalSentence}
        self.collection.insert_one(post)
    
    def getOne(self, id):
        return self.collection.find_one({"id": id})



def toFile(config, dataDirectories, saveDirectory):
    indexer = Doc2VecIndexerFile(config[0], dataDirectories, saveDirectory)
    indexer.index()
    
        

def toMongoDB(config, description=None, dataDirectories):
    indexer = MongoD2VIndexer(config[0], dataDirectories, description=description, collectionId="nopunct_enwiki")
    indexer.index()
    print indexer.getOne("sts_120d01764a058657eb82c95cbf4f8c94")



if __name__ == '__main__':
    
    # Some tests :
    verbose = True;
    test = False;
    
    # All config to train :
    config = \
    [
        {
            "doc2vec":
            {
                "size": 1000,
                "window": 8,
                "min_count": 15, # for little corpora, this can disp an error in building the vocab
                "workers": 6
            },
            "generator":
            {
                "lemma": False,
                "removeStopWords": False,
                "removePunct": True,
                "toLowerCase": True,
                "verbose": verbose,
                "test": test,
                "dataPart": 1.0,
                "data": "enwiki"
            }
        }
    ]
    
    description = "This index is the index of all doc2vec models which have no punct and with 14352 sentence pairs (without MNT) from SemEval 2016. All sentence from all SemEval pairs have a string id (sts_[hash]), and all sentence from ukwac have a int id."
    
    if stout():
        toMongoDB(config, description)
