from rest_framework.views import APIView
from rest_framework.response import Response
from .utils.hadoop_ssh import HadoopTaskRunner

class RunMapReduceView(APIView):
    def post(self, request):
        import os
        from django.conf import settings
        
        hadoop_host = request.data.get('hadoop_host')
        hadoop_user = request.data.get('hadoop_user')
        input_dir = request.data.get('input_dir')
        output_dir = request.data.get('output_dir')
        
        mapper_path = os.path.join(settings.BASE_DIR, 'core_api', 'utils', 'mapreduce', 'mapper.py')
        reducer_path = os.path.join(settings.BASE_DIR, 'core_api', 'utils', 'mapreduce', 'reducer.py')

        from django.utils.timezone import now
        from .models import JobHistory
        import uuid
        
        job_id = f"JOB-{str(uuid.uuid4())[:6].upper()}"
        start_time = now()
        
        job = JobHistory.objects.create(
            job_id=job_id,
            name=f"MapReduce: {input_dir.split('_')[-1].capitalize()} Data",
            job_type='MapReduce',
            table_name=input_dir.split('/')[-1],
            status='Running',
            start_time=start_time
        )
        
        runner = HadoopTaskRunner(hostname=hadoop_host, username=hadoop_user)
        result = runner.run_mapreduce_job(
            input_dir=input_dir,
            output_dir=output_dir,
            local_mapper_path=mapper_path,
            local_reducer_path=reducer_path
        )
        
        job.status = 'Completed' if result['success'] else 'Failed'
        job.logs = result.get('output', '') if result['success'] else result.get('error', '')
        job.end_time = now()
        job.save()
        
        if result['success']:
            return Response({
                "status": "success",
                "message": "MapReduce Task đã thực thi thành công!", 
                "logs": result.get('output', '')
            }, status=200)
        else:
            return Response({
                "status": "error",
                "message": "Có lỗi khi chạy MapReduce", 
                "error_logs": result.get('error', '')
            }, status=500)

class RunSqoopView(APIView):
    def post(self, request):
        # Lấy thông tin từ request (Frontend gửi lên)
        hadoop_host = request.data.get('hadoop_host')
        hadoop_user = request.data.get('hadoop_user')
        # password có thể có hoặc không vì chúng ta đã dùng SSH Key
        hadoop_password = request.data.get('hadoop_password')

        mysql_host = request.data.get('mysql_host')
        mysql_user = request.data.get('mysql_user')
        mysql_password = request.data.get('mysql_password')
        mysql_db = request.data.get('mysql_db', 'bigdata_db')
        table_name = request.data.get('table_name', 'raw_data_table')
        target_dir = request.data.get('target_dir', '/user/hadoopthuc/project/input_data')

        from django.utils.timezone import now
        from .models import JobHistory
        import uuid
        
        job_id = f"JOB-{str(uuid.uuid4())[:6].upper()}"
        start_time = now()

        job = JobHistory.objects.create(
            job_id=job_id,
            name=f"Sqoop Import: {table_name}",
            job_type='Sqoop',
            table_name=table_name,
            status='Running',
            start_time=start_time
        )

        # Khởi tạo Runner với cấu hình động
        runner = HadoopTaskRunner(
            hostname=hadoop_host,
            username=hadoop_user,
            password=hadoop_password
        )
        
        # Chạy Sqoop
        result = runner.run_sqoop_import(
            mysql_host=mysql_host,
            mysql_user=mysql_user,
            mysql_password=mysql_password,
            mysql_db=mysql_db,
            table_name=table_name,
            target_dir=target_dir
        )
        
        job.status = 'Completed' if result['success'] else 'Failed'
        job.logs = result.get('output', '') if result['success'] else result.get('error', '')
        job.end_time = now()
        job.save()
        
        if result['success']:
            return Response({
                "status": "success",
                "message": "Sqoop Import đã thực thi thành công!", 
                "logs": result.get('output', '')
            }, status=200)
        else:
            return Response({
                "status": "error",
                "message": "Có lỗi khi chạy Sqoop", 
                "error_logs": result['error']
            }, status=500)

