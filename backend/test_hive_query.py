import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_api.utils.hadoop_ssh import HadoopTaskRunner
runner = HadoopTaskRunner('192.168.10.10', username='hadoopthuc')

hive_query = """
SET hive.cli.print.header=false;
SELECT brand, COUNT(1) as total
FROM (
    SELECT brand FROM laptop_products_common_hive
    UNION ALL
    SELECT brand FROM keyboard_products_common_hive
    UNION ALL
    SELECT brand FROM monitor_products_common_hive
) all_products
GROUP BY brand
ORDER BY total DESC LIMIT 5;
"""

import base64
encoded_query = base64.b64encode(hive_query.encode('utf-8')).decode('utf-8')
cmd = f"echo {encoded_query} | base64 -d > /tmp/chart4.hql && /home/hadoopthuc/hive/bin/hive -S -f /tmp/chart4.hql"

print("Running Hive Query...")
res = runner.execute_command(cmd)
print("Stdout:")
print(res.get('output', ''))
print("Stderr:", res.get('error', ''))
