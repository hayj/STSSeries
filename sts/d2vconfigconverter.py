# coding: utf-8

from util.text import *
from util.system import *
import collections
import random
from util.number import truncateFloat

def parsingStringToSwList(parsingString):
    return parsingConfigToSwList(parsingStringToParsingConfig(parsingString))

def parsingConfigToSwList(config):
    swList = []
    for key, value in config.items():
        if isinstance(value, bool) and value:
            if "sw" in key:
                swList += StopWord.swDict[key]
    if len(swList) == 0:
        return None
    return list(set(swList))
            

def parsingConfigToParsingString(config):
    # _nopunct_lowercase_[lemmatizers]_[swlists]
    parsingString = ""
    if "removePunct" in config and config["removePunct"]:
        parsingString += "_" + "nopunct"
    if "toLowerCase" in config and config["toLowerCase"]:
        parsingString += "_" + "lowercase"
    for currentLemmatizer in ["porterstem", "lemma"]:
        if currentLemmatizer in config and config[currentLemmatizer]:
            parsingString += "_" + currentLemmatizer
            break
    atLeastOneSw = False
    for currentSWList, _ in StopWord.swDict.items():
        if currentSWList in config and config[currentSWList]:
            parsingString += "_" + currentSWList
            atLeastOneSw = True
#     if atLeastOneSw:
#         parsingString = "_nostopword" + parsingString
    
    return parsingString


def parsingStringToParsingConfig(parsingString, prefix=""):
    config = OrderedDict()
    if parsingString[0] == "_":
        parsingString = parsingString[1:]
    parsingString = parsingString.split("_")
    if "nopunct" in parsingString:
        config[prefix + "removePunct"] = True
    else:
        config[prefix + "removePunct"] = False
    if "lowercase" in parsingString:
        config[prefix + "toLowerCase"] = True
    else:
        config[prefix + "toLowerCase"] = False
    for currentLemmatizer in ["porterstem", "lemma"]:
        if currentLemmatizer in parsingString:
            config[prefix + currentLemmatizer] = True
        else:
            config[prefix + currentLemmatizer] = False
    atLeastOneSw = False
    for currentSWList, _ in StopWord.swDict.items():
        if currentSWList in parsingString:
            config[prefix + currentSWList] = True
            atLeastOneSw = True
        else:
            config[prefix + currentSWList] = False
    if not atLeastOneSw and "nostopword" in parsingString:
        atLeastOneSw = True
        config[prefix + "nltksw"] = True
    if atLeastOneSw:
        config[prefix + "removeStopWords"] = True
    else:
        config[prefix + "removeStopWords"] = False
        
    
    return config
    
    
    
        

def getRandomD2vFileId():
    config = dict()
    config['Doc2VecFeature'] = True
    config['Doc2VecFeature.data.dataPart'] = getRandomFloat()
    config['Doc2VecFeature.data'] = "brown"
    if config['Doc2VecFeature.data.dataPart'] == 0.0:
        config['Doc2VecFeature.data'] = "stsall"
    
    config['Doc2VecFeature.data.sample'] = getRandomFloat(0.0, 0.00015, 7)
    config['Doc2VecFeature.data.iter'] = random.randint(5, 20)
    config['Doc2VecFeature.data.negative'] = random.randint(0, 10)
    config['Doc2VecFeature.data.alpha'] = getRandomFloat(0.01, 0.15)
    
    config['Doc2VecFeature.data.min_count'] = random.randint(0, 200)
    config['Doc2VecFeature.data.window'] = random.randint(1, 10)
    config['Doc2VecFeature.data.size'] = random.randint(50, 6000)
    
    config['Doc2VecFeature.data.lemma'] = bool(random.getrandbits(1))
    config['Doc2VecFeature.data.removeStopWords'] = bool(random.getrandbits(1))
    config['Doc2VecFeature.data.removePunct'] = bool(random.getrandbits(1))
    config['Doc2VecFeature.data.toLowerCase'] = bool(random.getrandbits(1))
    
    return configToFileId(config)


def getRandomD2vFileIdList(count=30):
    fileIdList = []
    for i in range(count):
        fileIdList.append(getRandomD2vFileId())
    return fileIdList


