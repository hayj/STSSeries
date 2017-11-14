# coding: utf-8


import time
class TicToc():
    # TODO human readable
    """
    This class provide 2 methods to print time during an execution
    """
    def __init__(self, marker="-->", msgSeparator=" | message: ", maxDecimal=2):
        self.startTime = None
        self.previousTime = None
        self.marker = marker
        self.msgSeparator = msgSeparator
        self.maxDecimal = maxDecimal
    
    def setMaxDecimal(self, maxDecimal):
        self.maxDecimal = maxDecimal
    
    def tic(self, msg=None):
        """
        This method start the timer and print it, or print the time between the previous tic()
        and the current tic(). You can print a message by giving it in parameters.
        It's the local duration.
        """
        if msg is None:
            msg = ""
        else:
            msg = self.msgSeparator + msg
        if self.startTime is None:
            self.startTime = time.time()
            self.previousTime = self.startTime
            print self.marker + " tictoc starts..." + msg
            return -1
        else:
            currentTime = time.time()
            diffTime = currentTime - self.previousTime
            diffTime = float(float(int(diffTime * (10**self.maxDecimal))) / float((10**self.maxDecimal)))
            print self.marker + " tic: " + str(diffTime) + " seconds" + msg # time duration from the previous tic()
            self.previousTime = currentTime
            return diffTime
            
    
    def toc(self, msg=None):
        """
        This method print the elapsed time from the first tic().
        You can print a message by giving it in parameters.
        It's the total duration.
        """
        if self.startTime is not None:
            if msg is None:
                msg = ""
            else:
                msg = self.msgSeparator + msg
            currentTime = time.time()
            diffTime = currentTime - self.startTime
            diffTime = float(float(int(diffTime * (10**self.maxDecimal))) / float((10**self.maxDecimal)))
            print self.marker + " toc total duration: " + str(diffTime) + " seconds" + msg
            return diffTime
        return -1

