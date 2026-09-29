#!/usr/bin/env python3
import sys

# Script Mapper - Phân tích dữ liệu sản phẩm
# Cấu trúc bảng: brand, category, date, discount, discount_rate, name, original_price, price, product_id, rating, sku, sold, sold_info, source, url

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split('\t')
    
    if len(parts) >= 15:
        brand = parts[0].strip().upper()
        price_str = parts[7].strip()
        
        try:
            price = float(price_str)
            if price > 0:
                print(f"{brand}\t{price}")
        except ValueError:
            pass
