
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

class TPCCHUser(User):

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

        for id in self._queryDict.keys():
            self.fireQueryId(id)

        self.numErrors = 0
        tEnd = time.time()
        self.log("succeeded", [tEnd-tStart, tStart-self.userStartTime])

    def stopUser(self):
        """ executed once after stop request was sent to user """
        pass

    def fireQueryId(self, queryId, queryArgs={"papi": "NO_PAPI"}, sessionContext=None, autocommit=False, stored_procedure=None):
        self.fireQuery(self._queryDict[queryId], queryArgs, sessionContext, autocommit, stored_procedure)

    def formatLog(self, key, value):
        if key == "succeeded":
            logStr = "%f;%f\n" % (value[0], value[1])
            return logStr
        elif key == "failed":
            return "%f;%f;%i\n" % (value[0], value[1], value[2])
        else:
            return "%s\n" % str(value)


class TPCCHBenchmark(Benchmark):

    def __init__(self, benchmarkGroupId, benchmarkRunId, buildSettings, **kwargs):
        Benchmark.__init__(self, benchmarkGroupId, benchmarkRunId, buildSettings, **kwargs)

        self.setUserClass(TPCCHUser)

        self._dirHyriseDB = os.path.join(os.getcwd(), "hyrise/test")
        os.environ['HYRISE_DB_PATH'] = self._dirHyriseDB

    def benchPrepare(self):
        tpccTableLoad = open("hyrise/test/tpcc/load_tpcc_tables.json").read()
        self.addQueryFile(1, "hyrise/test/tpcch/query1.json")
        self.addQueryFile(3, "hyrise/test/tpcch/query1.json")
        self.addQueryFile(6, "hyrise/test/tpcch/query1.json")
        self.addQueryFile(18, "hyrise/test/tpcch/query1.json")
        self.addQueryFile(19, "hyrise/test/tpcch/query1.json")

        self.fireQuery(tpccTableLoad)

