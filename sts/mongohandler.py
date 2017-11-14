# coding: utf-8



import pymongo
from pymongo import MongoClient
import collections
from text import *
from system import *
from duration import *
from sts.d2vconfigconverter import *
from number import *
import datetime

def updateMd2vStructure():
    md2vCollection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-2"]
    
    allRow = []
    for current in md2vCollection.find({}):
        current.pop("_id")
        randomMultiD2vModel = current.pop("randomMultiD2vModel")
        if randomMultiD2vModel:
            current["type"] = "random"
        else:
            current["type"] = "topdef" # or "topdelta"
        current["lastFileId"] = current["fileIdSet"][-1]
        allRow.append(current)
    
    newMd2vCollection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-3"]
    newMd2vCollection.insert_many(allRow)
    newMd2vCollection.create_index("lastFileId", unique=False)
                

class Score():
    def __init__(self, md2vCollection, d2vCollection, fileId, serieDefinition):
        self.md2vCollection = md2vCollection
        self.d2vCollection = d2vCollection
        self.fileId = fileId
        self.parents = []
        self.md2vScores = []
        self.normalizedMd2vScores = []
        self.md2vDeltaScores = []
        self.normalizedMd2vDeltaScores = []
        self.d2vScore = None
        self.normalizedD2vScore = None
        self.benefitScore = None
        self.serieDefinition = serieDefinition
        self.maxBonus = None
        self.parentScores = []
        
#         if self.fileId == "_s110_w2_mc0_a0.08_i22_sa6.8e-05_lemma_nopunct_lowercase_brown":
#             print "b"
        
        currentRequest = dict({"lastFileId": self.fileId}.items() + serieDefinition["allRequest"].items())
        for current in self.md2vCollection.find(currentRequest):
            # Parent :
            fileIdSet = current["fileIdSet"]
            parent = fileIdSet[0:len(fileIdSet) - 1]
            if len(parent) > 0:
                self.parents.append(parent)
            
            # md2v Score :
            md2vScore = current["score"]
            self.md2vScores.append(md2vScore)
            
#                 for current in self.d2vCollection.find():
#                     size = str(current["size"])
#                     if size[-1] != "0":
#                         print listToStr(postToConfig(current))
            
            # d2v score :
            d2vRow = self.d2vCollection.find_one({"hash": postToHash(fileIdToPost(self.fileId))})
            if d2vRow is not None:
                self.d2vScore = d2vRow["score"][0]
            else:
                print "A d2v score doesn't exist..."
                exit()
            
            # delta md2v score :
            if parent is None or len(parent) == 0:
                md2vDeltaScore = 0.0
            else:
                md2vParentRow = self.md2vCollection.find_one(dict({"fileIdSet": parent}.items() + serieDefinition["allRequest"].items()))
                md2vDeltaScore = md2vScore - md2vParentRow["score"]
                md2vDeltaScore = truncateFloat(md2vDeltaScore, 8)
                
                
            self.md2vDeltaScores.append(md2vDeltaScore)
            
            
#         print "self.d2vScore  = " + str(self.md2vScores)
#         print "self.md2vScores  = " + str(self.md2vScores)
#         print "self.md2vDeltaScores  = " + str(self.md2vDeltaScores)
#         exit()

    def addChild(self, parentScore):
        self.parentScores.append(parentScore)

    def setSerieDefinition(self, serieDefinition):
        self.serieDefinition = serieDefinition
    
    def __str__(self):
        return "Score Object (" + str(self.benefitScore) + " " + self.fileId + ")"
    
    def toString(self):
        d = dict()
        d["fileId"] = self.fileId
        d["parents"] = self.parents
        d["md2vScores"] = self.md2vScores
        d["md2vDeltaScores"] = self.md2vDeltaScores
        d["d2vScore"] = self.d2vScore
        d["benefitScore"] = self.benefitScore
        d["parentScores"] = self.parentScores
        
        return listToStr(d)
        
    
    def initNormalize(self):
        # Normalize all :
        self.normalizedMd2vScores = []
        for current in self.md2vScores:
            normalizedCurrent = normalize1(current, self.serieDefinition["md2vMinScore"],
                    self.serieDefinition["md2vMaxScore"])
            self.normalizedMd2vScores.append(normalizedCurrent)
#             print current
#             print normalizedCurrent
        
        self.normalizedMd2vDeltaScores = []
        for current in self.md2vDeltaScores:
