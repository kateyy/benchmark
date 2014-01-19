
import httplib
import logging
import os
import requests
import shutil
import signal
import subprocess
import sys
import time

from benchmark import Benchmark
from user import User

class SkeletonUser(User):

    def __init__(self, userId, host, port, dirOutput, queryDict, **kwargs):
        User.__init__(self, userId, host, port, dirOutput, queryDict, **kwargs)

        self.perf = {}
        self.numErrors = 0

    def prepareUser(self):
        """ executed once when user starts """
        self.userStartTime = time.time()

    def runUser(self):
        """ main user activity """
        self.perf = {}
        tStart = time.time()
        
        # do something here...

        self.numErrors = 0
        tEnd = time.time()
        self.log("runs", [tEnd-tStart, tStart-self.userStartTime, self.numErrors])

    def stopUser(self):
        """ executed once after stop request was sent to user """
        pass

    def formatLog(self, key, value):
        if key == "runs":
            logStr = "%f;%f;%i" % (value[0], value[1], value[2])
            return logStr
        elif key == "failed":
            return "%f;%f;%i\n" % (value[0], value[1], value[2])
        else:
            return "%s\n" % str(value)


class SkeletonBenchmark(Benchmark):

    def __init__(self, benchmarkGroupId, benchmarkRunId, buildSettings, **kwargs):
        Benchmark.__init__(self, benchmarkGroupId, benchmarkRunId, buildSettings, **kwargs)

        self.setUserClass(SkeletonUser)

    def benchPrepare(self):
        pass

