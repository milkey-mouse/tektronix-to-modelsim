#!/usr/bin/env python3
from PIL import Image
import numpy as np
import sys

img = Image.open("ir_data/0.png")

mid = img.height / 2
img = img.crop((0, mid, img.width, mid+1))
#img.save("cropped.png")

array = np.array(img)[0]
edges = [i for i, d in enumerate(abs(p - [66, 0, 66]).sum() for p in array) if d < 100]

val = True
print("starting val", val)
last = 0
widths = [set(),set()]
for e in edges:
    width = (e - last) / 10 # 10 px = 1 ms
    widths[int(val)].add(width)
    print(val, "for", width, "ms")
    val = not val
    last = e
print("final val", val)
print("total length", (edges[-1] - edges[0]) / 10, "ms")
print("widths:", widths)
