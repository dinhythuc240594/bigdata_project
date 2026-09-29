import os
import pandas as pd
from sqlalchemy import create_engine, types

# 1. Cấu hình kết nối MySQL
DB_USER = "root"
DB_PASS = "Loc%402005mysql"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "bigdata_db"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# 2. Danh sách các file CSV cần nạp
csv_files = [
    "keyboard_products_common.csv",
    "laptop_products_common.csv",
    "monitor_products_common.csv"
]

# 3. Schema kiểu dữ liệu chuẩn cho MySQL
dtype_mapping = {
    'record_id': types.VARCHAR(100),
    'product_id': types.VARCHAR(100),
    'sku': types.VARCHAR(100),
    'name': types.VARCHAR(500),
    'brand': types.VARCHAR(100),
    'category': types.VARCHAR(50),
    'price_vnd': types.DECIMAL(15, 2),
    'old_price_vnd': types.DECIMAL(15, 2),
    'discount_amount_vnd': types.DECIMAL(15, 2),
    'discount_percent': types.DECIMAL(5, 2),
    'rating': types.DECIMAL(3, 2),
    'review_count': types.INTEGER(),
    'url': types.TEXT(),
    'source': types.VARCHAR(50),
    'crawl_date': types.DATE()
}

# 4. Vòng lặp đọc từng file và nạp vào bảng tương ứng
for file_name in csv_files:
    if not os.path.exists('data/cleaned/merged/' + file_name):
        print(f"Không tìm thấy file: {'data/cleaned/merged/' + file_name}")
        continue
    
    # Lấy tên file bỏ đuôi .csv làm tên bảng
    table_name = os.path.splitext(os.path.basename(file_name))[0]
    
    print(f"Đang xử lý file '{file_name}' -> Bảng: '{table_name}'...")
    df = pd.read_csv('data/cleaned/merged/' + file_name)
    
    # Nạp vào MySQL
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',   # 'replace' tạo mới lại bảng; hoặc dùng 'append' nếu muốn nạp nối tiếp
        index=False,
        dtype=dtype_mapping,
        chunksize=1000
    )
    print(f"Đã nạp thành công {len(df)} dòng vào bảng '{table_name}'.\n")

print("Hoàn thành nạp dữ liệu cho cả 3 bảng!")