import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_api.utils.hadoop_ssh import HadoopTaskRunner
runner = HadoopTaskRunner('192.168.10.10', username='hadoopthuc')

pyspark_script = """
import json
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('Dashboard_Chart1').getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df1 = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')
df1.createOrReplaceTempView("laptop")
df2 = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_keyboard_products_common')
df2.createOrReplaceTempView("keyboard")
df3 = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_monitor_products_common')
df3.createOrReplaceTempView("monitor")

res1 = spark.sql('''
    SELECT _c0 as brand, 
           AVG(CASE WHEN _c13 LIKE '%thegioididong%' THEN CAST(_c7 AS DOUBLE) ELSE NULL END) as tgdd_price,
           AVG(CASE WHEN _c13 LIKE '%phongvu%' THEN CAST(_c7 AS DOUBLE) ELSE NULL END) as pv_price
    FROM (
        SELECT _c0, _c13, _c7 FROM laptop
        UNION ALL SELECT _c0, _c13, _c7 FROM keyboard
        UNION ALL SELECT _c0, _c13, _c7 FROM monitor
    ) all_products
    GROUP BY _c0
    HAVING tgdd_price IS NOT NULL AND pv_price IS NOT NULL
    ORDER BY tgdd_price DESC LIMIT 5
''').collect()

results = []
for row in res1:
    results.append({
        "brand": row["brand"],
        "tgdd_price": float(row["tgdd_price"]) if row["tgdd_price"] else 0,
        "pv_price": float(row["pv_price"]) if row["pv_price"] else 0
    })

print("CHART1_DATA:" + json.dumps(results))
"""

import base64
encoded_script = base64.b64encode(pyspark_script.encode('utf-8')).decode('utf-8')
cmd = f"echo {encoded_script} | base64 -d > /tmp/chart1.py && /home/hadoopthuc/spark/bin/spark-submit /tmp/chart1.py"

print("Running Spark Query...")
res = runner.execute_command(cmd)
print("Stdout:")
print(res.get('output', ''))
print("Stderr:", res.get('error', ''))
