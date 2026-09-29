#!/usr/bin/env python3
import sys

current_key = None
total = 0.0
count = 0
min_price = float('inf')
max_price = 0.0

print("KEY\tMAX_PRICE")
print("-" * 30)

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    
    try:
        key, val_str = line.split('\t', 1)
        val = float(val_str)
        price = float(val_str)
    except:
        continue

    if current_key == key:
        max_price = max(max_price, price)
    else:
        if current_key:
            if "MAX_PRICE" == "AVG_PRICE": print(f"{current_key}\t{total/count:.2f}")
            elif "MAX_PRICE" == "MIN_PRICE": print(f"{current_key}\t{min_price}")
            elif "MAX_PRICE" == "MAX_PRICE": print(f"{current_key}\t{max_price}")
            else: print(f"{current_key}\t{count}")
        
        current_key = key
        total = price
        count = int(val)
        min_price = price
        max_price = price

if current_key == key:
    if "MAX_PRICE" == "AVG_PRICE": print(f"{current_key}\t{total/count:.2f}")
    elif "MAX_PRICE" == "MIN_PRICE": print(f"{current_key}\t{min_price}")
    elif "MAX_PRICE" == "MAX_PRICE": print(f"{current_key}\t{max_price}")
    else: print(f"{current_key}\t{count}")
