# coding: utf-8

import cPickle as pickle
import util.text
from util.system import *
from util.system import getWorkingDirectory
import os
import gzip

class SerializableHashMap():
    # class Value(): # Todo date history, object, max number (limit)...

    def __init__(self, filePath, compresslevel=0):
        self.dict = dict()
        self.filePath = filePath
        self.compresslevel = compresslevel
        self.load()
        
    
    def serialize(self):
        f = None
        if self.compresslevel > 0:
            f = gzip.GzipFile(self.filePath, 'w', compresslevel=self.compresslevel)
        else:
            f = open(self.filePath, 'w')
        try:
            pickle.dump(self.dict, f, pickle.HIGHEST_PROTOCOL)
        finally:
            f.close()

    def add(self, key, value):
        self.dict[key] = value
        
    def getOne(self, key):
        if self.has_key(key):
            return self.dict[key]
        else:
            return None
        
    def has_key(self, key):
        return self.dict.has_key(key)
        
    def load(self):
        if (len(sortedGlob(self.filePath)) > 0):
            print "Loading " + self.filePath + " from the disk"
            f = None
            if self.compresslevel > 0:
                f = gzip.GzipFile(self.filePath, 'r', compresslevel=self.compresslevel)
            else:
                f = open(self.filePath, 'r')
            try:
                self.dict = pickle.load(f)
            finally:
                f.close()
    
    def clean(self):
        if (len(sortedGlob(self.filePath)) > 0):
            os.remove(self.filePath)
        self.dict = dict()
    
    def size(self):
        return len(self.dict)




class SentencePair:
    def __init__(self, s1, s2):
        assert(isinstance(s1, str) or isinstance(s1, unicode))
        assert(isinstance(s2, str) or isinstance(s1, unicode))
        self.s1 = s1
        self.s2 = s2

    def __hash__(self):
        return (self.s1 + "\t" + self.s2).__hash__()

    def __eq__(self, other):
        return (self.s1 == other.s1) and (self.s2 == other.s2)
    
    def __str__(self):
        if isinstance(self.s1, str):
            return str(self.s1) + "\t" + str(self.s2)
        elif isinstance(self.s1, unicode):
            import unicodedata
            return unicodedata.normalize('NFKD', self.s1 + "\t" + self.s2).encode('ascii','ignore')
        else:
            return "Unknown object."
