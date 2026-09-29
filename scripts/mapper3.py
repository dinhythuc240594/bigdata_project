#!/usr/bin/env python3
import csv
import re
import sys

# Regex nhận diện thông số RAM/bộ nhớ bị trôi vào cột brand
RAM_PATTERN = re.compile(r"^\d+\s*(gb|g|tb)$", re.IGNORECASE)

# Bảng chuẩn hóa tên các hãng công nghệ phổ biến
BRAND_MAP = {
    "asus": "Asus",
    "acer": "Acer",
    "dell": "Dell",
    "hp": "HP",
    "lenovo": "Lenovo",
    "lg": "LG",
    "msi": "MSI",
    "apple": "Apple",
    "macbook": "MacBook",
    "gigabyte": "Gigabyte",
}


def clean_number(value_str):
  """Làm sạch chuỗi chứa số, bỏ ký tự %, tiền tệ và phân cách nghìn."""
  if not value_str:
    return 0.0
  cleaned = re.sub(r"[^\d.]", "", value_str.strip())
  return float(cleaned) if cleaned else 0.0


reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có[cite: 6]
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    brand = row[4].strip()

    # Bỏ qua nếu rỗng, là thông số RAM hoặc chứa ký tự lệch dòng
    if not brand or RAM_PATTERN.match(brand) or ")" in brand:
      continue

    disc_vnd = clean_number(row[8]) if len(row) > 8 else 0.0
    disc_pct = clean_number(row[9]) if len(row) > 9 else 0.0

    # Chỉ tính các bản ghi có giảm giá[cite: 6]
    if disc_vnd > 0 or disc_pct > 0:
      # Chuẩn hóa tên thương hiệu
      clean_brand = BRAND_MAP.get(brand.lower(), brand.title())
      print(f"{clean_brand}\t{disc_vnd},{disc_pct},1")
  except (ValueError, IndexError):
    continue