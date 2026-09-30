import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_api.utils.hadoop_ssh import HadoopTaskRunner
runner = HadoopTaskRunner('192.168.10.10', username='hadoopthuc')

pyspark_script = """
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('Test_Spark_Hive').enableHiveSupport().getOrCreate()
res = spark.sql('SELECT COUNT(*) FROM laptop_products_common_hive').collect()
print("FINAL_RESULT:", res[0][0])
"""

import base64
encoded_script = base64.b64encode(pyspark_script.encode('utf-8')).decode('utf-8')
cmd = f"echo {encoded_script} | base64 -d > /tmp/test_hive.py && /home/hadoopthuc/spark/bin/spark-submit /tmp/test_hive.py"

print("Running Spark Job...")
res = runner.execute_command(cmd)
print("Stdout:", res.get('output', ''))
print("Stderr:", res.get('error', ''))
