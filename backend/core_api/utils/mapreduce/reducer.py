#!/usr/bin/env python3
import sys

# Script Reducer - Tổng hợp dữ liệu Laptop
# Nhận đầu vào từ Mapper đã được sort theo KEY (Brand)

current_brand = None
total_price = 0.0
count = 0

print("BRAND\tAVERAGE_PRICE\tTOTAL_PRODUCTS")
print("-" * 50)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    try:
        brand, price_str = line.split('\t', 1)
        price = float(price_str)
    except ValueError:
        continue

    # Vì dữ liệu Hadoop gửi tới Reducer đã được sort theo Brand
    # Nên các dòng cùng Brand sẽ nằm liền kề nhau
    if current_brand == brand:
        total_price += price
        count += 1
    else:
        if current_brand:
            avg_price = total_price / count
            print(f"{current_brand}\t{avg_price:.2f}\t{count}")
        current_brand = brand
        total_price = price
        count = 1

# In ra brand cuối cùng sau khi hết vòng lặp
if current_brand == brand:
    avg_price = total_price / count
    print(f"{current_brand}\t{avg_price:.2f}\t{count}")
