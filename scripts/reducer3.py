#!/usr/bin/env python3
import sys

cur_brand = None
total_disc_vnd = 0.0
total_disc_pct = 0.0
count = 0

for line in sys.stdin:
  line = line.strip()
  if not line:
    continue

  parts = line.split("\t")
  if len(parts) != 2:
    continue

  brand, val = parts
  val_parts = val.split(",")
  if len(val_parts) != 3:
    continue

  try:
    d_vnd = float(val_parts[0])
    d_pct = float(val_parts[1])
    c = int(val_parts[2])
  except ValueError:
    continue

  if cur_brand == brand:
    total_disc_vnd += d_vnd
    total_disc_pct += d_pct
    count += c
  else:
    if cur_brand is not None and count > 0:
      avg_vnd = total_disc_vnd / count
      avg_pct = total_disc_pct / count
      print(f"{cur_brand}\t{avg_vnd:.0f}\t{avg_pct:.2f}\t{count}")
    cur_brand = brand
    total_disc_vnd = d_vnd
    total_disc_pct = d_pct
    count = c

# In bản ghi cho hãng cuối cùng
if cur_brand is not None and count > 0:
  avg_vnd = total_disc_vnd / count
  avg_pct = total_disc_pct / count
  print(f"{cur_brand}\t{avg_vnd:.0f}\t{avg_pct:.2f}\t{count}")