# coding: utf-8



import sys
reload(sys)  
sys.setdefaultencoding('utf8')

from text import *
from duration import *
from system import *
from gensim.models import doc2vec
import gzip
from collections import OrderedDict
import re
from distutils.util import strtobool

import codecs



class MaltReader(object):
    def __init__(self, dataDirectories, verbose=True):
        self.dataDirectories = dataDirectories
        self.verbose = verbose
        self.filesPath = []
        # For all dataDirectories :
        for directory in self.dataDirectories:
            # We add the '/' if not exist at the end :
            if directory[-1] != '/':
                directory += '/'
            # We get all filesPath in :
            currentFiles = sortedGlob(directory + "*.gz")
            # If there are filesPath :
            if (len(currentFiles) > 0):
                # We add all these filesPath :
                for currentFile in currentFiles:
                    self.filesPath.append(currentFile)
            elif verbose:
                print "Empty folder!"
            

    def __iter__(self):        
        if self.verbose:
            print "files: " + str(self.filesPath)
        
        fileCounter = 0
        sentenceCounter = 0
        documentCount = 0
        
        # For all files :
        for filePath in self.filesPath:
            if self.verbose and fileCounter % 30 == 0:
                print str((float(fileCounter) / float(len(self.filesPath))) * 100.0) + '%' + ' on ' + filePath
            fileCounter += 1
            # We open the file :
            with gzip.open(filePath, 'rt') as file:
                sentences = None
                currentSentence = None
                docId = None
                # For all lines in the current file :
                for currentLine in file:
                    currentLine = currentLine.strip()
                    # currentLine = unicode(currentLine, "utf-8").strip()
                    # currentLine = currentLine.decode("utf-8").strip()
                    if currentLine.startswith("<doc id="):
                        m = re.search(u'id="(.+?)"', currentLine)
                        if m:
                            docId = m.group(1)
                        else:
                            print "docId error..."
                        document = None
                        sentences = []
                        currentSentence = None
                    elif currentLine.startswith("</doc"):
                        if currentSentence is not None and len(currentSentence) > 0:
                            sentences.append(currentSentence)
                        document = dict()
                        document["id"] = docId
                        document["sentences"] = []
                        for sentence in sentences:
                            sentenceDict = dict()
                            sentenceDict["id"] = sentenceCounter
                            words = []
                            for word in sentence:
                                words.append(word["word"])
                            sentenceDict["hash"] = strToHashCode2(listToStr(words))
                            sentenceDict["words"] = sentence
                            document["sentences"].append(sentenceDict)
                            sentenceCounter += 1
                        if len(document["sentences"]) > 0:
                            yield document
                            documentCount += 1
#                         if documentCount == 100:
#                             break
                    else:
                        splitedLine = currentLine.split('\t')
                        # If we have something and the first element is a int :
                        if len(splitedLine) >= 4 and representsInt(splitedLine[0]):
                            # We get the index of the sentence :
                            wordId = int(splitedLine[0])
                            if wordId == 1:
                                # We start a new sentence :
                                if currentSentence is not None and len(currentSentence) > 0:
                                    sentences.append(currentSentence)
                                currentSentence = []
                                previousWordId = 0
                            if wordId == previousWordId + 1:
                                currentWord = OrderedDict()
                                currentWord["id"] = wordId
                                currentWord["word"] = trim(splitedLine[1])
                                currentWord["lc"] = currentWord["word"].lower()
                                currentWord["malt_lemma_lc"] = trim(splitedLine[2])
                                currentWord["nltk_wordnet_lemma"] = lemmatize(currentWord["word"])
                                currentWord["nltk_wordnet_lemma_lc"] = currentWord["nltk_wordnet_lemma"].lower()
                                currentWord["nltk_porter_stem"] = stem(currentWord["word"])
                                currentWord["nltk_porter_stem_lc"] = currentWord["nltk_porter_stem"].lower()
                                currentWord["punct"] = isPunct(currentWord["word"])
                                currentWord["tag"] = trim(splitedLine[3])
                                if currentWord["punct"]:
                                    for name, stopWords in StopWord.swDict.items():
                                        currentWord[name] = False
                                else:
                                    for name, stopWords in StopWord.swDict.items():
                                        currentWord[name] = currentWord["lc"] in stopWords
                                currentSentence.append(currentWord)
                                previousWordId = currentWord["id"]
                            

