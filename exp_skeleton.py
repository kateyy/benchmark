import argparse
import benchmark
import os
import getpass


aparser = argparse.ArgumentParser(description='Python skeleton benchmark implementation for HYRISE')
aparser.add_argument('--duration', default=10, type=int, metavar='D',
                     help='How long to run the benchmark in seconds')
aparser.add_argument('--clients', default=-1, type=int, metavar='N',
                     help='The number of blocking clients to fork (note: this overrides --clients-min/--clients-max')
aparser.add_argument('--clients-min', default=1, type=int, metavar='N',
                     help='The minimum number of blocking clients to fork')
aparser.add_argument('--clients-max', default=1, type=int, metavar='N',
                     help='The maximum number of blocking clients to fork')
aparser.add_argument('--host', default="localhost", type=str, metavar="H",
                     help='IP on which HYRISE should be run remotely')
aparser.add_argument('--remoteUser', default=getpass.getuser(), type=str, metavar="R",
                     help='remote User for remote host on which HYRISE should be run remotely')
aparser.add_argument('--remotePath', default="/home/" + getpass.getuser() +"/benchmark", type=str,
                     help='path of benchmark folder on remote host')
aparser.add_argument('--port', default=5001, type=int, metavar="P",
                     help='Port on which HYRISE should be run')
aparser.add_argument('--threads', default=0, type=int, metavar="T",
                     help='Number of server threadsto use')
aparser.add_argument('--warmup', default=3, type=int,
                     help='Warmuptime before logging is activated')
aparser.add_argument('--manual', action='store_true',
                     help='Do not build and start a HYRISE instance (note: a HYRISE server must be running on the specified port)')
aparser.add_argument('--stdout', action='store_true',
                     help='Print HYRISE server\'s stdout to console')
aparser.add_argument('--stderr', action='store_true',
                     help='Print HYRISE server\'s stderr to console')
aparser.add_argument('--rebuild', action='store_true',
                     help='Force `make clean` before each build')
aparser.add_argument('--perfdata', default=False, action='store_true',
                     help='Collect additional performance data. Slows down benchmark.')
aparser.add_argument('--json', default=False, action='store_true',
                     help='Use JSON queries instead of stored procedures.')
args = vars(aparser.parse_args())

s1 = benchmark.Settings("None", PERSISTENCY="NONE")

kwargs = {
    "remoteUser"        : args["remoteUser"],
    "remotePath"        : args["remotePath"],
    "remote"            : args["host"] is not "localhost",
    "host"              : args["host"],
    "port"              : args["port"],
    "manual"            : args["manual"],
    "warmuptime"        : args["warmup"],
    "runtime"           : args["duration"],
    "benchmarkQueries"  : [],
    "prepareQueries"    : [],
    "showStdout"        : args["stdout"],
    "showStderr"        : args["stderr"],
    "rebuild"           : args["rebuild"],
    "serverThreads"     : args["threads"],
    "collectPerfData"   : args["perfdata"],
    "useJson"           : args["json"]
}

num_clients = args["clients"]
minClients = args["clients_min"]
maxClients = args["clients_max"]

if args["clients"] > 0:
    minClients = args["clients"]
    maxClients = args["clients"]

groupId = "skeletons"

for num_clients in xrange(minClients, maxClients+1):
    runId = "numClients_%s" % num_clients
    kwargs["numUsers"] = num_clients

    b1 = benchmark.SkeletonBenchmark(groupId, runId, s1, **kwargs)

    b1.run()