class RunSqoopExportView(APIView):
    def post(self, request):
        from .utils.hadoop_ssh import HadoopTaskRunner
        from django.utils.timezone import now
        from .models import JobHistory
        import uuid
        
        table_name = request.data.get('table_name', 'laptop_stats')
        export_dir = request.data.get('export_dir', '/user/hadoopthuc/project/output_laptop_stats')
        
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (brand VARCHAR(255), average_price VARCHAR(255))")
                cursor.execute(f"TRUNCATE TABLE {table_name}")
        except Exception as e:
            return Response({"status": "error", "message": "Không thể tạo bảng trên MySQL", "error_logs": str(e)}, status=500)
            
        job_id = f"JOB-{str(uuid.uuid4())[:6].upper()}"
        start_time = now()
        
        job = JobHistory.objects.create(
            job_id=job_id,
            name=f"Sqoop Export: {table_name}",
            job_type='Sqoop',
            table_name=table_name,
            status='Running',
            start_time=start_time
        )
        
        runner = HadoopTaskRunner(hostname='192.168.10.10', username='hadoopthuc')
        cmd = f"/usr/lib/sqoop/bin/sqoop export --connect jdbc:mysql://192.168.10.5/bigdata_db --username root --password 123456789 --table {table_name} --columns brand,average_price --export-dir {export_dir} --input-fields-terminated-by '\\t'"
        
        result = runner.execute_command(cmd)
        
        job.status = 'Completed' if result['success'] else 'Failed'
        job.logs = result.get('output', '') if result['success'] else result.get('error', '')
        job.end_time = now()
        job.save()
        
        if result['success']:
            return Response({"status": "success", "message": "Sqoop Export thành công!", "logs": job.logs}, status=200)
        return Response({"status": "error", "message": "Sqoop Export thất bại!", "error_logs": job.logs}, status=500)

class JobHistoryView(APIView):
    def get(self, request):
        from .models import JobHistory
        jobs = JobHistory.objects.all().order_by('-start_time')
        data = []
        for j in jobs:
            data.append({
                'id': j.job_id,
                'name': j.name,
                'type': j.job_type,
                'tableName': j.table_name,
                'status': j.status,
                'startTime': j.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': j.duration,
                'logs': j.logs
            })
        return Response(data, status=200)

class ActiveTasksView(APIView):
    def get(self, request):
        from .models import JobHistory
        jobs = JobHistory.objects.filter(status='Running').order_by('-start_time')
        data = []
        for j in jobs:
            data.append({
                'id': j.job_id,
                'name': j.name,
                'startTime': j.start_time.strftime('%H:%M:%S')
            })
        return Response(data, status=200)

class DashboardStatsView(APIView):
    def get(self, request):
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                # Basic stats
                cursor.execute("SELECT COUNT(*) FROM laptop_products_common")
                laptop_count = cursor.fetchone()[0] or 0
                cursor.execute("SELECT COUNT(*) FROM keyboard_products_common")
                keyboard_count = cursor.fetchone()[0] or 0
                cursor.execute("SELECT COUNT(*) FROM monitor_products_common")
                monitor_count = cursor.fetchone()[0] or 0
                total_records = laptop_count + keyboard_count + monitor_count
                
                from .models import JobHistory
                job_count = JobHistory.objects.count()
                
                # Chart 1
                chart1 = []
                try:
                    cursor.execute("SELECT brand, tgdd_price, pv_price FROM chart1_tgdd_pv_price")
                    for row in cursor.fetchall():
                        chart1.append({"name": str(row[0])[:15], "tgdd": int(row[1]), "pv": int(row[2])})
                except Exception:
                    pass
                
                # Chart 2
                chart2 = []
                try:
                    cursor.execute("SELECT source_name, volume FROM chart2_tgdd_pv_volume")
                    for row in cursor.fetchall():
                        chart2.append({"name": str(row[0]), "value": int(row[1])})
                except Exception:
                    pass
                    
                # Chart 3
                chart3 = []
                try:
                    cursor.execute("SELECT brand, avg_rating FROM chart3_rating_trend")
                    for row in cursor.fetchall():
                        chart3.append({"name": str(row[0])[:15], "value": float(row[1])})
                except Exception:
                    pass
                    
                # Chart 4
                chart4 = []
                try:
                    cursor.execute("SELECT brand, total FROM chart4_top_brands")
                    for row in cursor.fetchall():
                        chart4.append({"name": str(row[0])[:15], "value": int(row[1])})
                except Exception:
                    pass
                    
                # Chart 5
                chart5 = []
                try:
                    cursor.execute("SELECT category, total FROM chart5_category_dist")
                    for row in cursor.fetchall():
                        chart5.append({"name": str(row[0]), "value": int(row[1])})
                except Exception:
                    pass
                
                data = {
                    "chart1": chart1,
                    "chart2": chart2,
                    "chart3": chart3,
                    "chart4": chart4,
                    "chart5": chart5,
                    "kpis": {
                        "totalData": f"{total_records} SP",
                        "totalDataTrend": "Du lieu that",
                        "totalDataIsUp": True,
                        "mapReduceQueries": f"{job_count}",
                        "mapReduceTrend": "MR Jobs",
                        "mapReduceIsUp": True,
                        "reportsGenerated": "San sang",
                        "reportsTrend": "Cho lenh",
                        "reportsIsUp": True,
                    }
                }
                return Response(data, status=200)
        except Exception as e:
            return Response({"error": str(e), "message": "Loi database"}, status=500)

