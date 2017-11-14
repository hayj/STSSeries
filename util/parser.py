# coding: utf-8

from datastructure.hashmap import SerializableHashMap
from util.system import *



class SerializableParser(object):
    """
    This class allow the user to parse some sentences or other object hashable
    and automatically store all results on the disk. See the unit test for usage example.
    """
    def __init__(self, storeAsGzip=False,
                 verbose=False,
                 percentEach=20,
                 autoSerialize=True,
                 autoSerializeEach=True,
                 serializeEach=200,
                 workingPath=None,
                 fileId=None):
        # Instance vars :
        self.workingDirectory = workingPath
        self.verbose = verbose
        self.serializeEach = serializeEach
        self.autoSerialize = autoSerialize
        self.fileId = fileId
        self.autoSerializeEach = autoSerializeEach
        self.percentEach = percentEach
        self.storeAsGzip = storeAsGzip
        
        # Set the fileId :
        if self.fileId is None:
            self.fileId = "noid"
        
        # Get the tmp directory :
        if self.workingDirectory is None:
            self.workingDirectory = getWorkingDirectory()
            
        # Private vars :
        self.notSerializedCount = 0
        self.filePath = self.workingDirectory + "/" + "computed" + "_" + self.fileId + ".bin"
        self.hm = SerializableHashMap(self.filePath, self.storeAsGzip)
        self.oldSize = len(self.getHashMap())
        
        # Some preproc :
        self.updateSerializeEach()
        
        self.alreadyExistRowCount = 0
        
        self.doublonDict = dict()
        self.countDoublons = True
        if stout():
            self.countDoublons = False
        
    
    def setVerbose(self, verbose):
        self.verbose = verbose
    
    def setAutoSerializeEach(self, autoSerializeEach):
        self.autoSerializeEach = autoSerializeEach
    
    def setAutoSerialize(self, autoSerialize):
        self.autoSerialize = autoSerialize
        
    def serializeIfChanged(self):
        if self.oldSize != len(self.getHashMap()):
            self.serialize()
    
    def parseAll(self, sentences, parserFunct, argsDict=None):
        """
        This method parse all sentences and serialize all results at the end.
        In argsDict, you can give a dict of tuple (for each sentence) for a *args in the parse funct
        Or a dict of dict for a **kwargs
        """
        # Parse all sentences :
        i = 0
        for sentence in sentences:
            if argsDict is not None:
                if sentence in argsDict:
                    if isinstance(argsDict[sentence], dict):
                        self.parse(sentence, parserFunct, **(argsDict[sentence]))
                    else:
                        self.parse(sentence, parserFunct, *(argsDict[sentence]))
            else:
                self.parse(sentence, parserFunct)
            # Print the processing % :
            if (self.verbose) and ((i % self.percentEach) == 0):
                print ">>>>>>>>> " + str(float(i) / float(len(sentences)) * 100.0) + "% done."
            i += 1
        # Serialize at the end :
        if (self.autoSerialize) and (self.notSerializedCount > 0):
            self.serialize()
            if self.verbose:
                print "Serialized until last sentence: " + self.getStringOfKey(sentences[-1])
    
    def clean(self):
        self.oldSize = 0
        return self.hm.clean()
    
    def size(self):
        return self.hm.size()
    
    def getOne(self, sentence):
        return self.hm.getOne(sentence)
    
    def getHashMap(self):
        return self.hm.dict
            
    def parse(self, sentence, parserFunct, *args, **kwargs):
        """
        This method parse a sentence according to a function.
        """
        # Get the already parsed sentence :
        parsedSentence = self.hm.getOne(sentence)
        
        
        if parsedSentence is not None and self.countDoublons:
            # print "this sentence already exists" # 156e54ad24e48f054e7162616a0ac20d
            self.alreadyExistRowCount += 1
            if sentence in self.doublonDict:
                self.doublonDict[sentence] += 1
            else:
                self.doublonDict[sentence] = 1
               
#             print self.alreadyExistRowCount
#             print self.fileId
#             for key, current in self.doublonDict.items():
#                 if current > 1:
#                     print key
              

        # If it does not exist :
        if parsedSentence is None:
            # Inc the count 
            self.notSerializedCount += 1
                        
            # Get the parsed sentence and add it :
            parsedSentence = parserFunct(sentence, *args, **kwargs)
            self.hm.add(sentence, parsedSentence)

            # Then serialize each :
            if self.autoSerialize:
                self.updateSerializeEach()
                if (self.notSerializedCount % self.serializeEach) == 0:
                    self.serialize()
                    if self.verbose:
                        print "Serialized until: " + self.getStringOfKey(sentence)
                else:
                    if self.verbose:
                        print "Waiting to serialize: " + self.getStringOfKey(sentence)
        else:
            if self.verbose:
                print "Loaded: " + self.getStringOfKey(sentence)

        # Return the result :
        return parsedSentence
    
    def getStringOfKey(self, sentence):
        if isinstance(sentence, str):
            return sentence
        elif isinstance(sentence, unicode):
            import unicodedata
            return unicodedata.normalize('NFKD', sentence).encode('ascii','ignore')
        else:
            return str(sentence)
    
    def serialize(self):
        self.hm.serialize()
        
    def updateSerializeEach(self):
        if self.autoSerializeEach:
            coef = 10
            if self.hm.size() > (coef + 1):
                self.serializeEach = int(float(self.hm.size()) / float(coef))
            else:
                self.serializeEach = 1
                
        
