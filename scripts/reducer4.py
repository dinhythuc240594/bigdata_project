#!/usr/bin/env python3
import sys

cur_rating = None
total_count = 0

for line in sys.stdin:
  line = line.strip()
  if not line:
    continue

  parts = line.split("\t")
  if len(parts) != 2:
    continue

  rating, c = parts
  try:
    c = int(c)
  except ValueError:
    continue

  if cur_rating == rating:
    total_count += c
  else:
    if cur_rating is not None:
      print(f"{cur_rating}\t{total_count}")
    cur_rating = rating
    total_count = c

if cur_rating is not None:
  print(f"{cur_rating}\t{total_count}")