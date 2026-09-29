#!/usr/bin/env python3
import sys
# MR 5: Count products by price range
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split('\t')
    if len(parts) >= 5:
        try:
            price = float(parts[7]); range_name = '<10M' if price < 10000000 else ('10M-20M' if price <= 20000000 else '>20M')
            key = str(price)
            val = str(1)
            print(f"{key}\t{val}")
        except: pass
