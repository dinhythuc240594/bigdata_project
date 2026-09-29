#!/usr/bin/env python3
import csv
import re
import sys

reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có[cite: 8]
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    if len(row) <= 10:
      continue

    raw_rating = row[10].strip()
    if not raw_rating:
      continue

    # Lọc lấy giá trị số thập phân, loại bỏ ký tự rác nếu bị lệch cột
    match = re.search(r"^\d+(\.\d+)?", raw_rating)
    if not match:
      continue

    rating = float(match.group(0))

    # Giới hạn giá trị đánh giá hợp lệ từ 1.0 đến 5.0[cite: 8]
    if 1.0 <= rating <= 5.0:
      rating_group = f"{int(rating)}-Sao"
      print(f"{rating_group}\t1")
  except (ValueError, IndexError):
    continue