class MaltConverter():
    def __init__(self, dataDirectories, saveDirectory, id, compresslevel=1, documentPerFile=20000):
        self.id = id
        self.compresslevel = compresslevel
        self.documentPerFile = documentPerFile
        
        # We add the '/' if not exist at the end :
        if saveDirectory[-1] != '/':
            saveDirectory += '/'
        self.saveDirectory = saveDirectory
        self.dataDirectories = dataDirectories
    
    def convert(self):
        # Init duration :
        tt = TicToc()
        tt.tic("Converting...")
        
        mr = MaltReader(self.dataDirectories)
        
        documentCount = 0
        sentenceStartId = None
        file = None
        t = u"\t" 
        n = u"\n"
        for document in mr:
            toWrite = ""
            toWrite += u"document" + t + unicode(document["id"]) + n + n
            for sentence in document["sentences"]:
                toWrite += u"sentence" + t + unicode(sentence["id"]) + t + sentence["hash"] + n
                for wordDict in sentence["words"]:
                    for key, value in wordDict.items():
                        if isinstance(value, bool):
                            value = 1 if value else 0
                        if isinstance(value, basestring):
                            toWrite += value
                            toWrite += t
                        else:
                            toWrite += unicode(value) + t
                    toWrite += n
                toWrite += u"_" + n
                toWrite += n
                        
            if documentCount % self.documentPerFile == 0:
                # Create a file (name_sentenceStartId_sentenceidstop) :
                if file is not None:
                    file.close()
                
                sentenceId = document["sentences"][0]["id"]
                                
                
                filePath = self.saveDirectory + "hjcorpus_" + self.id + "_" + str(sentenceId) + ".bin"
                file = gzip.open(filePath, 'wt', compresslevel=self.compresslevel)
                
                firstLine = u""
                for key, value in document["sentences"][0]["words"][0].items():
                    firstLine += key + t
                file.write(firstLine + n)
            
            file.write(unicode(toWrite) + n)
            documentCount += 1
        
        
        tt.toc(self.id + " done.")
            


class ConvertedMaltReader():
    def __init__(self, dataDirectories,
                 pattern="hjcorpus_",
                 verbose=True,
                 maxFileCount=68,
                 dataPart=None,
                 replaceSwUnderscore=False):
        self.pattern = pattern
        self.dataDirectories = dataDirectories
        self.verbose = verbose
        self.replaceSwUnderscore = replaceSwUnderscore
        self.filesPath = []
        # For all dataDirectories :
        for directory in self.dataDirectories:
            # We add the '/' if not exist at the end :
            if directory[-1] != '/':
                directory += '/'
            # We get all filesPath in :
            currentFiles = sortedGlob(directory + "*" + pattern + "*", sortBy=GlobSortEnum.MTIME)
            # If there are filesPath :
            if (len(currentFiles) > 0):
                # We add all these filesPath :
                for currentFile in currentFiles:
                    self.filesPath.append(currentFile)
            elif verbose:
                print "Empty folder!"
        if maxFileCount is not None:
            self.filesPath = self.filesPath[:maxFileCount]
        
        if dataPart is not None:
            dataPart = int(dataPart * float(len(self.filesPath)))
            self.filesPath = self.filesPath[:dataPart]
        
        print "ConvertedMaltReader on:\n" + listToStr(self.filesPath)
    
    def getColumns(self):
        splitedLine = None
        with gzip.open(self.filesPath[0], 'rb') as file:
            for currentLine in file:
                if currentLine.startswith("id"):
                    currentLine = unicode(currentLine, "utf-8").strip()
                    splitedLine = currentLine.split('\t')
                    break
            if self.replaceSwUnderscore:
                i = 0
                for column in splitedLine:
                    if "sw" in column:
                        column = column.replace("_", "")
                        splitedLine[i] = column
                    i += 1
        return splitedLine
            
    def __iter__(self):
        if self.verbose:
            print "files: " + str(self.filesPath)
        
        fileCounter = 0
        currentSentence = None
        
        # For all files :
        for filePath in self.filesPath:
            if self.verbose and fileCounter % 1 == 0:
                print str((float(fileCounter) / float(len(self.filesPath))) * 100.0) + '%' + ' on ' + filePath
            fileCounter += 1
            previousSentence = None
            try:
                # We open the file :
                with gzip.open(filePath, 'rb') as file:
                    firstSplittedLine = None
                    firstSplittedLine = self.getColumns() # Added at 13/08/16
                    for currentLine in file:
                        currentLine = unicode(currentLine, "utf-8").strip()
                        splitedLine = currentLine.split('\t')
                        if firstSplittedLine is None:
                            firstSplittedLine = splitedLine
                        if splitedLine[0] == "sentence":
                            currentSentence = OrderedDict()
                            currentSentence["id"] = int(splitedLine[1])
                            currentSentence["hash"] = splitedLine[2]
                            currentSentence["words"] = []
                        elif representsInt(splitedLine[0]):
                            currentWord = OrderedDict()
                            i = 0
                            for currentKey in firstSplittedLine:
                                if i == 0:
                                    currentWord[currentKey] = int(splitedLine[i])
                                elif re.search("punct", currentKey) or re.search("sw", currentKey):
                                    currentWord[currentKey] = True if splitedLine[i] == "1" else False
                                else:
                                    currentWord[currentKey] = splitedLine[i]
                                i += 1
                            currentSentence["words"].append(currentWord)
                        elif splitedLine[0] == "_":
                            yield currentSentence
                            previousSentence = currentSentence
                            currentSentence = None
            except:
                print "Error in " + filePath + " on this sentence:\n" + listToStr(previousSentence)


