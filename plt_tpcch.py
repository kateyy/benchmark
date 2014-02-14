import argparse
import benchmark

if __name__ == "__main__":
    aparser = argparse.ArgumentParser(description='Plotter for HYRISE TPC-CH Benchmark results')
    aparser.add_argument('--groupId', type=str, metavar="GROUP", default="tpcch",
                         help='Group ID for benchmark results to be plotted')
    args = vars(aparser.parse_args())

    plotter = benchmark.TPCCHPlotter(args["groupId"])

    plotter.printStatistics()




