#!/usr/bin/env python3
import sys

current_source = None
count = 0

print("SOURCE\tTOTAL_PRODUCTS")
print("-" * 30)

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    
    try:
        source, val = line.split('\t', 1)
        val = int(val)
    except ValueError:
        continue

    if current_source == source:
        count += val
    else:
        if current_source:
            print(f"{current_source}\t{count}")
        current_source = source
        count = val

if current_source == source:
    print(f"{current_source}\t{count}")
