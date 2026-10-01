import os
import glob
import pandas as pd
from sqlalchemy import create_engine, types

# 1. Cấu hình kết nối MySQL (thay đổi thông tin của bạn)
DB_USER = "root"
DB_PASS = "123456789"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "bigdata_project"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")

FILES_MAPPING = {
    "laptop_specs": "C:/Project_Python/bigdata_project/data/cleaned/merged/laptop_specs.csv",
    "keyboard_specs": "C:/Project_Python/bigdata_project/data/cleaned/merged/keyboard_specs.csv",
    "monitor_specs": "C:/Project_Python/bigdata_project/data/cleaned/merged/monitor_specs.csv",
}

for table_name, file_path in FILES_MAPPING.items():
    print(f"Đang đọc dữ liệu cho bảng {table_name}...")
    df = pd.read_csv(file_path)

    # Đẩy dữ liệu vào bảng (chunksize giúp tránh tràn RAM nếu file nặng)
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",  # 'append' để thêm dữ liệu, hoặc 'replace' để tạo mới bảng
        index=False,
        chunksize=10000,
    )
    print(f"-> Đã nạp thành công {len(df)} dòng vào bảng {table_name}.")