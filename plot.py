#!/usr/bin/env python
import os
import matplotlib as m
if os.uname()[0] == "Darwin":
    m.use("MacOSX")
else:
    m.use("Agg")
import matplotlib.pyplot as plt

BOTTLENECK_BYTE_RATE = 1.4

def read_throughput(path):

    path += 'output.txt'
    with open(path, 'r') as f:
        line = f.read()
    return float(line) / BOTTLENECK_BYTE_RATE


def plot_throughput(xdata, ydata, output_path, label='TCP', color='red', marker='s'):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])

    data = sorted(zip(xdata, ydata), lambda x, y: 1 if x[0] - y[0] > 0 else -1)
    ax.plot(*zip(*data), label=label, color=color, marker=marker)

    ax.legend(loc=2, bbox_to_anchor=(1.05, 1))
    ax.set_ylabel("Throughput (normalized)")
    ax.set_xlabel("DoS Inter-burst Period (second)")
    plt.savefig("%s" % (output_path,))
