from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, 
    DoubleType, IntegerType, DecimalType
)
from pyspark.sql.functions import avg, max, min, sum, col, round, lower, trim

# 1. Khởi tạo Spark Session
spark = SparkSession.builder \
    .appName("KeyboardProductAnalysis") \
    .getOrCreate()

# 2. Định nghĩa Schema chuẩn xác theo cấu trúc 15 cột
schema = StructType([
    StructField("record_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("sku", StringType(), True),
    StructField("name", StringType(), True),
    StructField("brand", StringType(), True),
    StructField("category", StringType(), True),
    StructField("price_vnd", DoubleType(), True),
    StructField("old_price_vnd", DoubleType(), True),
    StructField("discount_amount_vnd", DoubleType(), True),
    StructField("discount_percent", DoubleType(), True),
    StructField("rating", DoubleType(), True),
    StructField("review_count", IntegerType(), True),
    StructField("url", StringType(), True),
    StructField("source", StringType(), True),
    StructField("crawl_date", StringType(), True)
])

# 3. Đọc dữ liệu từ HDFS, loại bỏ dòng lỗi và chuyển chữ "null" thành giá trị null thực sự
raw_df = spark.read.csv(
    "hdfs:///user/hadoopthuc/products/*",
    header=False,
    schema=schema,
    nullValue="null",
    emptyValue="",
    quote="\"",
    escape="\"",
    mode="DROPMALFORMED"
)

# 4. Làm sạch & Lọc riêng dòng sản phẩm KEYBOARD
keyboard_df = raw_df \
    .filter(col("category").isNotNull()) \
    .filter(lower(trim(col("category"))) == "keyboard") \
    .filter(col("product_id").isNotNull()) \
    .filter(col("price_vnd").isNotNull()) \
    .dropDuplicates(["record_id"])

# Lưu vào cache để tối ưu hiệu năng khi thực hiện nhiều phép tính
keyboard_df.cache()

print("========== SAMPLE KEYBOARD DATA ==========")
keyboard_df.select("product_id", "brand", "name", "price_vnd", "discount_amount_vnd", "rating") \
    .show(10, truncate=False)

print("========== TOTAL KEYBOARD PRODUCTS ==========")
print(f"Tổng số bàn phím hợp lệ: {keyboard_df.count()}")


# ========================================================
# 1. SỐ LƯỢNG BÀN PHÍM THEO HÃNG (BRAND)
# ========================================================
print("========== 1. COUNT KEYBOARDS BY BRAND ==========")
kb_brand_count = keyboard_df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .count() \
    .orderBy(col("count").desc())

kb_brand_count.show(truncate=False)
kb_brand_count.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/keyboard-01-count-brand")


# ========================================================
# 2. GIÁ TRUNG BÌNH, MIN, MAX BÀN PHÍM THEO HÃNG (Tránh E7/E8)
# ========================================================
print("========== 2. PRICE STATS BY BRAND ==========")
kb_price_stats = keyboard_df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .agg(
        avg("price_vnd").alias("avg_price"),
        min("price_vnd").alias("min_price"),
        max("price_vnd").alias("max_price")
    ) \
    .withColumn("avg_price", col("avg_price").cast(DecimalType(18, 0))) \
    .withColumn("min_price", col("min_price").cast(DecimalType(18, 0))) \
    .withColumn("max_price", col("max_price").cast(DecimalType(18, 0))) \
    .orderBy(col("avg_price").desc())

kb_price_stats.show(truncate=False)
kb_price_stats.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/keyboard-02-price-stats-brand")


# ========================================================
# 3. MỨC GIẢM GIÁ VÀ TỔNG CHIẾT KHẤU THEO HÃNG (Tránh E7/E8)
# ========================================================
print("========== 3. DISCOUNT STATS FOR KEYBOARDS ==========")
kb_discount_stats = keyboard_df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .agg(
        max("discount_amount_vnd").alias("max_discount_vnd"),
        sum("discount_amount_vnd").alias("total_discount_vnd"),
        round(avg("discount_percent"), 2).alias("avg_discount_pct")
    ) \
    .withColumn("max_discount_vnd", col("max_discount_vnd").cast(DecimalType(18, 0))) \
    .withColumn("total_discount_vnd", col("total_discount_vnd").cast(DecimalType(18, 0))) \
    .orderBy(col("max_discount_vnd").desc())

kb_discount_stats.show(truncate=False)
kb_discount_stats.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/keyboard-03-discount-stats")


# ========================================================
# 4. TỔNG ĐÁNH GIÁ VÀ ĐIỂM RATING TRUNG BÌNH THEO HÃNG
# ========================================================
print("========== 4. REVIEWS & RATING BY BRAND ==========")
kb_review_stats = keyboard_df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .agg(
        sum("review_count").alias("total_reviews"),
        round(avg("rating"), 2).alias("avg_rating")
    ) \
    .orderBy(col("total_reviews").desc())

kb_review_stats.show(truncate=False)
kb_review_stats.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/keyboard-04-reviews-rating")


# ========================================================
# 5. SỐ LƯỢNG THEO NGUỒN DỮ LIỆU CÀO (SOURCE)
# ========================================================
print("========== 5. COUNT KEYBOARDS BY SOURCE ==========")
kb_source_count = keyboard_df.filter(col("source").isNotNull()) \
    .groupBy("source") \
    .count() \
    .orderBy(col("count").desc())

kb_source_count.show(truncate=False)
kb_source_count.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/keyboard-05-source-count")

# Giải phóng bộ nhớ và dừng Spark Session
keyboard_df.unpersist()
spark.stop()