def configToCollectionName(config):
    scoreTypeId = ""
    if config["score"] == "NumpyPearsonCorrelation":
        scoreTypeId += "pc"
    elif config["score"] == "MeanLeastSquares":
        scoreTypeId += "mls"
    featureId = ""
    if "LengthFeature" in config and config["LengthFeature"]:
        featureId += "lf"
    if "SultanAlignerFeature" in config and config["SultanAlignerFeature"]:
        if featureId != "":
            featureId = featureId + "-"
        featureId += "saf"
    
    if scoreTypeId != "" and featureId != "":
        scoreTypeId += "-"
    
    scoreTypeAndFeatures = scoreTypeId + featureId
    
    crossValidationName = ""
    if config["data"] == "CrossValidation2016":
        crossValidationName = "cv2016"
    elif config["data"] == "CrossValidation2017":
        crossValidationName = "cv2017"
    elif config["data"] == "Normal2016":
        crossValidationName = "n2016"
    elif config["data"] == "Normal2015":
        crossValidationName = "n2015"
    elif config["data"] == "NormalSets2016":
        crossValidationName = "ns2016"
    elif config["data"] == "NormalSets2015":
        crossValidationName = "ns2015"
    elif config["data"] == "SamsungPolandMappingSets2016":
        crossValidationName = "spm2016"
    else:
        crossValidationName = "unknowndata"
    
    scoreTypeAndFeatures = scoreTypeAndFeatures + "-" + crossValidationName
    
    return scoreTypeAndFeatures

def fileIdToConfig(fileId):
    if fileId[0] == "_":
        fileId = fileId[1:]
    elements = fileId.split("_")
    size = None
    window = None
    min_count = None
    alpha = None
    lemma = False
    removeStopWords = False
    removePunct = False
    toLowerCase = False
    data = None
    dataPart = None
    sample = None
    negative = None
    iter = None
#     swListName = []
    for el in elements:
        if el[0] == "s" and representsInt(el[1:]):
            size = int(el[1:])
        elif el[0] == "w" and representsInt(el[1:]):
            window = int(el[1:])
        elif el[0] == "a" and representsFloat(el[1:]):
            alpha = float(el[1:])
        elif el[0] == "n" and representsInt(el[1:]):
            negative = int(el[1:])
        elif el[0] == "i" and representsInt(el[1:]):
            iter = int(el[1:])
        elif el[0] == "m" and el[1] == "c" and representsInt(el[2:]):
            min_count = int(el[2:])
        elif el[0] == "s" and el[1] == "a" and representsFloat(el[2:]):
            sample = float(el[2:])
        elif el == "lemma":
            lemma = True
        elif el == "nostopword" or "sw" in el:
            removeStopWords = True
#             if "sw" in el:
#                 swListName.append(el)
        elif el == "nopunct":
            removePunct = True
        elif el == "lowercase":
            toLowerCase = True
        elif "part" in el and isFloat(el[4:]):
            dataPart = float(el[4:])
#         elif isWord(el):
        elif ("brown" in el or "stsall" in el or "enwiki2" in el) and isWord(el):
            data = el
    
    # Defaults:
    if dataPart is None:
        dataPart = 1.0
    if negative is None:
        negative = 0
    if alpha is None:
        alpha = 0.025
    if iter is None:
        iter = 5
    if sample is None:
        sample = 0.0
    
    config = dict()
    config['Doc2VecFeature'] = True
    config['Doc2VecFeature.data'] = data
    config['Doc2VecFeature.data.min_count'] = min_count
    config['Doc2VecFeature.data.size'] = size
    config['Doc2VecFeature.data.window'] = window
    config['Doc2VecFeature.data.lemma'] = lemma
    config['Doc2VecFeature.data.removeStopWords'] = removeStopWords
    config['Doc2VecFeature.data.removePunct'] = removePunct
    config['Doc2VecFeature.data.toLowerCase'] = toLowerCase
    if alpha is not None:
        config['Doc2VecFeature.data.alpha'] = alpha
    if dataPart is not None:
        config['Doc2VecFeature.data.dataPart'] = dataPart
    if sample is not None:
        config['Doc2VecFeature.data.sample'] = sample
    if negative is not None:
        config['Doc2VecFeature.data.negative'] = negative
    if iter is not None:
        config['Doc2VecFeature.data.iter'] = iter
    
    if config['Doc2VecFeature.data'] == "stsall":
        config['Doc2VecFeature.data.dataPart'] = 0.0
    
    
    config = collections.OrderedDict(sorted(config.items()))
    return config
    
def fileIdToPost(fileId):
    return configToPost(fileIdToConfig(fileId))

def postToFileId(post):
    return configToFileId(postToConfig(post))

