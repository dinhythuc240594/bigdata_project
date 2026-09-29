#!/usr/bin/env python3
import sys

# MapReduce 2: Đếm số lượng sản phẩm theo nguồn dữ liệu (Source)
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split('\t')
    if len(parts) >= 15:
        source = parts[13].strip()
        print(f"{source}\t1")