#             if isinstance(self.serieDefinition["maxDeltaScore"], basestring):
#                 print "wtf"
            normalizedCurrent = normalize1(current, self.serieDefinition["minDeltaScore"],
                    self.serieDefinition["maxDeltaScore"])
            self.normalizedMd2vDeltaScores.append(normalizedCurrent)
#             print current
#             print normalizedCurrent
        
        self.normalizedD2vScore = normalize1(self.d2vScore,
                                   self.serieDefinition["d2vMinScore"],
                                   self.serieDefinition["d2vMaxScore"])
        
#         print self.d2vScore
#         print self.normalizedD2vScore
    
    def getBenefitScore(self):
        return self.benefitScore
    
    def computeBenefitScore(self):
        # Compute the benefit :
        self.benefitScore = self.computeBenefitScoreRecursive(self.serieDefinition)
        
    def computeBenefitScoreRecursive(self, serieDefinition):
        
        self.initNormalize()
        serieDefinition = serieDefinition.copy()
        # Stop condition :
        if serieDefinition["omegas"] is None or len(serieDefinition["omegas"]) == 0:
            return None
        else:
            # Some vars :
            maxCount = serieDefinition["maxCount"]
            omega = serieDefinition["omegas"][0]
            sigma = serieDefinition["sigma"]
            beta = serieDefinition["beta"]
            alpha = serieDefinition["alpha"]

            # Then for each parent :
            currentDeltaScoreMean = 0.0
            if len(self.parents) > 0:
                i = 0
                for i in range(len(self.parents)):
                    # We get currents vars :
                    currentParent = self.parents[i]
                    currentNormalizedDeltaScore = self.normalizedMd2vDeltaScores[i]
                    currentNormalizedMd2vScore = self.normalizedMd2vScores[i]
                    
                    # We compute the bonus :
                    currentAncestorBonus = sigma * beta * (float(len(currentParent) + 1) / float(maxCount))
                    currentScoreBonus = (1 - sigma) * beta * currentNormalizedMd2vScore
                    currentBonus = currentAncestorBonus + currentScoreBonus
                    
                    # And we add the bonus :
                    currentNormalizedDeltaScore += currentBonus
                    # And we normalize between 0 and 1 :
                    currentNormalizedDeltaScore = normalize1(currentNormalizedDeltaScore, 0, 1 + beta)
                    # then the score added in the mean :
                    currentDeltaScoreMean += currentNormalizedDeltaScore
                
                # We compute the mean :
                currentDeltaScoreMean = currentDeltaScoreMean / float(len(self.parents))
            
            # Compute the benefi :
            currentBenefit = omega * ((1 - alpha) * self.d2vScore + alpha * currentDeltaScoreMean)
            
            # Get all parent benefit :
            parentOmegas = serieDefinition["omegas"][1:len(serieDefinition["omegas"])]
            serieDefinition["omegas"] = parentOmegas
            parentBenefit = 0.0
            if len(self.parentScores) > 0:
                for currentParentScore in self.parentScores:
                    currentParentBenefit = currentParentScore.computeBenefitScoreRecursive(serieDefinition)
                    if currentParentBenefit is not None:
                        parentBenefit += currentParentBenefit
                parentBenefit = parentBenefit / float(len(self.parentScores))
            
            # Return the right benefit :
            currentBenefit += parentBenefit
            
            return currentBenefit

        
            
def normalize1(score, min, max):
            return (score - min) / (max - min)

class MongoMultiD2VSerieFusion():
    def __init__(self, beginTopCount=2, fusionSchedule=[1, 1, 2, 1], beginByTopdef=True,
                    infBoundScore=0.0,
                    omegas=[0.7, 0.25, 0.05],
                    alpha=0.8, beta=0.2, sigma=0.5,
                    maxCount=104, maxTopDelta=150,
                    md2vCollectionName="pc-lf-saf-cv2016-3",
                    d2vScoreTypeAndFeatures="pc-lf-cv2016",
                    d2vDbName="d2vscore-archive14"):
        
        assert(len(fusionSchedule) in [2, 4, 6, 8, 10, 12])
        
        mongoD2v = MongoD2VScore(dbId=d2vDbName, scoreTypeAndFeatures=d2vScoreTypeAndFeatures)
        topDeltaFusion = mongoD2v.topStringList(max=beginTopCount)
        
        self.collectionName = md2vCollectionName
        mRandom = MongoMultiD2VSerie(md2vCollectionName=self.collectionName)
        randomTopDelta = mRandom.computeTopDelta(type="random",
                    infBoundScore=infBoundScore,
                    omegas=omegas,
                    alpha=alpha, beta=beta, sigma=sigma,
                    maxCount=maxCount, outFormat=OutScoreEnum.LIST_STRING)
        mTopdef = MongoMultiD2VSerie(md2vCollectionName=self.collectionName)
        topdefTopDelta = mTopdef.computeTopDelta(type="topdef",
                    infBoundScore=infBoundScore,
                    omegas=omegas,
                    alpha=alpha, beta=beta, sigma=sigma,
                    maxCount=maxCount, outFormat=OutScoreEnum.LIST_STRING)
        