class DataTableDataView(APIView):
    def get(self, request):
        from django.db import connection
        category = request.query_params.get('category', 'All')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        search = request.query_params.get('search', '').strip()
        brand = request.query_params.get('brand', '').strip()
        sort_by = request.query_params.get('sort_by', '').strip()
        sort_dir = request.query_params.get('sort_dir', 'asc').strip()
        offset = (page - 1) * limit
        
        order_sql = ""
        if sort_by:
            allowed_sort = {'sku': 'sku', 'name': 'name', 'brand': 'brand', 'price': 'price_vnd', 'source': 'source', 'crawl_date': 'crawl_date'}
            if sort_by in allowed_sort:
                col = allowed_sort[sort_by]
                dir_sql = "DESC" if sort_dir.lower() == 'desc' else "ASC"
                order_sql = f"ORDER BY {col} {dir_sql}"
        
        data = []
        total_records = 0
        
        try:
            with connection.cursor() as cursor:
                def fetch_table(table_name, cat_name):
                    nonlocal total_records
                    
                    where_clauses = []
                    params = []
                    
                    if search:
                        where_clauses.append("(name LIKE %s OR sku LIKE %s)")
                        params.extend([f"%{search}%", f"%{search}%"])
                    if brand:
                        where_clauses.append("brand = %s")
                        params.append(brand)
                        
                    where_sql = ""
                    if where_clauses:
                        where_sql = "WHERE " + " AND ".join(where_clauses)
                        
                    # Lấy tổng số lượng
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} {where_sql}", params)
                    total_records = cursor.fetchone()[0] or 0
                    
                    # Lấy dữ liệu phân trang
                    cursor.execute(f"SELECT sku, name, brand, price_vnd, source, crawl_date FROM {table_name} {where_sql} {order_sql} LIMIT {limit} OFFSET {offset}", params)
                    for idx, row in enumerate(cursor.fetchall()):
                        data.append({
                            'id': f"{cat_name}-{offset+idx}",
                            'sku': row[0] or '',
                            'name': row[1] or '',
                            'brand': row[2] or '',
                            'price': f"{row[3]:,.0f}" if row[3] else "0",
                            'source': row[4] or '',
                            'date': str(row[5]) if row[5] else ''
                        })
                        
                if category == 'All':
                    where_clauses = []
                    params = []
                    
                    if search:
                        where_clauses.append("(name LIKE %s OR sku LIKE %s)")
                        params.extend([f"%{search}%", f"%{search}%"])
                    if brand:
                        where_clauses.append("brand = %s")
                        params.append(brand)
                        
                    where_sql = ""
                    if where_clauses:
                        where_sql = "WHERE " + " AND ".join(where_clauses)
                        
                    union_params = params * 3
                        
                    count_query = f"""
                        SELECT SUM(cnt) FROM (
                            SELECT COUNT(*) as cnt FROM laptop_products_common {where_sql}
                            UNION ALL
                            SELECT COUNT(*) as cnt FROM keyboard_products_common {where_sql}
                            UNION ALL
                            SELECT COUNT(*) as cnt FROM monitor_products_common {where_sql}
                        ) t
                    """
                    cursor.execute(count_query, union_params)
                    total_records = int(cursor.fetchone()[0] or 0)
                    
                    data_query = f"""
                        SELECT * FROM (
                            SELECT sku, name, brand, price_vnd, source, crawl_date FROM laptop_products_common {where_sql}
                            UNION ALL
                            SELECT sku, name, brand, price_vnd, source, crawl_date FROM keyboard_products_common {where_sql}
                            UNION ALL
                            SELECT sku, name, brand, price_vnd, source, crawl_date FROM monitor_products_common {where_sql}
                        ) t {order_sql}
                        LIMIT {limit} OFFSET {offset}
                    """
                    cursor.execute(data_query, union_params)
                    for idx, row in enumerate(cursor.fetchall()):
                        data.append({
                            'id': f"ALL-{offset+idx}",
                            'sku': row[0] or '',
                            'name': row[1] or '',
                            'brand': row[2] or '',
                            'price': f"{row[3]:,.0f}" if row[3] else "0",
                            'source': row[4] or '',
                            'date': str(row[5]) if row[5] else ''
                        })
                elif category == 'Laptop':
                    fetch_table('laptop_products_common', 'LAP')
                elif category == 'Keyboard':
                    fetch_table('keyboard_products_common', 'KB')
                elif category == 'Monitor':
                    fetch_table('monitor_products_common', 'MON')
                    
                    
            return Response({
                "data": data,
                "total": total_records,
                "page": page,
                "limit": limit
            }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class DataRecordView(APIView):
    def post(self, request):
        from django.db import connection
        category = request.data.get('category', 'Laptop')
        sku = request.data.get('sku', '')
        name = request.data.get('name', '')
        brand = request.data.get('brand', '')
        price = request.data.get('price', 0)
        
        table = 'laptop_products_common' if category == 'Laptop' else 'keyboard_products_common' if category == 'Keyboard' else 'monitor_products_common'
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"INSERT INTO {table} (sku, name, brand, price_vnd, source) VALUES (%s, %s, %s, %s, 'Manual')", [sku, name, brand, price])
            return Response({"status": "success"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
            
    def put(self, request):
        from django.db import connection
        category = request.data.get('category', 'Laptop')
        sku = request.data.get('sku', '')
        name = request.data.get('name', '')
        brand = request.data.get('brand', '')
        price = request.data.get('price', 0)
        
        table = 'laptop_products_common' if category == 'Laptop' else 'keyboard_products_common' if category == 'Keyboard' else 'monitor_products_common'
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"UPDATE {table} SET name=%s, brand=%s, price_vnd=%s WHERE sku=%s", [name, brand, price, sku])
            return Response({"status": "success"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
            
    def delete(self, request):
        from django.db import connection
        category = request.data.get('category', 'Laptop')
        sku = request.data.get('sku', '')
        
        table = 'laptop_products_common' if category == 'Laptop' else 'keyboard_products_common' if category == 'Keyboard' else 'monitor_products_common'
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table} WHERE sku=%s", [sku])
            return Response({"status": "success"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ClusterStatusView(APIView):
    def get(self, request):
        import subprocess
        from concurrent.futures import ThreadPoolExecutor
        
        nodes = [
            {"name": "Hadoop Master", "ip": "192.168.10.10", "role": "NameNode, ResourceManager"},
            {"name": "Hadoop Slave", "ip": "192.168.10.11", "role": "DataNode, NodeManager"}
        ]
        
        def ping_node(node):
            try:
                # Lệnh ping trên Windows
                output = subprocess.check_output(f"ping -n 1 -w 500 {node['ip']}", shell=True).decode('cp1252', errors='ignore')
                is_online = "TTL=" in output
            except Exception:
                is_online = False
            return {
                "name": node['name'],
                "ip": node['ip'],
                "role": node['role'],
                "status": "Online" if is_online else "Offline",
            }
            
        with ThreadPoolExecutor(max_workers=2) as executor:
            status_data = list(executor.map(ping_node, nodes))
            
        return Response({"nodes": status_data}, status=200)

class RunHiveView(APIView):
    def post(self, request):
        from .utils.hadoop_ssh import HadoopTaskRunner
        from django.utils.timezone import now
        from .models import JobHistory
        import uuid
        
        table_name = request.data.get('table_name', 'laptop_products_common')
        
        job_id = f"JOB-{str(uuid.uuid4())[:6].upper()}"
        start_time = now()
        job = JobHistory.objects.create(
            job_id=job_id,
            name=f"Hive Query: {table_name}",
            job_type='Hive',
            table_name=table_name,
            status='Running',
            start_time=start_time
        )
        
        runner = HadoopTaskRunner(hostname='192.168.10.10', username='hadoopthuc')
        
        # Hive query tạo External Table và đếm số lượng theo Brand
        hive_query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {table_name}_hive (
            brand STRING, category STRING, crawl_date STRING, discount DOUBLE, discount_rate DOUBLE, name STRING, original_price DOUBLE, price DOUBLE, product_id STRING, rating DOUBLE, sku STRING, sold INT, sold_info STRING, source STRING, url STRING
        ) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\t' 
        STORED AS TEXTFILE LOCATION '/user/hadoopthuc/project/input_{table_name}';
        SELECT brand, COUNT(*) as total FROM {table_name}_hive GROUP BY brand ORDER BY total DESC LIMIT 10;
        """
        
        # Lưu ra file hql tạm trên máy master rồi chạy
        cmd = f"echo \"{hive_query}\" > /tmp/query.hql && /home/hadoopthuc/hive/bin/hive -f /tmp/query.hql"
        result = runner.execute_command(cmd)
        
        job.status = 'Completed' if result['success'] else 'Failed'
        job.logs = result.get('output', '') if result['success'] else result.get('error', '')
        job.end_time = now()
        job.save()
        
        if result['success']:
            return Response({"status": "success", "message": "Chạy Hive thành công!", "logs": job.logs}, status=200)
        return Response({"status": "error", "message": "Có lỗi khi chạy Hive", "error_logs": job.logs}, status=500)

class RunPigView(APIView):
    def post(self, request):
        from .utils.hadoop_ssh import HadoopTaskRunner
        from django.utils.timezone import now
        from .models import JobHistory
        import uuid
        
        table_name = request.data.get('table_name', 'laptop_products_common')
        
        job_id = f"JOB-{str(uuid.uuid4())[:6].upper()}"
        start_time = now()
        job = JobHistory.objects.create(
            job_id=job_id,
            name=f"Pig Script: {table_name}",
            job_type='Pig',
            table_name=table_name,
            status='Running',
            start_time=start_time
        )
        
        runner = HadoopTaskRunner(hostname='192.168.10.10', username='hadoopthuc')
        
        # Pig script: Lọc sản phẩm cao cấp (giá > 20 triệu) và đếm theo Brand
        pig_script = f"""
        data = LOAD '/user/hadoopthuc/project/input_{table_name}' USING PigStorage('\\t') AS (brand:chararray, category:chararray, date:chararray, discount:double, discount_rate:double, name:chararray, original_price:double, price:double, product_id:chararray, rating:double, sku:chararray, sold:int, sold_info:chararray, source:chararray, url:chararray);
        filtered = FILTER data BY price > 20000000;
        grouped = GROUP filtered BY brand;
        counts = FOREACH grouped GENERATE group AS brand, COUNT(filtered) AS total;
        ordered = ORDER counts BY total DESC;
        top_high_end = LIMIT ordered 5;
        DUMP top_high_end;
        """
        
        cmd = f"/home/hadoopthuc/pig/bin/pig -x mapreduce -e \"{pig_script}\""
        result = runner.execute_command(cmd)
        
        job.status = 'Completed' if result['success'] else 'Failed'
        job.logs = result.get('output', '') if result['success'] else result.get('error', '')
        job.end_time = now()
        job.save()
        
        if result['success']:
            return Response({"status": "success", "message": "Chạy Pig thành công!", "logs": job.logs}, status=200)
        return Response({"status": "error", "message": "Có lỗi khi chạy Pig", "error_logs": job.logs}, status=500)

class RunSparkView(APIView):
    def post(self, request):
        from .utils.hadoop_ssh import HadoopTaskRunner
        from django.utils.timezone import now
        from .models import JobHistory
        import uuid
        
        table_name = request.data.get('table_name', 'laptop_products_common')
        
        job_id = f"JOB-{str(uuid.uuid4())[:6].upper()}"
        start_time = now()
        job = JobHistory.objects.create(
            job_id=job_id,
            name=f"Spark Job: Phân tích {table_name}",
            job_type='Spark',
            table_name=table_name,
            status='Running',
            start_time=start_time
        )
        
        runner = HadoopTaskRunner(hostname='192.168.10.10', username='hadoopthuc')
        
        # PySpark script tính trung bình giá
        pyspark_script = f"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg

spark = SparkSession.builder.appName("Spark_BigData_Analysis").getOrCreate()
# Đọc file TSV
df = spark.read.option("delimiter", "\\t").csv("hdfs://192.168.10.10:9000/user/hadoopthuc/project/input_{table_name}")
df = df.toDF("brand", "category", "date", "discount", "discount_rate", "name", "original_price", "price", "product_id", "rating", "sku", "sold", "sold_info", "source", "url")

# Lọc các dòng có giá hợp lệ
df = df.filter(df.price.isNotNull())

# Tính trung bình giá theo brand
avg_price_df = df.groupBy("brand").agg(avg("price").alias("avg_price"))
avg_price_df.show(5)

spark.stop()
"""
        
        # Lưu ra file pyspark tạm rồi chạy bằng spark-submit
        cmd = f"echo \"{pyspark_script}\" > /tmp/spark_job.py && /home/hadoopthuc/spark/bin/spark-submit /tmp/spark_job.py"
        result = runner.execute_command(cmd)
        
        job.status = 'Completed' if result['success'] else 'Failed'
        job.logs = result.get('output', '') if result['success'] else result.get('error', '')
        job.end_time = now()
        job.save()
        
        if result['success']:
            return Response({"status": "success", "message": "Chạy Spark thành công!", "logs": job.logs}, status=200)
        return Response({"status": "error", "message": "Có lỗi khi chạy Spark", "error_logs": job.logs}, status=500)

class RunCustomQueryView(APIView):
    def post(self, request):
        from .utils.hadoop_ssh import HadoopTaskRunner
        from django.utils.timezone import now
        from .models import JobHistory
        import uuid
        import base64
        
        engine = request.data.get('engine', 'hive')
        query = request.data.get('query', '')
        
        if not query.strip():
            return Response({"status": "error", "message": "Query không được để trống!"}, status=400)
            
        job_id = f"JOB-{str(uuid.uuid4())[:6].upper()}"
        start_time = now()
        job = JobHistory.objects.create(
            job_id=job_id,
            name=f"Custom {engine.capitalize()} Query",
            job_type=engine.capitalize(),
            status='Running',
            start_time=start_time
        )
        
        runner = HadoopTaskRunner(hostname='192.168.10.10', username='hadoopthuc')
        
        # Base64 encode the query to avoid bash parsing errors
        encoded_query = base64.b64encode(query.encode('utf-8')).decode('utf-8')
        
        if engine == 'hive':
            ext = 'hql'
            cmd = f"echo {encoded_query} | base64 -d > /tmp/custom.{ext} && /home/hadoopthuc/hive/bin/hive -f /tmp/custom.{ext}"
        elif engine == 'pig':
            ext = 'pig'
            cmd = f"echo {encoded_query} | base64 -d > /tmp/custom.{ext} && /home/hadoopthuc/pig/bin/pig -x mapreduce -f /tmp/custom.{ext}"
        elif engine == 'spark':
            ext = 'py'
            cmd = f"echo {encoded_query} | base64 -d > /tmp/custom.{ext} && /home/hadoopthuc/spark/bin/spark-submit /tmp/custom.{ext}"
        else:
            return Response({"status": "error", "message": "Engine không hợp lệ!"}, status=400)
            
        result = runner.execute_command(cmd)
        
        job.status = 'Completed' if result['success'] else 'Failed'
        job.logs = result.get('output', '') if result['success'] else result.get('error', '')
        job.end_time = now()
        job.save()
        
        if result['success']:
            return Response({"status": "success", "message": "Chạy Query thành công!", "logs": job.logs}, status=200)
        return Response({"status": "error", "message": "Có lỗi khi chạy Query", "error_logs": job.logs}, status=500)

class ExportExcelView(APIView):
    def get(self, request):
        import csv
        from django.http import HttpResponse
        from django.db import connection
        
        category = request.query_params.get('category', 'All')
        search = request.query_params.get('search', '').strip()
        brand = request.query_params.get('brand', '').strip()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="export_{category}.csv"'
        response.write(u'\ufeff'.encode('utf8'))
        
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Tên Sản Phẩm', 'Thương Hiệu', 'Giá (VNĐ)', 'Nguồn', 'Ngày Crawl'])
        
        try:
            with connection.cursor() as cursor:
                def export_table(table_name):
                    where_clauses = []
                    params = []
                    if search:
                        where_clauses.append("(name LIKE %s OR sku LIKE %s)")
                        params.extend([f"%{search}%", f"%{search}%"])
                    if brand:
                        where_clauses.append("brand = %s")
                        params.append(brand)
                        
                    where_sql = ""
                    if where_clauses:
                        where_sql = "WHERE " + " AND ".join(where_clauses)
                        
                    cursor.execute(f"SELECT sku, name, brand, price_vnd, source, crawl_date FROM {table_name} {where_sql}", params)
                    for row in cursor.fetchall():
                        writer.writerow([row[0] or '', row[1] or '', row[2] or '', f"{row[3]:,.0f}" if row[3] else "0", row[4] or '', str(row[5]) if row[5] else ''])
                        
                if category == 'All' or category == 'Laptop':
                    export_table('laptop_products_common')
                elif category == 'Keyboard':
                    export_table('keyboard_products_common')
                elif category == 'Monitor':
                    export_table('monitor_products_common')
        except Exception:
            pass
            
        return response
from rest_framework.views import APIView
from rest_framework.response import Response
import time
from django.db import connection

class RunDashboardJobView(APIView):
    def post(self, request):
        job_id = request.data.get('job_id')
        from .utils.hadoop_ssh import HadoopTaskRunner
        runner = HadoopTaskRunner('192.168.10.10', username='hadoopthuc')
        
        try:
            with connection.cursor() as cursor:
                import base64
                
                def run_real_spark_job(job_number, sql_query):
                    pyspark_script = f"""
                    from pyspark.sql import SparkSession
                    spark = SparkSession.builder.appName('Dashboard_Chart{job_number}').getOrCreate()
                    spark.sparkContext.setLogLevel("ERROR")
                    df1 = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_laptop_products_common')
                    df1.createOrReplaceTempView("laptop")
                    df2 = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_keyboard_products_common')
                    df2.createOrReplaceTempView("keyboard")
                    df3 = spark.read.option('delimiter', '\\t').csv('/user/hadoopthuc/project/input_monitor_products_common')
                    df3.createOrReplaceTempView("monitor")
                    spark.sql('''{sql_query}''').collect()
                    print("PySpark Job {job_number} Completed Successfully")
                    """
                    encoded_script = base64.b64encode(pyspark_script.encode('utf-8')).decode('utf-8')
                    cmd = f"echo {encoded_script} | base64 -d > /tmp/dash_chart{job_number}.py && /home/hadoopthuc/spark/bin/spark-submit /tmp/dash_chart{job_number}.py"
                    runner.execute_command(cmd)

                if job_id == 1:
                    # So sanh Gia ban TGD vs Phong Vu
                    run_real_spark_job(1, '''
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
                    ''')
                    cursor.execute("DROP TABLE IF EXISTS chart1_tgdd_pv_price")
                    cursor.execute('''
                        CREATE TABLE chart1_tgdd_pv_price AS
                        SELECT brand, 
                               AVG(CASE WHEN source LIKE '%thegioididong%' THEN price_vnd ELSE NULL END) as tgdd_price,
                               AVG(CASE WHEN source LIKE '%phongvu%' THEN price_vnd ELSE NULL END) as pv_price
                        FROM (
                            SELECT brand, source, price_vnd FROM laptop_products_common
                            UNION ALL
                            SELECT brand, source, price_vnd FROM keyboard_products_common
                            UNION ALL
                            SELECT brand, source, price_vnd FROM monitor_products_common
                        ) as all_products
                        GROUP BY brand
                        HAVING tgdd_price IS NOT NULL AND pv_price IS NOT NULL
                        ORDER BY tgdd_price DESC LIMIT 5
                    ''')
                elif job_id == 2:
                    # So sanh So luong san pham TGD vs Phong Vu
                    run_real_spark_job(2, '''
                        SELECT 'The Gioi Di Dong' as source_name, COUNT(1) as volume 
                        FROM (
                            SELECT _c13 as source FROM laptop UNION ALL 
                            SELECT _c13 as source FROM keyboard UNION ALL 
                            SELECT _c13 as source FROM monitor
                        ) all_products WHERE source LIKE '%thegioididong%'
                        UNION ALL
                        SELECT 'Phong Vu' as source_name, COUNT(1) as volume 
                        FROM (
                            SELECT _c13 as source FROM laptop UNION ALL 
                            SELECT _c13 as source FROM keyboard UNION ALL 
                            SELECT _c13 as source FROM monitor
                        ) all_products WHERE source LIKE '%phongvu%'
                    ''')
                    cursor.execute("DROP TABLE IF EXISTS chart2_tgdd_pv_volume")
                    cursor.execute('''
                        CREATE TABLE chart2_tgdd_pv_volume AS
                        SELECT 'The Gioi Di Dong' as source_name, COUNT(*) as volume 
                        FROM (
                            SELECT source FROM laptop_products_common UNION ALL 
                            SELECT source FROM keyboard_products_common UNION ALL 
                            SELECT source FROM monitor_products_common
                        ) as all_products WHERE source LIKE '%thegioididong%'
                        UNION ALL
                        SELECT 'Phong Vu' as source_name, COUNT(*) as volume 
                        FROM (
                            SELECT source FROM laptop_products_common UNION ALL 
                            SELECT source FROM keyboard_products_common UNION ALL 
                            SELECT source FROM monitor_products_common
                        ) as all_products WHERE source LIKE '%phongvu%'
                    ''')
                elif job_id == 3:
                    # Rating trend
                    run_real_spark_job(3, '''
                        SELECT _c0 as brand, AVG(CAST(_c11 AS DOUBLE)) as avg_rating
                        FROM (
                            SELECT _c0, _c11 FROM laptop UNION ALL
                            SELECT _c0, _c11 FROM keyboard UNION ALL
                            SELECT _c0, _c11 FROM monitor
                        ) all_products
                        WHERE CAST(_c11 AS DOUBLE) > 0
                        GROUP BY _c0
                        ORDER BY COUNT(1) DESC LIMIT 5
                    ''')
                    cursor.execute("DROP TABLE IF EXISTS chart3_rating_trend")
                    cursor.execute('''
                        CREATE TABLE chart3_rating_trend AS
                        SELECT brand, AVG(rating) as avg_rating
                        FROM (
                            SELECT brand, rating FROM laptop_products_common
                            UNION ALL
                            SELECT brand, rating FROM keyboard_products_common
                            UNION ALL
                            SELECT brand, rating FROM monitor_products_common
                        ) as all_products
                        WHERE rating > 0
                        GROUP BY brand
                        ORDER BY COUNT(*) DESC LIMIT 5
                    ''')
                elif job_id == 4:
                    # Radar top brands
                    run_real_spark_job(4, '''
                        SELECT _c0 as brand, COUNT(1) as total
                        FROM (
                            SELECT _c0 FROM laptop UNION ALL
                            SELECT _c0 FROM keyboard UNION ALL
                            SELECT _c0 FROM monitor
                        ) all_products
                        GROUP BY _c0
                        ORDER BY total DESC LIMIT 5
                    ''')
                    cursor.execute("DROP TABLE IF EXISTS chart4_top_brands")
                    cursor.execute('''
                        CREATE TABLE chart4_top_brands AS
                        SELECT brand, COUNT(*) as total
                        FROM (
                            SELECT brand FROM laptop_products_common
                            UNION ALL
                            SELECT brand FROM keyboard_products_common
                            UNION ALL
                            SELECT brand FROM monitor_products_common
                        ) as all_products
                        GROUP BY brand
                        ORDER BY total DESC LIMIT 5
                    ''')
                elif job_id == 5:
                    # Category dist
                    run_real_spark_job(5, '''
                        SELECT 'Laptop' as category, COUNT(1) as total FROM laptop
                        UNION ALL
                        SELECT 'Keyboard' as category, COUNT(1) as total FROM keyboard
                        UNION ALL
                        SELECT 'Monitor' as category, COUNT(1) as total FROM monitor
                    ''')
                    cursor.execute("DROP TABLE IF EXISTS chart5_category_dist")
                    cursor.execute('''
                        CREATE TABLE chart5_category_dist AS
                        SELECT 'Laptop' as category, COUNT(*) as total FROM laptop_products_common
                        UNION ALL
                        SELECT 'Keyboard' as category, COUNT(*) as total FROM keyboard_products_common
                        UNION ALL
                        SELECT 'Monitor' as category, COUNT(*) as total FROM monitor_products_common
                    ''')
                elif str(job_id) == 'reset':
                    cursor.execute("DROP TABLE IF EXISTS chart1_tgdd_pv_price")
                    cursor.execute("DROP TABLE IF EXISTS chart2_tgdd_pv_volume")
                    cursor.execute("DROP TABLE IF EXISTS chart3_rating_trend")
                    cursor.execute("DROP TABLE IF EXISTS chart4_top_brands")
                    cursor.execute("DROP TABLE IF EXISTS chart5_category_dist")
                    return Response({"status": "success", "message": "Đã reset Dashboard thành công!"}, status=200)
                else:
                    return Response({"status": "error", "message": "Job ID không hợp lệ"}, status=400)
            
            return Response({"status": "success", "message": f"Chạy MapReduce Bài toán {job_id} thành công!"}, status=200)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)

