#!/usr/bin/env python3
import sys

# MR 9: So sánh giá trung bình và tỷ lệ giảm giá giữa các sàn TMĐT (Nguồn/Source)
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split('\t')
    
    # Cấu trúc: brand, category, date, discount, discount_rate, name, original_price, price, product_id, rating, sku, sold, sold_info, source, url
    if len(parts) >= 15:
        source = parts[13].strip().upper()
        if not source: source = "UNKNOWN"
        
        price_str = parts[7].strip()
        discount_rate_str = parts[4].strip()
        
        try:
            price = float(price_str)
            discount_rate = float(discount_rate_str)
            if price > 0:
                print(f"{source}\t{price},{discount_rate}")
        except ValueError:
            pass
