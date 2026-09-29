#!/usr/bin/env python3
import sys
# MR 6: Average price by source
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split('\t')
    if len(parts) >= 5:
        try:
            source = parts[13]
            key = str(source)
            val = str(price)
            print(f"{key}\t{val}")
        except: pass
