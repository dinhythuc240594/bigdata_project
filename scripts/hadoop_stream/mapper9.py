#!/usr/bin/env python3
import sys
import csv

def mapper():
    # Sử dụng csv.reader để xử lý chính xác các trường chứa dấu phẩy
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        if not row:
            continue
        
        # Bỏ qua dòng tiêu đề
        if row[0] == 'record_id':
            continue
        
        # Cột source ở vị trí thứ 13 (0-indexed)
        if len(row) > 13:
            source = row[13].strip().lower()
            if source in ['phongvu', 'thegioididong']:
                # Ghi ra cặp key-value ngăn cách bởi tab: <source>\t1
                print(f"{source}\t1")

if __name__ == "__main__":
    mapper()