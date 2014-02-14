
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
            self.log("queries", [id, tEnd-tStart, tStart-self.userStartTime])

        self.numErrors = 0

    def stopUser(self):
        """ executed once after stop request was sent to user """
        pass

    def fireQueryId(self, queryId, queryArgs={"papi": "NO_PAPI"}, sessionContext=None, autocommit=False, stored_procedure=None):
        self.fireQuery(self._queryDict[queryId], queryArgs, sessionContext, autocommit, stored_procedure)

    def formatLog(self, key, value):
        if key == "queries":  # log: id, duration, start time
            logStr = "%i;%f;%f\n" % (value[0], value[1], value[2])
            return logStr
        else:
            print "invalid key for log event: %s" % key
            return "%s\n" % str(value)


class TPCCHBenchmark(Benchmark):

    def __init__(self, queryIds, benchmarkGroupId, benchmarkRunId, buildSettings, useMysqlTables=False, **kwargs):
        Benchmark.__init__(self, benchmarkGroupId, benchmarkRunId, buildSettings, **kwargs)

        self.setUserClass(TPCCHUser)

        self._dirHyriseDB = os.path.join(os.getcwd(), "hyrise/test")
        os.environ['HYRISE_DB_PATH'] = self._dirHyriseDB

        self.useMysqlTables = useMysqlTables
        queryBaseName = ""
        if useMysqlTables:
            queryBaseName = "hyrise/test/tpcch/mysqlQuery%s.json"
        else:
            queryBaseName = "hyrise/test/tpcch/query%s.json"

        for id in queryIds:
            self.addQueryFile(id, queryBaseName % id)

    def benchPrepare(self):
        if self.useMysqlTables:
            tpccTableLoad = open("hyrise/test/tpcc/load_tpcc_mysql_tables.json").read()
            print "loading tables from mysql host..."
            self.fireQuery(tpccTableLoad)
            print " ...done"
        else:
            tpccTableLoad = open("hyrise/test/tpcc/load_tpcc_csv_tables.json").read()
            self.fireQuery(tpccTableLoad)