class SelectMaltReader():
    def __init__(self, dataDirectories, pattern="hjcorpus",
                 verbose=True,
                 removeStopWords=False,
                 removePunct=True,
                 toLowerCase=True,
                 lemma=True,
                 lemmaRegex=".*wordnet.*",
                 stopWordRegex=".*nltk.*",
                 yieldSentenceHash=False,
                 yieldSentenceId=True,
                 maxFileCount=68,
                 dataPart=None,
                 replaceSwUnderscore=False):
        self.yieldSentenceId = yieldSentenceId
        self.yieldSentenceHash = yieldSentenceHash
        self.removeStopWords = removeStopWords
        self.removePunct = removePunct
        self.toLowerCase = toLowerCase
        self.lemma = lemma
        self.lemmaRegex = lemmaRegex
        self.stopWordRegex = stopWordRegex
        self.verbose = verbose
        self.replaceSwUnderscore = replaceSwUnderscore
        
        self.dataDirectories = dataDirectories
        self.cmr = ConvertedMaltReader(self.dataDirectories,
                                       pattern=pattern,
                                       verbose=verbose,
                                       maxFileCount=maxFileCount,
                                       dataPart=dataPart,
                                       replaceSwUnderscore=self.replaceSwUnderscore)
    
        self.columns = self.cmr.getColumns()
        
        if self.verbose:
            print "columns = " + str(self.columns)
        
        # Find the right case for the word :
        self.wordColumn = "word"
        if lemma:
            lemmaColumns = []
            for column in self.columns:
                if re.search("lemma", column) or re.search("stem", column):
                    if re.search(self.lemmaRegex, column):
                        if self.toLowerCase and re.search("lc", column):
                            lemmaColumns.append(column)
                        elif not self.toLowerCase and not re.search("lc", column):
                            lemmaColumns.append(column)
            if self.verbose and len(lemmaColumns) != 1:
                raise Exception("ERROR: lemmaColumns problem (" + str(len(lemmaColumns)) + " items)")
            self.wordColumn = lemmaColumns[0]
        elif self.toLowerCase:
            self.wordColumn = "lc"
        if self.verbose:
            print "wordColumn = " + self.wordColumn
        
        self.swColumnList = []
        if self.stopWordRegex is not None:
            for column in self.columns:
                if re.search("sw", column):
                    if re.search(self.stopWordRegex, column):
                        self.swColumnList.append(column)
        if self.verbose:
            print "swColumnList = " + str(self.swColumnList)
        
    def __iter__(self):
        for sentence in self.cmr:
            sentenceId =  sentence["id"]
            sentenceHash =  sentence["hash"]
            words = []
            for wordDict in sentence["words"]:
                if self.removePunct and (wordDict["punct"] or wordDict["lc"] in ['-lrb-', '-rrb-', '-lsb-', '-rsb-', '-lcb-', '-rcb-']):
                    continue
                if self.removeStopWords:
                    isStopWord = False
                    for swColumn in self.swColumnList:
                        if "bigsw" in swColumn or "nltkextra" in swColumn or "sentsw1" in swColumn:
                            if wordDict["lc"] == "n't" or wordDict["lc"] == "an": # because "n't" was added after and "an" was "an " with a space...
                                isStopWord = True
                                break
                        if "smallsw" in swColumn:
                            if wordDict["lc"] == "an":
                                isStopWord = True
                                break
                        if swColumn == "nltksw1":
                            if wordDict["lc"] == "yo": # because the "u" was missing
                                pass
                            elif wordDict["lc"] == "you":
                                isStopWord = True
                                break
                        if wordDict[swColumn]:
                        # if wordDict["lc"] in StopWord.swDict[swColumn]:
                            isStopWord = True
                            break
                    if isStopWord:
                        continue
                if isinstance(wordDict[self.wordColumn], bool):
                    print "WTF"
                words.append(wordDict[self.wordColumn])
            if len(words) > 0:
                if self.yieldSentenceId:
                    if self.yieldSentenceHash:
                        yield (sentenceId, sentenceHash, words)
                    else:
                        yield (sentenceId, words)
                elif self.yieldSentenceHash:
                    yield (sentenceHash, words)
                else:
                    yield (words)


