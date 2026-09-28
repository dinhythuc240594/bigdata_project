#!/usr/bin/env python3
import sys

cur_cat = None
total_reviews = 0

for line in sys.stdin:
  line = line.strip()
  if not line:
    continue

  parts = line.split("\t")
  if len(parts) != 2:
    continue

  cat, rev = parts
  try:
    rev = int(rev)
  except ValueError:
    continue

  if cur_cat == cat:
    total_reviews += rev
  else:
    if cur_cat is not None:
      print(f"{cur_cat}\t{total_reviews}")
    cur_cat = cat
    total_reviews = rev

if cur_cat is not None:
  print(f"{cur_cat}\t{total_reviews}")