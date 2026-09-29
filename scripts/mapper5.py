#!/usr/bin/env python3
import csv
import re
import sys

reader = csv.reader(sys.stdin)

for row in reader:
  if not row:
    continue

  # Bỏ qua dòng header nếu có
  first_col = row[0].strip().lower()
  if first_col in ["record_id", "id"]:
    continue

  try:
    if len(row) <= 5:
      continue

    cat = row[5].strip()

    # Bỏ qua nếu category rỗng hoặc dính ký tự lệch dòng
    if not cat or ")" in cat:
      continue

    # Lấy và làm sạch số lượt review
    raw_rev = row[11].strip() if len(row) > 11 else "0"
    clean_rev = re.sub(r"[^\d]", "", raw_rev)
    rev_count = int(clean_rev) if clean_rev else 0

    clean_cat = cat.title()
    print(f"{clean_cat}\t{rev_count}")
  except (ValueError, IndexError):
    continue