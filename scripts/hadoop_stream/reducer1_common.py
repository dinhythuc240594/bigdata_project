#!/usr/bin/env python3
import sys

cur_cat = None
total_price = 0.0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    # Tách key và value qua dấu tab
    parts = line.split("\t")
    if len(parts) != 2:
        continue

    cat, val = parts
    val_parts = val.split(",")
    if len(val_parts) != 2:
        continue

    try:
        p = float(val_parts[0])
        c = int(val_parts[1])
    except ValueError:
        continue

    if cur_cat == cat:
        total_price += p
        count += c
    else:
        if cur_cat is not None and count > 0:
            avg_p = total_price / count
            print(f"{cur_cat}\t{count}\t{avg_p:.0f}")
        cur_cat = cat
        total_price = p
        count = c

# In kết quả cho danh mục cuối cùng
if cur_cat is not None and count > 0:
    avg_p = total_price / count
    print(f"{cur_cat}\t{count}\t{avg_p:.0f}")