#         print listToStr(topdefTopDelta[:90])
#         print listToStr(randomTopDelta[:90])
                
        # Delete duplicate :
        i = 0
        newTopdefTopDelta = []
        for current in topdefTopDelta:
            if current not in topDeltaFusion:
                newTopdefTopDelta.append(current)
        topdefTopDelta = newTopdefTopDelta
        
        
        currentState = 0
        firstIndex = 0
        secondIndex = 0
        if beginByTopdef:
            mFirst = topdefTopDelta
            mSecond = randomTopDelta
        else:
            mFirst = randomTopDelta
            mSecond = topdefTopDelta
        while len(topDeltaFusion) <= maxTopDelta:
            countToAdd = fusionSchedule[currentState]
            for u in range(countToAdd):
                topDeltaFusion.append(mFirst[firstIndex])
                firstIndex += 1
            countToAdd = fusionSchedule[currentState + 1]
            for u in range(countToAdd):
                topDeltaFusion.append(mSecond[secondIndex])
                secondIndex += 1
            currentState = (currentState + 2) % len(fusionSchedule)
            
            
        
        topDeltaFusion = topDeltaFusion[:maxTopDelta]
        
#         print listToStr(topDeltaFusion)
#         print len(topDeltaFusion)
        
        self.topDeltaFusion = topDeltaFusion
    
    def getTopDeltaFusion(self):
        return self.topDeltaFusion
        
        
    
class OutScoreEnum():
    (
        SCORE,
        LIST_STRING
    ) = range(2)

    
class MongoMultiD2VSerie():
    def __init__(self, verbose=False, d2vDbName="d2vscore", md2vCollectionName="pc-lf-saf-cv2016-3", d2vCollectionName="pc-lf-cv2016-1"):
        self.md2vCollection = MongoClient()["multid2vscore"][md2vCollectionName]
        self.d2vCollection = MongoClient()[d2vDbName][d2vCollectionName]
        self.verbose = verbose
        self.allScores = None
        self.topDelta = None
    
    def getAllScores(self):
        return self.allScores
    
    def getTopDelta(self):
        return self.topDelta
    
    def computeTopDelta(self, infBoundScore=0.0,
                    omegas=[0.7, 0.25, 0.05],
                    alpha=0.8, beta=0.2, sigma=0.5,
                    type=None,
                    maxCount=104, outFormat=OutScoreEnum.SCORE):
        # We set the topdelta serieDefinition :
        self.serieDefinition = dict()
        self.serieDefinition["infBoundScore"] = infBoundScore
        self.serieDefinition["type"] = type
        self.serieDefinition["maxCount"] = maxCount
        self.serieDefinition["d2vMinScore"] = self.d2vCollection.find_one(sort=[("score", 1)])["score"][0]
        self.serieDefinition["d2vMaxScore"] = self.d2vCollection.find_one(sort=[("score", -1)])["score"][0]
        self.serieDefinition["omegas"] = omegas
        self.serieDefinition["alpha"] = alpha
        self.serieDefinition["minDeltaScore"] = 0
        self.serieDefinition["maxDeltaScore"] = None
        self.serieDefinition["beta"] = beta
        self.serieDefinition["sigma"] = sigma
        
        allRequest = dict()
        if type is not None:
            allRequest["type"] = self.serieDefinition["type"]
        if maxCount is not None:
            if type == "topdef":
                allRequest["count"] = {"$lt": 60 + 1}
            else:
                allRequest["count"] = {"$lt": self.serieDefinition["maxCount"] + 1}
        if infBoundScore is not None:
            allRequest["score"] = {"$gt": self.serieDefinition["infBoundScore"]}
        self.serieDefinition["allRequest"] = allRequest
        
        self.serieDefinition["md2vMinScore"] = self.md2vCollection.find_one(allRequest, sort=[("score", 1)])["score"]
        self.serieDefinition["md2vMaxScore"] = self.md2vCollection.find_one(allRequest, sort=[("score", -1)])["score"]
        
