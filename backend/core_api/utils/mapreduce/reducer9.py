#!/usr/bin/env python3
import sys

# Reducer 9: Tính trung bình cộng Giá và Tỷ lệ giảm giá cho mỗi sàn TMĐT để SO SÁNH
current_source = None
total_price = 0.0
total_discount = 0.0
count = 0

print(f"{'NGUỒN (SÀN TMĐT)'.ljust(20)}\t{'GIÁ TRUNG BÌNH'.ljust(20)}\t{'GIẢM GIÁ TB (%)'.ljust(15)}\t{'SỐ LƯỢNG SP'}")
print("-" * 80)

def print_result(source, price_sum, discount_sum, cnt):
    avg_price = price_sum / cnt
    avg_discount = discount_sum / cnt
    print(f"{source.ljust(20)}\t{avg_price:,.0f} VNĐ\t\t{avg_discount:.2f} %\t\t{cnt}")

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    
    parts = line.split('\t')
    if len(parts) != 2: continue
    
    source = parts[0]
    values = parts[1].split(',')
    if len(values) != 2: continue
    
    try:
        price = float(values[0])
        discount = float(values[1])
    except ValueError:
        continue

    if current_source == source:
        total_price += price
        total_discount += discount
        count += 1
    else:
        if current_source:
            print_result(current_source, total_price, total_discount, count)
            
        current_source = source
        total_price = price
        total_discount = discount
        count = 1

if current_source:
    print_result(current_source, total_price, total_discount, count)
