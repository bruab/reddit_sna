#!/usr/bin/env python3

import sys

_infile = sys.argv[1]

counts = {}
allcounts = []
with open(_infile, 'r') as infile:
    for line in infile:
        print(line)
        if "visited" in line:
            print('foo')
            num_subs = line.count(",") + 1
            allcounts.append(num_subs)
            if num_subs in counts:
                counts[num_subs] += 1
            else:
                counts[num_subs] = 1

for k in sorted(counts.keys()):
    print("\t".join([str(k), str(counts[k])]))

print("")

avg = sum(allcounts) / len(allcounts)
print("summary stats: min, mean, max", min(allcounts), avg, max(allcounts))
