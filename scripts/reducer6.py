#!/usr/bin/env python3
import sys

cur_src = None
total_p = 0.0
count = 0

for line in sys.stdin:
  line = line.strip()
  if not line:
    continue

  # Tách key và value qua dấu tab[cite: 13]
  parts = line.split("\t")
  if len(parts) != 2:
    continue

  src, val = parts
  val_parts = val.split(",")
  if len(val_parts) != 2:
    continue

  try:
    p = float(val_parts[0])
    c = int(val_parts[1])
  except ValueError:
    continue

  if cur_src == src:
    total_p += p
    count += c
  else:
    if cur_src is not None and count > 0:
      avg_p = total_p / count
      print(f"{cur_src}\t{count}\t{avg_p:.0f}")
    cur_src = src
    total_p = p
    count = c

# In kết quả cho nguồn cuối cùng[cite: 13]
if cur_src is not None and count > 0:
  avg_p = total_p / count
  print(f"{cur_src}\t{count}\t{avg_p:.0f}")