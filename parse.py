#!/usr/bin/env python3
from collections import deque
from itertools import groupby
from math import isclose
from sys import stderr
import sys
import csv

TIMESTEP = 0.000001
CLOCK_Hz = 50e6  # 50 MHz
#CLOCK_Hz = 38.222e3
#CLOCK_Hz = 50e6/1308
INPUT = "sim:/ir_decoder/ir_in"

def histogram(data, step, width=100):
    scale = width / max(sum(1 for _ in g) for _, g in groupby(data, key=lambda s: round(s / step)))
    for k, g in groupby(data, key=lambda s: round(s / step)):
        try:
            (count, first), *_, (count, last) = enumerate(g)
        except ValueError:
            continue
            first = k * step
            last = (k+1) * step
            count = 1
        bar = "X" * int(count * scale)
        print(f"{first:.3f}-{last:.3f} {bar}", file=stderr)

samples = []
sample_offset = 0
for filename in sys.argv[1:]:
    with open(filename, newline="") as f:
        # skip header
        for line in f:
            if line.rstrip() == "TIME,CH3":
                break
        else:
            assert(False)

        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        for time, voltage in reader:
            if time != "" and voltage != "":
                samples.append((time + sample_offset, voltage))

    sample_offset = samples[-1][0]

# find threshold value where dV/dt is highest in sorted list
sorted_samples = sorted(v for t, v in samples)
threshold = sum(max(zip(sorted_samples, sorted_samples[1:]), key=lambda x: x[1] - x[0])) / 2
histogram(sorted_samples, 0.01)
print("threshold voltage: {:.3f}".format(threshold), file=stderr)
del sorted_samples

# convert samples to boolean with threshold value
samples = [(t, v >= threshold) for t, v in samples]

# TODO: better check for hysteresis
for window in zip(samples, samples[1:], samples[2:]):
    assert(window != (True, False, True))
    assert(window != (False, True, False))

cycles_agg = []
last = samples[0]
for t, v in samples[1:]:
    if v != last[1]:
        ms = (t - last[0]) * 1000
        cycles = round((t - last[0]) * CLOCK_Hz)
        cycles_agg.append(cycles)
        print(f"{last[1]} for {ms:.3f}ms ({cycles} cycles @ {CLOCK_Hz} Hz)", file=stderr)
        print(f"force -freeze {INPUT} {int(v)} @{round(t*1e12)}ps")
        last = (t, v)

histogram(sorted(cycles_agg), 100)
