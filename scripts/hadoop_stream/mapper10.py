#!/usr/bin/env python3
import sys
import csv

def mapper():
    reader = csv.reader(sys.stdin)
    for row in reader:
        if not row:
            continue
        
        # Bỏ qua dòng tiêu đề
        if row[0] == 'record_id':
            continue
        
        # Cột brand (vị trí 4) và source (vị trí 13)
        if len(row) > 13:
            brand = row[4].strip().upper()  # Chuẩn hóa về chữ in hoa (MSI/Msi, Gigabyte/GIGABYTE)
            source = row[13].strip().lower()
            
            if brand and source in ['phongvu', 'thegioididong']:
                # Key: brand, Value: nguồn bán
                print(f"{brand}\t{source}")

if __name__ == "__main__":
    mapper()