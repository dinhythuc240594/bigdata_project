const fs = require('fs');
const filePath = 'c:/Users/Laptop/Documents/GitHub/bigdata_project/frontend/src/pages/QueryEditor.jsx';
let content = fs.readFileSync(filePath, 'utf8');

const tpl13 = "{ name: '13. Spark: So sánh Giá trung bình (TGDĐ vs Phong Vũ)', engine: 'spark', query: \\"from pyspark.sql import SparkSession\\\\nfrom pyspark.sql.functions import col, avg, round, when\\\\n\\\\nspark = SparkSession.builder.appName('CompareStores').getOrCreate()\\\\ndf = spark.read.option('delimiter', '\\\\\\\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')\\\\ndf = df.toDF('brand', 'category', 'date', 'discount', 'discount_rate', 'name', 'original_price', 'price', 'product_id', 'rating', 'sku', 'sold', 'sold_info', 'source', 'url')\\\\n\\\\ndf = df.withColumn('price', col('price').cast('double'))\\\\nstores_df = df.filter(col('source').like('%thegioididong%') | col('source').like('%phongvu%'))\\\\nstores_df = stores_df.withColumn('store', when(col('source').like('%thegioididong%'), 'TGDD').otherwise('PhongVu'))\\\\n\\\\navg_price = stores_df.filter(col('price') > 0).groupBy('store').agg(round(avg('price'), 0).alias('avg_price'))\\\\navg_price.show()\\\\nspark.stop()\\" }";

if (!content.includes('13. Spark: So sánh Giá trung bình')) {
    content = content.replace(
        "result.show()\\nspark.stop()\\" }",
        "result.show()\\nspark.stop()\\" },\n    " + tpl13
    );
    fs.writeFileSync(filePath, content, 'utf8');
    console.log('Template 13 added!');
} else {
    console.log('Template 13 already exists.');
}
