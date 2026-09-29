import sys

# MapReduce 2: Đếm số lượng sản phẩm theo nguồn dữ liệu (Source)
# Mục đích: Phân tích xem data thu thập được phần lớn đến từ trang web nào (PhongVu, TheGioiDiDong, FPTShop, v.v...)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split(',')
    
    # Nguồn thu thập (Source) thường nằm ở cột áp chót (index -2) trong dữ liệu raw MySQL
    if len(parts) >= 10:
        source = parts[-2].strip()
        
        # Bỏ qua dòng header nếu có
        if source.upper() != 'SOURCE' and source != '':
            # Xuất ra key-value: Nguồn \t 1
            print(f"{source}\t1")