def configToFileId(config, featureName="Doc2VecFeature"):
    # We create the fileId :
    if not featureName + '.data.size' in config:
        return config[featureName + '.data']
    fileId = "";
    fileId += "_s" + str(config[featureName + '.data.size']);
    fileId += "_w" + str(config[featureName + '.data.window']);
    fileId += "_mc" + str(config[featureName + '.data.min_count']);
    if featureName + ".data.alpha" in config and config[featureName + ".data.alpha"] != 0.025:
        fileId += "_a" + str(config[featureName + '.data.alpha']);
    if featureName + ".data.iter" in config and config[featureName + ".data.iter"] != 5:
        fileId += "_i" + str(config[featureName + '.data.iter']);
    if featureName + ".data.sample" in config and config[featureName + ".data.sample"] != 0.0:
        fileId += "_sa" + str(config[featureName + '.data.sample']);
    if featureName + ".data.negative" in config and config[featureName + ".data.negative"] != 0:
        fileId += "_n" + str(config[featureName + '.data.negative']);
    if config[featureName + ".data.lemma"]:
        fileId += "_lemma";
    if config[featureName + ".data.removeStopWords"]:
        fileId += "_nostopword";
    if config[featureName + ".data.removePunct"]:
        fileId += "_nopunct";
    if config[featureName + ".data.toLowerCase"]:
        fileId += "_lowercase";
    if config[featureName + ".data"]:
        fileId += "_" + str(config[featureName + ".data"]);
    if config[featureName + ".data"] != "stsall" and config[featureName + ".data.dataPart"] < 1.0:
        fileId += "_part" + str(config[featureName + ".data.dataPart"]);
    
    return fileId

def configToD2vParams(config):
    params = dict()
    params["size"] = config["Doc2VecFeature.data.size"]
    params["window"] = config["Doc2VecFeature.data.window"]
    params["min_count"] = config["Doc2VecFeature.data.min_count"]
    params["alpha"] = config["Doc2VecFeature.data.alpha"]
    params["iter"] = config["Doc2VecFeature.data.iter"]
    params["sample"] = config["Doc2VecFeature.data.sample"]
    params["negative"] = config["Doc2VecFeature.data.negative"]
    return params

def configToGeneratorParams(config):
    params = dict()
    params["data"] = config["Doc2VecFeature.data"]
    params["lemma"] = config["Doc2VecFeature.data.lemma"]
    params["removeStopWords"] = config["Doc2VecFeature.data.removeStopWords"]
    params["removePunct"] = config["Doc2VecFeature.data.removePunct"]
    params["toLowerCase"] = config["Doc2VecFeature.data.toLowerCase"]
    params["dataPart"] = config["Doc2VecFeature.data.dataPart"]
    return params

def fileIdToFileName(fileId):
    fileName = "doc2vec_model" + fileId + ".bin"
    return fileName

def fileNameToFilePath(fileName):
    folder = "~/doc2vec";
    filePath = folder + "/" + fileName
    
    return filePath

def d2vValidator(config):
    if "Doc2VecFeature" not in config:
        return True
    if "Doc2VecFeature.data" not in config:
        return True
    if      config['Doc2VecFeature.data'] == 'brown' \
            or config['Doc2VecFeature.data'] == 'stsall' \
            or config['Doc2VecFeature.data'] == 'enwiki2' \
            or config['Doc2VecFeature.data'] == 'brown_stsall':
        return True
    id = configToFileId(config)
    fileName = fileIdToFileName(id)
    filePath = fileNameToFilePath(fileName)
    exists = fileExists(filePath)
    return exists


def postToHash_old(row, verbose=False):
    post = collections.OrderedDict()
    post["window"] = row["window"]
    post["size"] = row["size"]
    post["min_count"] = row["min_count"]
    post["alpha"] = row["alpha"]
#     post["alpha"] = truncateFloat(row["alpha"], 8)
    post["lemma"] = row["lemma"]
    post["toLowerCase"] = row["toLowerCase"]
    post["removePunct"] = row["removePunct"]
    post["removeStopWords"] = row["removeStopWords"]
#     post["sample"] = truncateFloat(row["sample"], 10)
    post["sample"] = row["sample"]
    post["iter"] = row["iter"]
    post["negative"] = row["negative"]
    post["dataPart"] = row["dataPart"]
    post["data"] = str(row["data"])
    
    
    hash = strToHashCode(str(post))
    
    if verbose:
        print "post: " + str(post)
        print "hash: " + hash
    
    # Hash
    return hash

def configToTopdeltaDict(config):
    d = collections.OrderedDict()
    for key, value in config.items():
        if "MultiDoc2VecFeature.topdelta." in key and "maxTopDelta" not in key:
            d[key.split(".")[-1]] = value
    return d


