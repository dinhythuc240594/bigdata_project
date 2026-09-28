#!/usr/bin/env python3
import csv
import re
import sys

# Regex nhận diện thông số RAM/ổ cứng bị trôi vào cột (vd: 8GB, 16G, 32 GB, 1TB)
RAM_PATTERN = re.compile(r"^\d+\s*(gb|g|tb)$", re.IGNORECASE)

# Map chuẩn hóa tên các hãng công nghệ phổ biến
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

reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    brand = row[4].strip()

    # Bỏ qua nếu rỗng, là thông số RAM hoặc chứa ký tự lệch dòng
    if not brand or RAM_PATTERN.match(brand) or ")" in brand:
      continue

    # Chuẩn hóa tên hãng
    brand_lower = brand.lower()
    clean_brand = BRAND_MAP.get(brand_lower, brand.title())

    print(f"{clean_brand}\t1")
  except IndexError:
    continue