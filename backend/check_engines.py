import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_api.utils.hadoop_ssh import HadoopTaskRunner
runner = HadoopTaskRunner('192.168.10.10', username='hadoopthuc')

res = runner.execute_command('/home/hadoopthuc/hive/bin/hive -e "SELECT COUNT(1) FROM laptop_products_common_hive;"')
print("HIVE RESULT:", res)

res2 = runner.execute_command('/home/hadoopthuc/spark/bin/spark-submit --version')
print("SPARK RESULT:", res2)