#     d["alpha"] = config["MultiDoc2VecFeature.topdelta.alpha"]
#     d["beta"] = config["MultiDoc2VecFeature.topdelta.beta"]
#     d["sigma"] = config["MultiDoc2VecFeature.topdelta.sigma"]
#     d["omegas"] = config["MultiDoc2VecFeature.topdelta.omegas"]
#     d["beginTopCount"] = config["MultiDoc2VecFeature.topdelta.beginTopCount"]
#     d["beginByTopdef"] = config["MultiDoc2VecFeature.topdelta.beginByTopdef"]
#     d["fusionSchedule"] = config["MultiDoc2VecFeature.topdelta.fusionSchedule"]
#     d["infBoundScore"] = config["MultiDoc2VecFeature.topdelta.infBoundScore"]
#     d["maxCount"] = config["MultiDoc2VecFeature.topdelta.maxCount"]
#     d["maxTopDelta"] = config["MultiDoc2VecFeature.topdelta.maxTopDelta"]
   

    


def postToHash(row, verbose=False, truncateNumber=12):
    post = collections.OrderedDict()
    post["window"] = row["window"]
    post["size"] = row["size"]
    post["min_count"] = row["min_count"]
    post["alpha"] = truncateFloat(row["alpha"], truncateNumber)
    post["lemma"] = row["lemma"]
    post["toLowerCase"] = row["toLowerCase"]
    post["removePunct"] = row["removePunct"]
    post["removeStopWords"] = row["removeStopWords"]
    post["sample"] = truncateFloat(row["sample"], truncateNumber)
    post["iter"] = row["iter"]
    post["negative"] = row["negative"]
    post["dataPart"] = truncateFloat(row["dataPart"], truncateNumber)
    post["data"] = str(row["data"])
    
    
    hash = strToHashCode(str(post))
    
    if verbose:
        print "post: " + str(post)
        print "hash: " + hash
    
    # Hash
    return hash

def postEquals(row1, row2):
    if \
    (
        row1["window"] == row2["window"]
        and row1["size"] == row2["size"]
        and row1["min_count"] == row2["min_count"]
        and row1["alpha"] == row2["alpha"]
        and row1["lemma"] == row2["lemma"]
        and row1["toLowerCase"] == row2["toLowerCase"]
        and row1["removePunct"] == row2["removePunct"]
        and row1["removeStopWords"] == row2["removeStopWords"]
        and row1["sample"] == row2["sample"]
        and row1["iter"] == row2["iter"]
        and row1["negative"] == row2["negative"]
        and row1["dataPart"] == row2["dataPart"]
        and row1["data"] == row2["data"]
    ):
        return True
    return False


def configToPost(config):
    # Data :
    post = collections.OrderedDict()
    post["window"] = config["Doc2VecFeature.data.window"]
    post["size"] = config["Doc2VecFeature.data.size"]
    post["min_count"] = config["Doc2VecFeature.data.min_count"]
    post["alpha"] = config["Doc2VecFeature.data.alpha"]
    post["lemma"] = config["Doc2VecFeature.data.lemma"]
    post["toLowerCase"] = config["Doc2VecFeature.data.toLowerCase"]
    post["removePunct"] = config["Doc2VecFeature.data.removePunct"]
    post["removeStopWords"] = config["Doc2VecFeature.data.removeStopWords"]
    post["sample"] = config["Doc2VecFeature.data.sample"]
    post["iter"] = config["Doc2VecFeature.data.iter"]
    post["negative"] = config["Doc2VecFeature.data.negative"]
    
    # Specific stuff :
    post["dataPart"] = config["Doc2VecFeature.data.dataPart"]
    post["data"] = config["Doc2VecFeature.data"]
    
    # Some other field :
    post["hash"] = postToHash(post)
    
    return post

def postToConfig(post):
    # Data :
    config = collections.OrderedDict()
    config["Doc2VecFeature.data.window"] = post["window"]
    config["Doc2VecFeature.data.size"] =  post["size"]
    config["Doc2VecFeature.data.min_count"] = post["min_count"]
    config["Doc2VecFeature.data.alpha"] = post["alpha"]
    config["Doc2VecFeature.data.lemma"] = post["lemma"]
    config["Doc2VecFeature.data.toLowerCase"] = post["toLowerCase"]
    config["Doc2VecFeature.data.removePunct"] = post["removePunct"]
    config["Doc2VecFeature.data.removeStopWords"] = post["removeStopWords"]
    config["Doc2VecFeature.data.sample"] = post["sample"]
    config["Doc2VecFeature.data.iter"] = post["iter"]
    config["Doc2VecFeature.data.negative"] = post["negative"]
    
    # Specific stuff :
    config["Doc2VecFeature.data.dataPart"] = post["dataPart"]
    config["Doc2VecFeature.data"] = post["data"]
    config["Doc2VecFeature"] = True
    return config
