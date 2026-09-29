#!/usr/bin/env python3
import csv
import re
import sys


def clean_number(value_str):
  """Làm sạch chuỗi chứa số, loại bỏ đơn vị tiền tệ, % và ký tự đặc biệt."""
  if not value_str:
    return 0.0
  cleaned = re.sub(r"[^\d.]", "", value_str.strip())
  return float(cleaned) if cleaned else 0.0


reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có[cite: 16]
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    if len(row) <= 9:
      continue

    raw_name = row[3].strip()
    if not raw_name:
      continue

    disc_vnd = clean_number(row[8]) if len(row) > 8 else 0.0
    disc_pct = clean_number(row[9]) if len(row) > 9 else 0.0
    price = clean_number(row[6]) if len(row) > 6 else 0.0

    # Điều kiện lọc sản phẩm giảm giá sâu[cite: 16]
    if disc_pct >= 30.0 or disc_vnd >= 5000000.0:
      # Thay thế ký tự tab và phân cách pipe | để tránh vỡ format phân tách dòng[cite: 16]
      clean_name = raw_name.replace("\t", " ").replace("|", "-")
      print(
          f"HIGH_DISCOUNT\t{clean_name}|{price:.0f}|{disc_vnd:.0f}|{disc_pct:.1f}%"
      )
  except (ValueError, IndexError):
    continue