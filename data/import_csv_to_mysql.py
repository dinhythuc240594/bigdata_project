import os
import glob
import pandas as pd
from sqlalchemy import create_engine, types

# 1. Cấu hình kết nối MySQL (thay đổi thông tin của bạn)
DB_USER = "root"
DB_PASS = "123456789"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "bigdata_db"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")

# 2. Danh sách 3 file CSV
csv_files = [
    "keyboard_products_common.csv",
    "laptop_products_common.csv",
    "monitor_products_common.csv"
]

# 3. Đọc và gộp 3 file vào DataFrame chung
df_list = []
for file_name in csv_files:
    if os.path.exists('data/cleaned/merged/' + file_name):
        df = pd.read_csv('data/cleaned/merged/' + file_name)
        df_list.append(df)
        print(f"Đã đọc {file_name}: {len(df)} dòng.")

combined_df = pd.concat(df_list, ignore_index=True)

# 4. Định nghĩa kiểu dữ liệu MySQL tối ưu cho báo cáo
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

# 5. Import dữ liệu vào bảng 'products'
combined_df.to_sql(
    name='products',
    con=engine,
    if_exists='replace', # Dùng 'replace' để tạo mới bảng, hoặc 'append' nếu đã có bảng
    index=False,
    dtype=dtype_mapping,
    chunksize=1000
)

print(f"Hoàn thành nạp {len(combined_df)} bản ghi vào MySQL!")