#!/usr/bin/env python3
import csv
import re
import sys

# Bảng chuẩn hóa tên nguồn/sàn thương mại điện tử phổ biến
SOURCE_MAP = {
    "shopee": "Shopee",
    "tiki": "Tiki",
    "lazada": "Lazada",
    "cellphones": "CellphoneS",
    "fpt": "FPTShop",
    "fptshop": "FPTShop",
    "tgdd": "TGDD",
    "thegioididong": "TGDD",
    "phongvu": "PhongVu",
}

reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có[cite: 12]
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    if len(row) <= 13:
      continue

    source = row[13].strip()
    raw_price = row[6].strip()

    # Bỏ qua nếu source rỗng hoặc dính ký tự lệch dòng[cite: 12]
    if not source or ")" in source:
      continue

    # Làm sạch chuỗi giá: loại bỏ ký hiệu tiền tệ và các ký tự không phải số/chấm[cite: 12]
    clean_price_str = re.sub(r"[^\d.]", "", raw_price)
    if not clean_price_str:
      continue

    price = float(clean_price_str)

    if price > 0:
      # Chuẩn hóa tên nguồn[cite: 12]
      clean_source = SOURCE_MAP.get(source.lower(), source.title())
      print(f"{clean_source}\t{price},1")
  except (ValueError, IndexError):
    continue