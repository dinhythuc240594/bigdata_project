#!/usr/bin/env python3
import sys

def reducer():
    current_brand = None
    counts = {'phongvu': 0, 'thegioididong': 0}
    results = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) != 2:
            continue
            
        brand, source = parts[0], parts[1]

        if current_brand == brand:
            if source in counts:
                counts[source] += 1
        else:
            if current_brand is not None:
                total = counts['phongvu'] + counts['thegioididong']
                results.append((current_brand, total, counts['phongvu'], counts['thegioididong']))
            
            current_brand = brand
            counts = {'phongvu': 0, 'thegioididong': 0}
            if source in counts:
                counts[source] += 1

    # Lưu thương hiệu cuối cùng
    if current_brand is not None:
        total = counts['phongvu'] + counts['thegioididong']
        results.append((current_brand, total, counts['phongvu'], counts['thegioididong']))

    # Sắp xếp giảm dần theo tổng số lượng và lấy Top 10
    top_10 = sorted(results, key=lambda x: x[1], reverse=True)[:10]

    # In tiêu đề và kết quả
    print("RANK\tBRAND\tTOTAL\tPHONGVU\tTGDD")
    for rank, (brand, total, pv, tgdd) in enumerate(top_10, 1):
        print(f"{rank}\t{brand}\t{total}\t{pv}\t{tgdd}")

if __name__ == "__main__":
    reducer()