#         print self.serieDefinition["md2vMinScore"]
#         print self.serieDefinition["md2vMaxScore"]
#         
#         exit()
        
        # We create all score lioes :
        allFileId = []
        self.allScores = []
        i = 0
        for current in self.md2vCollection.find(self.serieDefinition["allRequest"]):
            theFileId = current["lastFileId"]
            if theFileId not in allFileId:
                allFileId.append(theFileId)
                self.allScores.append(Score(self.md2vCollection, self.d2vCollection, theFileId, self.serieDefinition))
        
        # We compute the max and min delta score md2v :
        maxDeltaScore = sys.float_info.min
        minDeltaScore = sys.float_info.max
        for currentScore in self.allScores:
            if len(currentScore.parents) > 0:
                md2vDeltaScores = currentScore.md2vDeltaScores
                currentMax = max(md2vDeltaScores)
                currentMin = min(md2vDeltaScores)
                if currentMax > maxDeltaScore:
                    maxDeltaScore = currentMax
                if currentMin < minDeltaScore:
                    minDeltaScore = currentMin
        self.serieDefinition["maxDeltaScore"] = maxDeltaScore
        self.serieDefinition["minDeltaScore"] = minDeltaScore
        
        # We set all children for all scores :
        for currentScore in self.allScores:
            for potentialParentScores in self.allScores:
                for parent in currentScore.parents:
                    if parent[-1] == potentialParentScores.fileId:
                        currentScore.addChild(potentialParentScores)
                        break
        
        # We set the serieDefinition of all scores :
        for currentScore in self.allScores:
            currentScore.setSerieDefinition(self.serieDefinition)
        
        # Print the definition :
        if self.verbose:
            print listToStr(self.serieDefinition)
        
        # We compute all
        for currentScore in self.allScores:
            currentScore.computeBenefitScore()
        
        self.allScores.sort(key=lambda x: x.benefitScore, reverse=True)
        
        if outFormat == OutScoreEnum.SCORE:
            return self.allScores
        else:
            result = []
            for current in self.allScores:
                result.append(current.fileId)
            return result
        

def getDoublons(l):
    currentDoublons = []
    for current in l:
        equals = 0
        if current not in currentDoublons:
            for current2 in l:
                if current == current2:
                    equals += 1
            if equals >= 2:
                currentDoublons.append(current)
    return currentDoublons

def getDoublonsCount(verbose=False):
    doublonCount = []
    collection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-2"]
    for currentCount in range(1, 61):
        allRowForCurrentCount = list(collection.find({"count": currentCount, "randomMultiD2vModel": False}))
        allCurrentTotEqualsParamsStr = []
        for currentRow in allRowForCurrentCount:
            currentNotEqualsParamsStr = currentRow["notEqualsParamsStr"]
            allCurrentTotEqualsParamsStr.append(currentNotEqualsParamsStr)
        currentDoublons = getDoublons(allCurrentTotEqualsParamsStr)
        if len(currentDoublons) > 0:
            if verbose:
                print "For count " + str(currentCount) + ", there are " + str(len(currentDoublons)) + " doublons."
            doublonCount.append((currentDoublons, currentCount))
    return doublonCount
        

def deleteDoublons():
    doublonCount = getDoublonsCount()
    print listToStr(doublonCount)
    collection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-2"]
    for currentDoublons, count in doublonCount:
        for currentDoublon in currentDoublons:
            collection.delete_one({"notEqualsParamsStr": currentDoublon, "count": count})

def md2vStateBoth(printCounts=False):
    print "Random:" + md2vState(random=True, printCounts=printCounts)
    print "Not Random:" + md2vState(random=False, printCounts=printCounts)
    

def deleteCount(count=82):
    collection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-3"]
    collection.delete_many({"count": {"$gt": count}, "type": "random"})
    collection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-2"]
    collection.delete_many({"count": {"$gt": count}, "randomMultiD2vModel": True})

def md2vState(printCounts=True, random=False):
    if random:
        randomText = "random"
    else:
        randomText = "topdef"
    collection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-3"]
    total = 0
    result = ""
    for i in range(240, 0, -1):
        currentCount = len(list(collection.find({"count": i, "type": randomText})))
        total += currentCount
        result += str(i) + ": " + str(currentCount) + ", "
    if printCounts:
        print result
    if random:
        max = float(15 * 60 + 13 * 30 + 1 * 30)
        minus = float(15 * 60 + 11 * 30)
    else:
        max = float(20 * 60)
        minus = 0
    return str(int(float(total - minus) / (max - minus) * 100.0)) + "%"

