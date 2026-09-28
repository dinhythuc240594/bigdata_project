#!/usr/bin/env python3
import sys

for line in sys.stdin:
  line = line.strip()
  if not line:
    continue

  parts = line.split("\t")
  if len(parts) != 2:
    continue

  info = parts[1].split("|")
  if len(info) != 4:
    continue

  name, price, disc_vnd, disc_pct = info
  print(f"{name}\tGia: {price} VND\tGiam: {disc_vnd} VND\tTi le: {disc_pct}")