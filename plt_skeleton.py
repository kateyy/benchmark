import argparse
import benchmark

if __name__ == "__main__":
	aparser = argparse.ArgumentParser(description='Plotter for HYRISE Skeleton Benchmark results')
	aparser.add_argument('groupId', type=str, metavar="GROUP",
	                     help='Group ID for benchmark results to be plotted')
	aparser.add_argument('--stats', action='store_true',
	                     help='Print run statistics and exit')
	args = vars(aparser.parse_args())

	plotter = benchmark.Plotter(args["groupId"])

	if args["stats"]:
		plotter.printStatistics()
		exit()

	plotter.plotResponseTimesVaryingUsers()

	plotter.plotResponseTimeFrequencies()

	#plotter.plotTotalThroughput()

	#plotter.plotTotalFails()

	#plotter.plotTransactionResponseTimes()