def updateHash():
    collection = MongoClient()["d2vscore"]["pc-lf-cv2016-1"]
 
    for current in collection.find({}):
        hash = postToHash(current)
        collection.update_one({ "_id": current["_id"] }, {"$set": { "hash": hash }})

def collectionLen(collection):
    i = 0
    for current in collection.find({}):
        i += 1
    return i

def deleteDuplicate():
    collectionDel = MongoClient()["d2vscore"]["pc-lf-cv2016-1"]
    
    # All in RAM :
    tt = TicToc()
    tt.tic()
    debSize = collectionLen(collectionDel)
    print "size de colection au début : " + str(debSize)
    dataBase = [None] * debSize
    i = 0
    for current in collectionDel.find({}):
        current.pop("hash")
        dataBase[i] = current
        i += 1
    tt.tic("In RAM done.")
    assert(len(dataBase) == debSize)
    
    theId = None
    
    # Iterate the dataBase :
    deleteCount = 0
    i = 0
    _idNotToBetInserted = []
    for theOne in dataBase:
        if theOne["_id"] not in _idNotToBetInserted:
            print "--> " + str(int(float(i + 1) / float(len(dataBase)) * 100.0)) + "%"
            # print listToStr(theOne)
    #         print theOne
    #         print listToStr(theOne)
            # print "----------"
            
            theOneCopy = theOne.copy()
            theOneCopy.pop("_id", None)
            theOneCopy.pop("hash", None)
            theOneCopy.pop("score", None)
            
            for toDeleteRow in collectionDel.find(theOneCopy):
                if toDeleteRow["_id"] != theOne["_id"] and postEquals(theOne, toDeleteRow):
                    
                    
                    _idNotToBetInserted.append(toDeleteRow["_id"])
                    
                    # print listToStr(toDeleteRow)
                    
                    if len(toDeleteRow["score"]) > 1:
                        print "WTF"
                    
                    if toDeleteRow["score"][0] not in theOne["score"]:
                        theOne["score"] += toDeleteRow["score"]
                        
#                         if theId is None:
#                             theId = theOne["_id"]
                        
                        print theOne["score"]
                        print dataBase[i]["score"]
                        
                        
#                     if toDeleteRow["_id"] == theId:
#                         print "OK BRO..."
                    
                    
                    deleteCount += 1
                    
            
            print deleteCount
            
            i += 1
            
            if not stout() and i > 160:
                break
    
    tt.tic("search done")
    
    print "FINAL deleteCount : " + str(deleteCount)
    finSize = collectionLen(collectionDel)
    print "size de colection A LA FIN : " + str(finSize)
    print "size differnece : " + str(debSize - finSize)
        
    newDataBase = []
    i = 0
    for current in dataBase:
        if current["_id"] not in _idNotToBetInserted:
            current["hash"] = postToHash(current)
            current.pop("_id", None)
            newDataBase.append(current)
            
    tt.tic("newDataBase done")
    
    collectionName = "pc-lf-cv2016-TO_ERASE"
    MongoClient()["d2vscore"].drop_collection(collectionName)
    collectionIns = MongoClient()["d2vscore"][collectionName]
    collectionIns.insert_many(newDataBase)
    
    
    tt.tic("insert_many done")
    
    print "len de l'ancienne collection : " + str(collectionLen(collectionDel))
    print "len de la nouvelle collection : " + str(collectionLen(collectionIns))
    
    
    i = 0
    for current in collectionIns.find({}):
        if len(current["score"]) > 1:
            print current["score"]
            i += 1
    print "Nombre de len score > 1 : " + str(i)
    
    
    tt.toc()


# Dropa collection
def dropCollection(dbId="d2vindex", collectionId="enwiki-test"):
    client = MongoClient()
    db = client[dbId]
    collection = db[collectionId]
    collection.drop()
    print db.collection_names() 
    
def printAllCollections():
    client = MongoClient()
    print "----------"
    for dbName in client.database_names():
        if "archive" not in dbName and "local" not in dbName:
            currentDb = client[dbName]
            str = ""
            str += dbName + ": "
            for collectionName in currentDb.collection_names():
                str += collectionName + " (" + unicode(currentDb[collectionName].count({})) + "), "
            print str
    print "----------"

