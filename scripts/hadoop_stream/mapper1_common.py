#!/usr/bin/env python3
import csv
import re
import sys

# Tập hợp các danh mục mục tiêu cần thống kê (viết thường để so sánh chuẩn xác)
TARGET_CATEGORIES = {
    "monitor": "Monitor",
    "keyboard": "Keyboard",
    "laptop": "Laptop"
}

reader = csv.reader(sys.stdin)

for row in reader:
    if not row:
        continue

    # Bỏ qua dòng header
    first_col = row[0].strip().lower()
    if first_col in ["record_id", "id"]:
        continue

    try:
        category = row[5].strip()
        raw_price = row[6].strip()

        # Bỏ qua nếu category rỗng hoặc có ký tự đóng ngoặc rác (do lệch cột)
        if not category or ")" in category:
            continue

        # Chuẩn hóa về chữ thường để kiểm tra có thuộc nhóm mục tiêu hay không
        cat_lower = category.lower()
        if cat_lower not in TARGET_CATEGORIES:
            continue

        # Làm sạch chuỗi giá: loại bỏ ký hiệu tiền tệ, chữ và dấu phân tách
        clean_price_str = re.sub(r"[^\d.]", "", raw_price)
        if not clean_price_str:
            continue

        price = float(clean_price_str)
        if price > 0:
            # Gán tên chuẩn hóa đồng nhất: Monitor, Keyboard, hoặc Laptop
            clean_cat = TARGET_CATEGORIES[cat_lower]
            print(f"{clean_cat}\t{price},1")

    except (ValueError, IndexError):
        continue