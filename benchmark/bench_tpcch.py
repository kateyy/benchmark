
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

        for id in self._queryDict.keys():
            tStart = time.time()
            self.fireQueryId(id)
            tEnd = time.time()
            self.log("succeeded", [id, tEnd-tStart, tStart-self.userStartTime])

        self.numErrors = 0

    def stopUser(self):
        """ executed once after stop request was sent to user """
        pass

    def fireQueryId(self, queryId, queryArgs={"papi": "NO_PAPI"}, sessionContext=None, autocommit=False, stored_procedure=None):
        self.fireQuery(self._queryDict[queryId], queryArgs, sessionContext, autocommit, stored_procedure)

    def formatLog(self, key, value):
        if key == "succeeded":
            logStr = "id:%i;%f;%f\n" % (value[0], value[1], value[2])
            return logStr
        elif key == "failed":
            return "id:%i;%f;%f\n" % (value[0], value[1], value[2])
        else:
            return "%s\n" % str(value)


class TPCCHBenchmark(Benchmark):

    def __init__(self, queryIds, benchmarkGroupId, benchmarkRunId, buildSettings, **kwargs):
        Benchmark.__init__(self, benchmarkGroupId, benchmarkRunId, buildSettings, **kwargs)

        self.setUserClass(TPCCHUser)

        self._dirHyriseDB = os.path.join(os.getcwd(), "hyrise/test")
        os.environ['HYRISE_DB_PATH'] = self._dirHyriseDB

        for id in queryIds:
            self.addQueryFile(id, "hyrise/test/tpcch/query%s.json" % id)

    def benchPrepare(self):
        tpccTableLoad = open("hyrise/test/tpcc/load_tpcc_tables.json").read()
        self.fireQuery(tpccTableLoad)