def updateStsall():
    exit()
    client = MongoClient()
    db = client["d2vscore"]
    collection = db["stsall1"]
    collection.update_many({}, {"$set": {"negative": 0, "sample": 0.0, "iter": 5}})

def printDataBases():
    client = MongoClient()
    print client.database_names()

# Archive db :
def archiveDatabases(archiveId, archiveD2vscore=True, archiveD2vindex=False):
    client = MongoClient()
    if archiveD2vindex:
        client.drop_database('d2vindex-archive' + str(archiveId))
    if archiveD2vscore:
        client.drop_database('d2vscore-archive' + str(archiveId))
    if archiveD2vindex:
        client.admin.command('copydb', fromdb='d2vindex', todb='d2vindex-archive' + str(archiveId))
    if archiveD2vscore:
        client.admin.command('copydb', fromdb='d2vscore', todb='d2vscore-archive' + str(archiveId))

# Rename a collection
def renameCollection(dbId, fromId, toId):
    client = MongoClient()
    db = client[dbId]
    print "Before: " + str(db.collection_names())
    collection = db[fromId]
    collection.rename(toId)
    print "After: " + str(db.collection_names())

class MongoD2VCombinason():
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client["d2vscore"]
        self.collection = self.db["combinasons"]
        
    def addCombinason(self, combinasons, top30, best, results):
        top30 = MongoD2VCombinason.replacePoint(top30)
        best = MongoD2VCombinason.replacePoint(best)
        results = MongoD2VCombinason.replacePoint(results)
        self.collection.insert_one({"combinasons": combinasons, "top30": top30, "best": best, "results": results, "date": datetime.datetime.utcnow()})

    @staticmethod
    def replacePoint(listOfDict):
        result = []
        for currentTuple in listOfDict:
            currentDict = currentTuple[0]
            currentNewDict = dict()
            for key, value in currentDict.items():
                currentNewDict[key.replace(".", "-")] = value
            result.append(currentNewDict)
        return result

class MongoD2VScore():
    def __init__(self, scoreTypeAndFeatures=None, version=1, dbId="d2vscore"):
        """
        scoreTypeAndFeatures : for example pc-lf for pearson correlation and length feature
        """
        # All vars :
        self.dbId = dbId
        self.scoreTypeAndFeatures = scoreTypeAndFeatures
        self.version = version
#         self.crossValidationName = crossValidationName
        
        # CV id :
#         if self.crossValidationName == "CrossValidation2016":
#             self.crossValidationName = "cv2016"
#         elif self.crossValidationName == "CrossValidation2017":
#             self.crossValidationName = "cv2017"
            
        # scoreTypeAndFeatures :
