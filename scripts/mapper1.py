#!/usr/bin/env python3
import csv
import re
import sys

reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có[cite: 4]
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    category = row[5].strip()
    raw_price = row[6].strip()

    # Bỏ qua nếu category rỗng hoặc có ký tự đóng ngoặc rác (do lệch cột)
    if not category or ")" in category:
      continue

    # Làm sạch chuỗi giá: loại bỏ ký hiệu tiền tệ, chữ và dấu phân tách
    clean_price_str = re.sub(r"[^\d.]", "", raw_price)
    if not clean_price_str:
      continue

    price = float(clean_price_str)

    if price > 0:
      # Chuẩn hóa tên danh mục về dạng Title Case
      clean_cat = category.title()
      print(f"{clean_cat}\t{price},1")
  except (ValueError, IndexError):
    continue