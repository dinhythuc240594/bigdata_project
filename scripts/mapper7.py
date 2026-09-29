#!/usr/bin/env python3
import csv
import re
import sys

reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có[cite: 14]
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    if len(row) <= 6:
      continue

    raw_price = row[6].strip()

    # Làm sạch chuỗi giá: loại bỏ ký hiệu tiền tệ và các ký tự không phải số/dấu chấm[cite: 14]
    clean_price_str = re.sub(r"[^\d.]", "", raw_price)
    if not clean_price_str:
      continue

    price = float(clean_price_str)

    # Chỉ phân loại các sản phẩm có giá hợp lệ (> 0)
    if price <= 0:
      continue

    # Phân khúc giá[cite: 14]
    if price < 2000000:
      segment = "1. Gia re (< 2 Trieu)"
    elif price <= 10000000:
      segment = "2. Pho thong (2 - 10 Trieu)"
    elif price <= 25000000:
      segment = "3. Trung cap (10 - 25 Trieu)"
    else:
      segment = "4. Cao cap (> 25 Trieu)"

    print(f"{segment}\t1")
  except (ValueError, IndexError):
    continue