#         if self.scoreTypeAndFeatures is None:
#             self.scoreTypeAndFeatures = ""
#         else:
#             self.scoreTypeAndFeatures = self.scoreTypeAndFeatures + "-"
        
        # The collection id :
        self.collectionId = self.scoreTypeAndFeatures + "-" + str(self.version)

        # And init the db :
        self.initDataBase()
        
    def initDataBase(self):
        self.client = MongoClient()
        self.db = self.client[self.dbId]
        self.collection = self.db[self.collectionId]
        self.collection.create_index("hash", unique=True)
        
    def resetDatabase(self):
        answer = raw_input('Are you sure ? (Y/n)')
        if answer == "Y":
            self.client.drop_database(self.dbId)
            self.initDataBase()
    
    def getIndexesSize(self):
        count = 0
        for index in self.collection.list_indexes():
            count += 1
        return count

    def toTopString(self, request={}, max=20, dispEndCount=6):
        entries = self.getAll(request)
        i = 0
        size = len(entries)
        modulo = size / dispEndCount
        forWhat = "all"
        if request != {}:
            forWhat = str(request)
        result = "Top " + str(max) + " on " + str(size) + " for " + forWhat + " in " + self.collectionId + ":\n"
        for entry in entries:
            if i < max or i == (size - 1):
                result += str(i + 1) + ": " + self.entryToString(entry) + "\n"
            elif i == max:
                result += "[...]\n"
            elif i % modulo == 0:
                result += str(i + 1) + ": " + self.entryToString(entry) + "\n"
                result += "[...]\n"
            i += 1
        return result
    
    def entryToString(self, entry):
        return str(entry["score"]) + " " + configToFileId(postToConfig(entry))

    
    def toString(self):
        result = ""
        for entry in self.collection.find({}):
            result += self.entryToString(entry) + "\n"
        return result
    
    def getFirstScore(self, config):
        return self.getOne(config)["score"][0]
    
    def configToHash(self, config):
        post = configToPost(config)
        return post["hash"]
    
    def exists(self, config):
        if self.getOne(self.configToHash(config)) is not None:
            return True
        else:
            return False
    
    def size(self):
        return self.collection.count({})
    
    def getScoreCount(self, config):
        post = self.getOne(self.configToHash(config))
        return len(post["score"])
 
    def addScore(self, score, config):
        post = configToPost(config)
        post["score"] = [score]
        
        entryInDB = self.getOne(post["hash"])
        if entryInDB is None:
            self.collection.insert_one(post)
        else:
            scoreExists = False
            for scoreInDB in entryInDB["score"]:
                if score == scoreInDB:
                    scoreExists = True
                    break
            if not scoreExists:
                self.collection.update_one({"hash": post["hash"]}, {"$push": {"score": post["score"][0]}})
    
        # self.collection.update_one({"hash": post["hash"]}, {"$push": {"score": post["score"]}, "$set": (post for post.pop("score")}, upsert=True)
        
    def getOne(self, something):
        if isinstance(something, dict) or isinstance(something, collections.OrderedDict):
            # something is a config :
            if "Doc2VecFeature" in something:
                hash = self.configToHash(something)
                return self.collection.find_one({"hash": hash})
            # something is a request
            else:
                return self.collection.find_one(something)
        # something is a  hash
        else:
            return self.collection.find_one({"hash": something})

    def getAll(self, something):
        # something is a request :
        cursor = self.collection.find(something)
        entries = []
        for result in cursor:
            entries.append(result)
        
        sortedEntries = MongoD2VScore.sortEntries(entries)
        
        return sortedEntries

    def topStringList(self, max=20):
        if max <= 0:
            return []
        all = self.getAll({})
        result = []
        i = 0
        for current in all:
            result.append(postToFileId(current))
            i += 1
            if i == max:
                break
        return result

    def find(self, query={}):
        return self.collection.find(query)
    
    def toDataFrame(self):
        import pandas as pd
        import numpy as np
        all = self.find()
        data = []
        for line in all:
            line["score"] = np.mean(line["score"])
            line.pop("_id")
            data.append(line)
        df = pd.DataFrame(list(data))
        return df
        
    @staticmethod
    def sortEntries(entries):
        sortedEntries = sorted(entries, key=lambda tup: max(tup["score"]))
        return list(reversed(sortedEntries))

