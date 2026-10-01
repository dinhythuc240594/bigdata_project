from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, 
    DoubleType, IntegerType, DecimalType
)
from pyspark.sql.functions import avg, max, min, sum, count, col, round, lower, trim, when

# 1. Khởi tạo Spark Session
spark = SparkSession.builder \
    .appName("CompareTGDDvsPhongVu") \
    .getOrCreate()

# 2. Schema dữ liệu 15 cột
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

# 3. Đọc dữ liệu từ HDFS và khử lỗi
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

# 4. Làm sạch & Chuẩn hóa tên nguồn (thegioididong / phongvu)
# Xử lý các biến thể chuỗi: tgdd -> thegioididong, phong_vu -> phongvu
clean_df = raw_df \
    .filter(col("source").isNotNull()) \
    .filter(col("price_vnd").isNotNull()) \
    .withColumn("source_clean", 
        when(lower(trim(col("source"))).contains("thegioididong") | lower(trim(col("source"))).contains("tgdd"), "thegioididong")
        .when(lower(trim(col("source"))).contains("phongvu") | lower(trim(col("source"))).contains("phong_vu"), "phongvu")
        .otherwise("other")
    ) \
    .filter(col("source_clean").isin("thegioididong", "phongvu")) \
    .dropDuplicates(["record_id"])

clean_df.cache()

print("========== SAMPLE COMPARISON DATA ==========")
clean_df.select("source_clean", "category", "brand", "name", "price_vnd") \
    .show(10, truncate=False)

print(f"Tổng số bản ghi hợp lệ (TGDD & Phong Vũ): {clean_df.count()}")


# ==============================================================================
# MR 01: SO SÁNH QUY MÔ SẢN PHẨM THEO NGÀNH HÀNG (MARKET COVERAGE BY CATEGORY)
# Map: (category, source) -> 1
# Reduce: Tính tổng sản phẩm của từng sàn và pivot theo cột để dễ so sánh
# ==============================================================================
print("========== MR 01: PRODUCT COUNT BY CATEGORY (TGDD VS PHONGVU) ==========")

mr01_result = clean_df \
    .filter(col("category").isNotNull()) \
    .groupBy("category") \
    .pivot("source_clean", ["thegioididong", "phongvu"]) \
    .agg(count("product_id")) \
    .na.fill(0)

mr01_result.show(truncate=False)
mr01_result.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/mr-source-01-category-coverage")


# ==============================================================================
# MR 02: SO SÁNH GIÁ TRUNG BÌNH & MỨC KHUYẾN MÃI (PRICE & DISCOUNT WAR)
# Map: (category, source) -> (price_vnd, discount_percent)
# Reduce: avg(price_vnd), avg(discount_percent)
# ==============================================================================
print("========== MR 02: AVG PRICE & DISCOUNT % BY SOURCE & CATEGORY ==========")

mr02_result = clean_df \
    .filter(col("category").isNotNull()) \
    .groupBy("category", "source_clean") \
    .agg(
        avg("price_vnd").alias("avg_price_vnd"),
        round(avg("discount_percent"), 2).alias("avg_discount_pct"),
        max("discount_amount_vnd").alias("max_discount_vnd")
    ) \
    .withColumn("avg_price_vnd", col("avg_price_vnd").cast(DecimalType(18, 0))) \
    .withColumn("max_discount_vnd", col("max_discount_vnd").cast(DecimalType(18, 0))) \
    .orderBy("category", "source_clean")

mr02_result.show(truncate=False)
mr02_result.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/mr-source-02-price-discount-war")


# ==============================================================================
# MR 03: PHÂN BỐ CÁC THƯƠNG HIỆU HÀNG ĐẦU GIỮA 2 SÀN (BRAND DOMINANCE)
# Map: (brand, source) -> 1
# Reduce: sum(count), phân bổ sản phẩm của từng hãng trên TGDD và Phong Vũ
# ==============================================================================
print("========== MR 03: TOP BRANDS PRESENCE (TGDD VS PHONGVU) ==========")

mr03_result = clean_df \
    .filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .pivot("source_clean", ["thegioididong", "phongvu"]) \
    .agg(count("product_id")) \
    .na.fill(0) \
    .withColumn("total", col("thegioididong") + col("phongvu")) \
    .orderBy(col("total").desc())

mr03_result.show(20, truncate=False)
mr03_result.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/mr-source-03-brand-presence")

# Giải phóng bộ nhớ và kết thúc session
clean_df.unpersist()
spark.stop()