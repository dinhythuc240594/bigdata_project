#!/usr/bin/env python3
import sys
# MR 4: Max price by brand
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split('\t')
    if len(parts) >= 5:
        try:
            brand = parts[0]
            key = str(brand)
            val = str(price)
            print(f"{key}\t{val}")
        except: pass