class ConvertedMaltSentenceGeneratorForD2V():
    def __init__(self,
                 hmAll,
                 parsingConfig,
                 dataDirectories=None,
                 verbose=True,
                 dataPart=1.0,
                 verboseIterationCount=100000,
                 maxSentenceCount=None):
        self.maxSentenceCount = maxSentenceCount
        self.hmAll = hmAll
        self.parsingConfig = parsingConfig
        self.verbose = verbose
        self.dataDirectories = dataDirectories
        self.verboseIterationCount = verboseIterationCount
        self.dataPart = dataPart
        
        self.stopWordRegex = ""
        for key, value in self.parsingConfig.items():
            if "sw" in key and value:
                key = key.replace("sw", ".*")
                self.stopWordRegex += key + "|"
        if len(self.stopWordRegex) == 0:
            self.stopWordRegex = None
        else:
            if self.stopWordRegex[-1] == "|":
                self.stopWordRegex = self.stopWordRegex[:len(self.stopWordRegex) - 1]
            self.stopWordRegex = ".*(" + self.stopWordRegex + ").*"
        
        if self.verbose:
            print "stopWordRegex: " + str(self.stopWordRegex)
    
    def __iter__(self):
        # Now we train on STS data :
        i = 0
        tt = None
        if self.verbose:
            tt = TicToc()
            tt.tic()
        for sentencePair, (parsed1, parsed2, _) in self.hmAll.items():
            if self.verbose and i % 1000 == 0:
                print "STS sentence: " + str(parsed1) + " (iteration " + str(i) + ")"
            yield doc2vec.LabeledSentence(words=(parsed1), tags=["sts_" + strToHashCode(sentencePair.s1)])
            yield doc2vec.LabeledSentence(words=(parsed2), tags=["sts_" + strToHashCode(sentencePair.s2)])
            i += 1
        
        if self.verbose:
            tt.tic("STS yields done.")
        # Yield all malt converted sentences :
        pattern = "hjcorpus_enwiki2"
        
        smr = SelectMaltReader(self.dataDirectories,
                               verbose=self.verbose,
                               removePunct=self.parsingConfig["removePunct"],
                               removeStopWords=self.parsingConfig["removeStopWords"],
                               toLowerCase=self.parsingConfig["toLowerCase"],
                               lemma=self.parsingConfig["lemma"],
                               stopWordRegex=self.stopWordRegex,
                               lemmaRegex=".*wordnet.*",
                               replaceSwUnderscore=True,
                               dataPart=self.dataPart)
        i = 0
        for sentence in smr:
            if self.maxSentenceCount is not None and i > self.maxSentenceCount:
                break
            if self.verbose and i % self.verboseIterationCount == 0:
                print "enwiki2 sentence: " + str(sentence) + " (iteration " + str(i) + ")"
                tt.toc(str(i) + " done for SelectMaltReader")
            yield doc2vec.LabeledSentence(words=(sentence[1]), tags=[sentence[0]])
            i += 1
        
        if self.verbose:
            print "Last sentence :"
            print str(sentence)
            tt.tic("SelectMaltReader yields done.")
        

def convert():
    dataDirectories = None
    saveDirectory = None
    id = "enwiki2"
    mc = MaltConverter(dataDirectories, saveDirectory, id)
    mc.convert()
        

def testRead():
    dataDirectories = None
    smr = SelectMaltReader([dataDirectories], removePunct=True, removeStopWords=True, toLowerCase=True, lemma=True, stopWordRegex=".*nltk.*", lemmaRegex=".*wordnet.*")

    tt = TicToc()

    i = 0
    for (id, words) in smr:
        if i % 500 == 0:
            print id
            print words
            tt.tic()
        i += 1
    
if __name__ == '__main__':
    if stout():
        convert()
#         testRead()
    



