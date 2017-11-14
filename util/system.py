# coding: utf-8


import time
import psutil
import inspect
import os
import glob
import sys
from pympler.asizeof import asizeof

def sleep(seconds):
    time.sleep(seconds)


def removeFile(path):
    try:
        os.remove(path)
    except OSError:
        pass

def fileToStr(path):
    with open(path, 'r') as myfile:
        data = myfile.read()
    return data

def stout():
    """
    Return True if we are on stout
    """
    return (psutil.cpu_count(logical=True) > 40) and ((psutil.virtual_memory().total / (1*(10**9))) > 40)

def getUtilDirectory():
    return os.path.dirname(os.path.realpath(__file__))

def getWorkingDirectory(file=None):
    # Get the tmp directory :
    workingPath = getRootDirectory(_file_=file) + "/tmp"
    
    # Add the tmp directory if not exists :
    if not os.path.exists(workingPath):
        os.makedirs(workingPath)
        
    return workingPath

def fileExists(filePath):
    return os.path.exists(filePath)

def getMemoryUsage(d):
    return asizeof(d)

def getMemoryPercent():
    return psutil.virtual_memory().percent

def printMemoryPercent():
    print "Memory usage: " + str(getMemoryPercent()) + "%"

def getRootDirectory(_file_=None):
    # If we don't have the __file__ :
    if _file_ is None:
        # We get the last :
        rootFile = inspect.stack()[-1][1]
        folder = os.path.abspath(rootFile)
        # If we use unittest :
        if ("/pysrc" in folder) and ("org.python.pydev" in folder):
            previous = None
            # We search from left to right the case.py :
            for el in inspect.stack():
                currentFile = os.path.abspath(el[1])
                if ("unittest/case.py" in currentFile) or ("org.python.pydev" in currentFile):
                    break
                previous = currentFile
            folder = previous
        # We return the folder :
        return os.path.dirname(folder)
    else:
        # We return the folder according to specified __file__ :
        return os.path.dirname(os.path.realpath(_file_))


class GlobSortEnum():
    (
        MTIME,
        NAME,
        SIZE
    ) = range(3)

def sortedGlob(regex, caseSensitive=True, sortBy=GlobSortEnum.NAME, reverse=False):
    # case insensitive glob function :
    def insensitiveGlob(pattern):
        def either(c):
            return '[%s%s]'%(c.lower(), c.upper()) if c.isalpha() else c
        return glob.glob(''.join(map(either, pattern)))
    
    # Handle case insentive param :
    if caseSensitive:
        paths = glob.glob(regex)
    else:
        paths = insensitiveGlob(regex)
    
    # Sort the result :
    if sortBy == GlobSortEnum.NAME:
        paths.sort(reverse=reverse)
    elif sortBy == GlobSortEnum.MTIME:
        paths.sort(key=os.path.getmtime, reverse=reverse)
    elif sortBy == GlobSortEnum.SIZE:
        paths.sort(key=os.path.getsize, reverse=reverse)
    
    return paths
