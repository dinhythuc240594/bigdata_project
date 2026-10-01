from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, 
    DoubleType, IntegerType, DecimalType
)
from pyspark.sql.functions import avg, max, min, sum, col, round, lower

# 1. Khởi tạo Spark Session
spark = SparkSession.builder \
    .appName("MonitorProductAnalysis") \
    .getOrCreate()

# 2. Định nghĩa Schema chuẩn
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

# 3. Đọc dữ liệu từ HDFS, xử lý chuỗi "null", dấu ngoặc kép và dòng lỗi
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

# 4. Làm sạch & Lọc riêng dòng sản phẩm MONITOR
monitor_df = raw_df \
    .filter(col("category").isNotNull()) \
    .filter(lower(col("category")) == "monitor") \
    .filter(col("product_id").isNotNull()) \
    .filter(col("price_vnd").isNotNull()) \
    .dropDuplicates(["record_id"])

# Cache lại DataFrame monitor vì sẽ thực hiện nhiều action phân tích
monitor_df.cache()

print("========== SAMPLE MONITOR DATA ==========")
monitor_df.select("product_id", "brand", "name", "price_vnd", "discount_amount_vnd", "rating") \
    .show(10, truncate=False)

print("========== TOTAL MONITOR PRODUCTS ==========")
print(f"Tổng số bản ghi monitor hợp lệ: {monitor_df.count()}")


# ========================================================
# 1. THỐNG KÊ SỐ LƯỢNG MÀN HÌNH THEO HÃNG (BRAND)
# ========================================================
print("========== 1. COUNT MONITORS BY BRAND ==========")
m_brand_count = monitor_df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .count() \
    .orderBy(col("count").desc())

m_brand_count.show(truncate=False)
m_brand_count.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/monitor-01-count-brand")


# ========================================================
# 2. GIÁ TRUNG BÌNH, MIN, MAX THEO HÃNG (Tránh lỗi E7/E8)
# ========================================================
print("========== 2. PRICE STATS BY BRAND ==========")
m_price_stats = monitor_df.filter(col("brand").isNotNull()) \
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

m_price_stats.show(truncate=False)
m_price_stats.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/monitor-02-price-stats-brand")


# ========================================================
# 3. MỨC GIẢM GIÁ CAO NHẤT & TỔNG GIẢM GIÁ CỦA MONITOR (Tránh E7/E8)
# ========================================================
print("========== 3. DISCOUNT STATS FOR MONITORS ==========")
m_discount_stats = monitor_df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .agg(
        max("discount_amount_vnd").alias("max_discount_vnd"),
        sum("discount_amount_vnd").alias("total_discount_vnd"),
        round(avg("discount_percent"), 2).alias("avg_discount_pct")
    ) \
    .withColumn("max_discount_vnd", col("max_discount_vnd").cast(DecimalType(18, 0))) \
    .withColumn("total_discount_vnd", col("total_discount_vnd").cast(DecimalType(18, 0))) \
    .orderBy(col("max_discount_vnd").desc())

m_discount_stats.show(truncate=False)
m_discount_stats.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/monitor-03-discount-stats")


# ========================================================
# 4. TỔNG LƯỢT ĐÁNH GIÁ VÀ RATING TRUNG BÌNH THEO HÃNG
# ========================================================
print("========== 4. REVIEWS & RATING BY BRAND ==========")
m_review_stats = monitor_df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .agg(
        sum("review_count").alias("total_reviews"),
        round(avg("rating"), 2).alias("avg_rating")
    ) \
    .orderBy(col("total_reviews").desc())

m_review_stats.show(truncate=False)
m_review_stats.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/monitor-04-reviews-rating")


# ========================================================
# 5. NGUỒN CÀO DỮ LIỆU CỦA MONITOR (SOURCE)
# ========================================================
print("========== 5. COUNT MONITOR BY SOURCE ==========")
m_source_count = monitor_df.filter(col("source").isNotNull()) \
    .groupBy("source") \
    .count() \
    .orderBy(col("count").desc())

m_source_count.show(truncate=False)
m_source_count.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/monitor-05-source-count")

# Giải phóng bộ nhớ cache và dừng Spark
monitor_df.unpersist()
spark.stop()