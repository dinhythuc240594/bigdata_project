from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, 
    DoubleType, IntegerType, DecimalType
)
from pyspark.sql.functions import avg, max, sum, col, round

spark = SparkSession.builder \
    .appName("ProductAnalysis") \
    .getOrCreate()

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

# Làm sạch dữ liệu
df = raw_df \
    .filter(col("product_id").isNotNull()) \
    .filter(col("category").isNotNull()) \
    .filter(col("price_vnd").isNotNull()) \
    .dropDuplicates(["record_id"])

# ==========================================
# MR01: Count by category
# ==========================================
print("========== 1. COUNT CATEGORY ==========")
result1 = df.groupBy("category") \
    .count() \
    .orderBy(col("count").desc())

result1.show(truncate=False)
result1.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/01-count-category")


# ==========================================
# MR02: Average price by brand (Tránh E7/E8 bằng DecimalType)
# ==========================================
print("========== 2. AVG PRICE BRAND ==========")
result2 = df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .agg(avg("price_vnd").alias("avg_price")) \
    .withColumn("avg_price", col("avg_price").cast(DecimalType(18, 0))) \
    .orderBy(col("avg_price").desc())

result2.show(truncate=False)
result2.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/02-avg-price-brand")


# ==========================================
# MR03: Max price by category (Tránh E7/E8 bằng DecimalType)
# ==========================================
print("========== 3. MAX PRICE CATEGORY ==========")
result3 = df.groupBy("category") \
    .agg(max("price_vnd").alias("max_price")) \
    .withColumn("max_price", col("max_price").cast(DecimalType(18, 0))) \
    .orderBy(col("max_price").desc())

result3.show(truncate=False)
result3.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/03-max-price-category")


# ==========================================
# MR04: Total reviews by brand
# ==========================================
print("========== 4. TOTAL REVIEWS BRAND ==========")
result4 = df.filter(col("brand").isNotNull()) \
    .groupBy("brand") \
    .agg(sum("review_count").alias("total_reviews")) \
    .orderBy(col("total_reviews").desc())

result4.show(truncate=False)
result4.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/04-total-reviews-brand")


# ==========================================
# MR05: Average rating category
# ==========================================
print("========== 5. AVG RATING CATEGORY ==========")
result5 = df.filter(col("rating").isNotNull()) \
    .groupBy("category") \
    .agg(round(avg("rating"), 2).alias("avg_rating")) \
    .orderBy(col("avg_rating").desc())

result5.show(truncate=False)
result5.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/05-avg-rating-category")


# ==========================================
# MR06: Total discount category (Tránh E7/E8 bằng DecimalType)
# ==========================================
print("========== 6. TOTAL DISCOUNT CATEGORY ==========")
result6 = df.filter(col("discount_amount_vnd").isNotNull()) \
    .groupBy("category") \
    .agg(sum("discount_amount_vnd").alias("total_discount")) \
    .withColumn("total_discount", col("total_discount").cast(DecimalType(18, 0))) \
    .orderBy(col("total_discount").desc())

result6.show(truncate=False)
result6.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/06-total-discount-category")


# ==========================================
# MR07: Count by source
# ==========================================
print("========== 7. COUNT SOURCE ==========")
result7 = df.filter(col("source").isNotNull()) \
    .groupBy("source") \
    .count() \
    .orderBy(col("count").desc())

result7.show(truncate=False)
result7.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/07-count-source")


# ==========================================
# MR08: Max discount category (Tránh E7/E8 bằng DecimalType)
# ==========================================
print("========== 8. MAX DISCOUNT CATEGORY ==========")
result8 = df.filter(col("discount_amount_vnd").isNotNull()) \
    .groupBy("category") \
    .agg(max("discount_amount_vnd").alias("max_discount")) \
    .withColumn("max_discount", col("max_discount").cast(DecimalType(18, 0))) \
    .orderBy(col("max_discount").desc())

result8.show(truncate=False)
result8.write.mode("overwrite").option("header", True) \
    .csv("hdfs:///user/hadoopthuc/spark-results/08-max-discount-category")

spark.stop()