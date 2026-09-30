#!/usr/bin/env python3
import sys

cur_brand = None
total_count = 0

for line in sys.stdin:
  line = line.strip()
  if not line:
    continue

  parts = line.split("\t")
  if len(parts) != 2:
    continue

  brand, c = parts
  try:
    c = int(c)
  except ValueError:
    continue

  if cur_brand == brand:
    total_count += c
  else:
    if cur_brand is not None:
      print(f"{cur_brand}\t{total_count}")
    cur_brand = brand
    total_count = c

if cur_brand is not None:
  print(f"{cur_brand}\t{total_count}")