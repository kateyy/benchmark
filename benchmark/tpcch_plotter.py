import os
from pylab import *


# const factor to convert result times from logs
# if papi is deactivated, logs contain time in secons
# we want ms, so factor ist 1000
z = 1000

class TPCCHPlotter:

    def __init__(self, benchmarkGroupId):
        self._groupId = benchmarkGroupId
        self._dirOutput = os.path.join(os.getcwd(), "plots", str(self._groupId))
        self._varyingParameter = None
        self._runs = self._collect()
        self._buildIds = self._runs[self._runs.keys()[0]].keys()

        if not os.path.isdir(self._dirOutput):
            os.makedirs(self._dirOutput)

    def tick(self):
        sys.stdout.write('.')
        sys.stdout.flush()

    def printStatistics(self):
        for runId, runData in self._runs.iteritems():
            numUsers = runData[runData.keys()[0]]["numUsers"]
            print "Run ID: %s [%s users]" % (runId, numUsers)
            print "=============================="
            for buildId, buildData in runData.iteritems():
                if buildData == {'numUsers': 0, 'queryStats': {}}:
                    continue
                print "|\n+-- Build ID: %s" % buildId
                print "|"
                totalRuns = 0.0
                totalTime = 0.0
                for queryID, queryData in buildData["queryStats"].iteritems():
                    totalRuns += queryData["totalRuns"]
                    totalTime += queryData["userTime"]
                for queryID, queryData in buildData["queryStats"].iteritems():
                    print "|     -------------------------------------------------------------------------------------------"
                    print "|     Query: {:2s} queries/s: {:05.2f}, min: {:05.2f}ms, max: {:05.2f}ms, avg: {:05.2f}ms, med: {:05.2f}ms".format(queryID, float(queryData["totalRuns"])*z / totalTime, queryData["rtMin"], queryData["rtMax"], queryData["rtAvg"], queryData["rtMed"])
                print "|     -------------------------------------------------------------------------------------------"
                print "|     total:            %1.2f queries/s\n" % (totalRuns*z / totalTime)
                print "totalRuns: %i, totalTime: %1.2fs" % (totalRuns, totalTime / z)

    def _collect(self):
        runs = {}
        dirResults = os.path.join(os.getcwd(), "results", self._groupId)
        if not os.path.isdir(dirResults):
            raise Exception("Group result directory '%s' not found!" % dirResults)

        # --- Runs --- #
        for run in os.listdir(dirResults):
            dirRun = os.path.join(dirResults, run)
            if os.path.isdir(dirRun):
                self._collectRun(runs, run, dirRun)

        return runs

    def _collectRun(self, runs, currentRun, dirRun):
        runs[currentRun] = {}

        # --- Builds --- #
        for build in os.listdir(dirRun):
            self.tick()
            dirBuild = os.path.join(dirRun, build)
            if os.path.isdir(dirBuild):
                self._collectBuild(runs, currentRun, build, dirBuild)

    def _collectBuild(self, runs, run, build, dirBuild):
        # -- Count Users --- #
        numUsers = 0
        for user in os.listdir(dirBuild):
            dirUser = os.path.join(dirBuild, user)
            if os.path.isdir(dirUser):
                numUsers += 1

        queryStats = {}
        opStats = {}
        hasOpData = False

        # -- Users --- #
        for user in os.listdir(dirBuild):
            dirUser = os.path.join(dirBuild, user)
            if os.path.isdir(dirUser):
                self._collectUser(user, dirUser, numUsers, opStats, queryStats)

        for queryId, queryData in queryStats.iteritems():
            allRuntimes = [a[1] for a in queryData["rtTuples"]]
            queryStats[queryId]["rtTuples"].sort(key=lambda a: a[0])
            queryStats[queryId]["rtRaw"] = allRuntimes
            queryStats[queryId]["rtMin"] = amin(allRuntimes)
            queryStats[queryId]["rtMax"] = amax(allRuntimes)
            queryStats[queryId]["rtAvg"] = average(allRuntimes)
            queryStats[queryId]["rtMed"] = median(allRuntimes)
            queryStats[queryId]["rtStd"] = std(allRuntimes)
            for opId, opData in opStats[queryId].iteritems():
                opStats[queryId][opId]["avgRuns"] = average([a[0] for a in opData["rtTuples"]])
                opStats[queryId][opId]["rtMin"] = amin([a[1] for a in opData["rtTuples"]])
                opStats[queryId][opId]["rtMax"] = amax([a[1] for a in opData["rtTuples"]])
                opStats[queryId][opId]["rtAvg"] = average([a[1] for a in opData["rtTuples"]])
                opStats[queryId][opId]["rtMed"] = median([a[1] for a in opData["rtTuples"]])
                opStats[queryId][opId]["rtStd"] = std([a[1] for a in opData["rtTuples"]])
            queryStats[queryId]["operators"] = opStats[queryId]
        if queryStats != {}:
            runs[run][build] = {"queryStats": queryStats, "numUsers": numUsers}

    def _collectUser(self, user, dirUser, numUsers, opStats, queryStats):
        if not os.path.isfile(os.path.join(dirUser, "queries.log")):
            print "WARNING: no query log found in %s!" % dirUser
            return
        for rawline in open(os.path.join(dirUser, "queries.log")):
            linedata = rawline.split(";")
            if len(linedata) != 3:
                print "invalid line in queries.log in: %s" % dirUser
                continue

            queryId     = linedata[0]
            runtime     = float(linedata[1]) * z # convert from s to ms
            starttime   = float(linedata[2]) * z # convert from s to ms

            opStats.setdefault(queryId, {})
            queryStats.setdefault(queryId,{
                "totalTime": 0.0,
                "userTime":  0.0,
                "totalRuns": 0,
                "totalFail": 0,
                "rtTuples":  [],
                "rtMin":     0.0,
                "rtMax":     0.0,
                "rtAvg":     0.0,
                "rtMed":     0.0,
                "rtStd":     0.0
            })
            queryStats[queryId]["totalTime"] += runtime
            queryStats[queryId]["userTime"]  += runtime / float(numUsers)
            queryStats[queryId]["totalRuns"] += 1
            queryStats[queryId]["rtTuples"].append((starttime, runtime))

            if len(linedata) > 3:
                for opStr in linedata[3:]:
                    opData = opStr.split(",")
                    opStats[queryId].setdefault(opData[0], {
                        "rtTuples":  [],
                        "avgRuns":   0.0,
                        "rtMin":     0.0,
                        "rtMax":     0.0,
                        "rtAvg":     0.0,
                        "rtMed":     0.0,
                        "rtStd":     0.0
                    })
                    opStats[queryId][opData[0]]["rtTuples"].append((float(opData[1]), float(opData[2])))

