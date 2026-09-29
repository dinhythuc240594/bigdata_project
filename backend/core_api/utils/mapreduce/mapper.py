#!/usr/bin/env python3
import sys

# Script Mapper - Phân tích dữ liệu Laptop
# Cấu trúc bảng: record_id,product_id,sku,name,brand(4),category,price(6),...

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split(',')
    
    # Sqoop xuất dữ liệu không có dấu ngoặc kép bọc chuỗi,
    # mà cột Tên sản phẩm (ở giữa) lại có chứa rất nhiều dấu phẩy (vd: 16GB, 512GB).
    # Việc này làm cột phía sau bị lệch index.
    # Giải pháp: Lấy Tên Hãng từ đầu mảng (index 0) và Giá từ cuối mảng đếm ngược lên (index -8)
    if len(parts) >= 10:
        brand = parts[0].strip().upper()
        price_str = parts[-8].strip()
        
        try:
            price = float(price_str)
            if price > 0:
                print(f"{brand}\t{price}")
        except ValueError:
            pass
