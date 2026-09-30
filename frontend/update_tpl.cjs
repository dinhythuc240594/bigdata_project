const fs = require('fs');
const filePath = 'c:/Users/Laptop/Documents/GitHub/bigdata_project/frontend/src/pages/QueryEditor.jsx';
let content = fs.readFileSync(filePath, 'utf8');

const tpl10 = "{ name: '10. Spark: Top 5 Laptop đắt nhất', engine: 'spark', query: rom pyspark.sql import SparkSession\\nfrom pyspark.sql.functions import col\\n\\nspark = SparkSession.builder.appName('TopExpensive').getOrCreate()\\ndf = spark.read.option('delimiter', '\\\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\\n\\ndf = df.withColumn('price', col('price').cast('double'))\\ntop5 = df.filter(col('price') > 0).orderBy(col('price').desc()).select('name', 'price').limit(5)\\ntop5.show(truncate=False)\\nspark.stop() }";

const tpl11 = "{ name: '11. Spark: Trung bình giảm giá theo hãng', engine: 'spark', query: rom pyspark.sql import SparkSession\\nfrom pyspark.sql.functions import col, avg, round\\n\\nspark = SparkSession.builder.appName('AvgDiscount').getOrCreate()\\ndf = spark.read.option('delimiter', '\\\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\\n\\ndf = df.withColumn('discount_rate', col('discount_rate').cast('double'))\\navg_discount = df.filter(col('discount_rate') > 0).groupBy('brand').agg(round(avg('discount_rate'), 2).alias('avg_discount')).orderBy(col('avg_discount').desc()).limit(10)\\navg_discount.show()\\nspark.stop() }";

const tpl12 = "{ name: '12. Spark: Số lượng máy bán ra theo phân khúc', engine: 'spark', query: rom pyspark.sql import SparkSession\\nfrom pyspark.sql.functions import col, sum, when\\n\\nspark = SparkSession.builder.appName('SoldBySegment').getOrCreate()\\ndf = spark.read.option('delimiter', '\\\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\\n\\ndf = df.withColumn('price', col('price').cast('double')).withColumn('sold', col('sold').cast('int'))\\nsegments = df.withColumn('segment', \\n    when(col('price') < 10000000, 'Gia re (<10Tr)')\\n    .when((col('price') >= 10000000) & (col('price') <= 20000000), 'Tam trung (10-20Tr)')\\n    .otherwise('Cao cap (>20Tr)')\\n)\\nresult = segments.groupBy('segment').agg(sum('sold').alias('total_sold')).orderBy(col('total_sold').desc())\\nresult.show()\\nspark.stop() }";


if (!content.includes('10. Spark')) {
    content = content.replace(
        "DUMP top10;\" }",
        "DUMP top10;\" },\n    " + tpl10 + ",\n    " + tpl11 + ",\n    " + tpl12
    );
    fs.writeFileSync(filePath, content, 'utf8');
    console.log('Templates added!');
} else {
    console.log('Templates already exist.');
}
