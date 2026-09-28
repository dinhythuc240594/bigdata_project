#!/usr/bin/env python3
import sys

cur_seg = None
total = 0

for line in sys.stdin:
  line = line.strip()
  if not line:
    continue

  # Tách segment và count qua tab[cite: 15]
  parts = line.split("\t")
  if len(parts) != 2:
    continue

  seg, c = parts
  try:
    c = int(c)
  except ValueError:
    continue

  if cur_seg == seg:
    total += c
  else:
    if cur_seg is not None:
      print(f"{cur_seg}\t{total}")
    cur_seg = seg
    total = c

# In phân khúc cuối cùng[cite: 15]
if cur_seg is not None:
  print(f"{cur_seg}\t{total}")