def fixD2vScoreDatabase(dbNameList=["d2vscore", "d2vscore-archive15", "d2vscore-archive14", "d2vscore-archive16", "d2vscore-archive17"]):
    def d2vState():
        print "\n\n------- D2V State"
        print "Collection count: " + str(d2vCollection.count({})) # 47486 au début
        indexesStr = "Indexes: "
        for currentIndex in d2vCollection.list_indexes():
            indexesStr += currentIndex["name"] + ", "
        print indexesStr
        i = 0
        for current in d2vCollection.find({}, sort=[("score", -1)]):
            print str(i) + ") " + str(current)
            print postToFileId(current)
            i += 1
            if i == 4:
                break
            
        nbCountScore = 0
        for current in d2vCollection.find({}):
            if len(current["score"]) > 1:
                nbCountScore += 1
        print "Nombre de score len > 1 : " + str(nbCountScore)
        
        notGoodHashCount = 0
        for current in d2vCollection.find({}):
            if current["hash"] != postToHash(current):
                notGoodHashCount += 1
        print "notGoodHashCount: " + str(notGoodHashCount)
            
        print "-------\n\n"
    
    def createHashCollection():
        client.drop_database("hash-test")
        hashDatabase = client["hash-test"]
        hashCollection = hashDatabase["pc-lf-cv2016"]
        for current in d2vCollection.find({}):
            hash = postToHash(current)
            hashCollection.insert_one({"hash": hash, "d2vId": current["_id"], "storedHash": current["hash"]})
        hashCollection.create_index("hash", unique=False)
    
    for d2vDbName in dbNameList:
        # Databases and collections :
        client = MongoClient()
        hashDatabase = client["hash-test"]
        hashCollection = hashDatabase["pc-lf-cv2016"]
        d2vDatabase = client[d2vDbName]
        d2vCollection = d2vDatabase["pc-lf-cv2016-1"]
        
        # d2v hash :
        try:
            d2vCollection.drop_index("hash_1")
        except pymongo.errors.OperationFailure:
            pass
        
       
        
        print "\n\n-------------------------------------------------------------\n\n"
        tt = TicToc()
        tt .tic(d2vDbName)
        
        # State :
        d2vState()
        
        createHashCollection()
        tt.tic("createHashCollection done.")
        # exit()
        
        # Update all id :
        for current in hashCollection.find({}):
            d2vCollection.update_one({"_id": current["d2vId"]}, {"$set": {"hash": current["hash"]}})
            
            
        tt.tic("Update all id done.")
        
        # Get all duplicate id :
        idToDelete = []
        for current in hashCollection.find({}):
            if current["d2vId"] not in idToDelete:
                currentScores = d2vCollection.find_one({"_id": current["d2vId"]})["score"]
                initialScoreLength = len(currentScores)
                for potentialDuplicate in hashCollection.find({"hash": current["hash"]}):
                    if current["_id"] != potentialDuplicate["_id"]:
                        idToDelete.append(potentialDuplicate["d2vId"])
                        currentScores += d2vCollection.find_one({"_id": potentialDuplicate["d2vId"]})["score"]
                if initialScoreLength != len(currentScores):
                    d2vCollection.update_one({"_id": current["d2vId"]}, {"$set": {"score": currentScores}})
        print "duplicateCount: "  + str(len(idToDelete))
        
        
        tt.tic("duplicateCount done.")
        
        # Delete all duplicate id:
        for currentId in idToDelete:
            d2vCollection.delete_one({"_id": currentId})
            
        tt.tic("Delete all duplicate id done.")
        
        d2vCollection.create_index("hash", unique=True)
        MongoClient().drop_database("hash-test")
        
        d2vState()
        
        tt.toc()
    
def deleteMd2vScoreWithoutDirectParent():
    print "start"
    while True:
        collection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-3"]
        toDelete = []
        for current in collection.find({"type": "random"}):
            if current["_id"] not in toDelete and current["count"] >= 2:
                parentLastFileId = current["fileIdSet"][-2]
                theParent =  collection.find_one({"type": "random", "lastFileId": parentLastFileId})
                if theParent is None:
                    toDelete.append(current["_id"])
                    print current["count"]
        if len(toDelete) == 0:
            break
        if not stout():
            raw_input("Continue ?")
        for id in toDelete:
            collection.delete_one({"type": "random", "_id": id})
    print "end"

def fixTtopdeltaParametersStr():
    collection = MongoClient()["multid2vscore"]["pc-lf-saf-cv2016-3"]
    i = 0
    for current in collection.find({"type": "topdelta"}):
        # Get data :
        oldParams = current["topdeltaParameters"]
        oldParamsStr = current["topdeltaParametersStr"]
        
        # print :
#         print "oldParams: " + listToStr(oldParams)
#         print "oldParamsStr: " + oldParamsStr
        
        # convert to config :
        config = collections.OrderedDict()
        config["MultiDoc2VecFeature.topdelta.alpha"] = oldParams["alpha"]
        config["MultiDoc2VecFeature.topdelta.beginByTopdef"] = oldParams["beginByTopdef"]
        config["MultiDoc2VecFeature.topdelta.beginTopCount"] = oldParams["beginTopCount"]
        config["MultiDoc2VecFeature.topdelta.beta"] = oldParams["beta"]
        config["MultiDoc2VecFeature.topdelta.fusionSchedule"] = oldParams["fusionSchedule"]
        config["MultiDoc2VecFeature.topdelta.infBoundScore"] = oldParams["infBoundScore"]
        config["MultiDoc2VecFeature.topdelta.maxCount"] = oldParams["maxCount"]
        config["MultiDoc2VecFeature.topdelta.omegas"] = oldParams["omegas"]
        config["MultiDoc2VecFeature.topdelta.sigma"] = oldParams["sigma"]
        
        # Convert the config to params :
        newParams = configToTopdeltaDict(config)
        newParamsStr = str(newParams)
        
        # Print current :
#         print "newParams: " + listToStr(newParams)
#         print "newParamsStr: " + newParamsStr
        
        collection.update_one({"_id": current["_id"]},
                              {"$set": {"topdeltaParameters": newParams,
                                "topdeltaParametersStr": newParamsStr}})
        
        print i
        i += 1
