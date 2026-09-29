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
                # Đếm số lượng sản phẩm mỗi loại
                cursor.execute("SELECT COUNT(*) FROM laptop_products_common")
                laptop_count = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM keyboard_products_common")
                keyboard_count = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM monitor_products_common")
                monitor_count = cursor.fetchone()[0] or 0
                
                total_records = laptop_count + keyboard_count + monitor_count
                
                def get_mr_data(table_name):
                    try:
                        cursor.execute(f"SELECT brand, average_price FROM {table_name}")
                        brands = []
                        for row in cursor.fetchall():
                            try:
                                b, v = str(row[0]), str(row[1])
                                try:
                                    val = int(float(v))
                                    name = b[:15]
                                except ValueError:
                                    val = int(float(b))
                                    name = v[:15]
                                    
                                if name.upper() != 'AVERAGE_PRICE' and name.upper() != 'BRAND':
                                    brands.append({"name": name, "value": val})
                            except:
                                pass
                        brands.sort(key=lambda x: x['value'], reverse=True)
                        return brands[:5] if brands else [{"name": "Chưa có dữ liệu", "value": 1}]
                    except Exception as e:
                        return [{"name": "Chưa Export", "value": 1}]

                # Tự động tìm tất cả các bảng *_stats
                cursor.execute("SHOW TABLES LIKE '%_stats'")
                stats_tables = [row[0] for row in cursor.fetchall()]
                
                dynamic_pie_charts = []
                for st_table in stats_tables:
                    # Tạo tiêu đề đẹp từ tên bảng (vd: laptop_stats -> Laptop)
                    title = st_table.replace('_stats', '').capitalize()
                    dynamic_pie_charts.append({
                        "title": f"Thống Kê {title}",
                        "data": get_mr_data(st_table)
                    })

                from .models import JobHistory
                from django.db.models import Count, Q
                
                # Hiệu suất Job (Real Data từ JobHistory)
                job_stats = JobHistory.objects.values('job_type').annotate(
                    success=Count('id', filter=Q(status='Completed')),
                    error=Count('id', filter=Q(status='Failed'))
                )
                line_data = []
                for stat in job_stats:
                    line_data.append({
                        "name": stat['job_type'],
                        "success": stat['success'],
                        "error": stat['error']
                    })
                if not line_data:
                    line_data = [{"name": "Chưa có Job", "success": 0, "error": 0}]

                # Lưu lượng truy cập (Thay bằng Giá trung bình các hãng Laptop - Real Data)
                cursor.execute("SELECT brand, AVG(price_vnd) FROM laptop_products_common GROUP BY brand ORDER BY COUNT(*) DESC LIMIT 6")
                area_data = []
                for row in cursor.fetchall():
                    try:
                        area_data.append({
                            "name": str(row[0])[:15],
                            "value": int(row[1])
                        })
                    except:
                        pass
                if not area_data:
                    area_data = [{"name": "Chưa có Data", "value": 0}]
                    
                # Chart tĩnh 1: Tỷ trọng danh mục (Pie Chart)
                category_pie = [
                    {"name": "Laptop", "value": laptop_count},
                    {"name": "Bàn phím", "value": keyboard_count},
                    {"name": "Màn hình", "value": monitor_count}
                ]
                
                # Chart tĩnh 2: Top 5 thương hiệu nhiều sản phẩm nhất (Bar Chart)
                cursor.execute("SELECT brand, COUNT(*) as cnt FROM laptop_products_common GROUP BY brand ORDER BY cnt DESC LIMIT 5")
                top_brands_bar = [{"name": str(row[0])[:15], "total": row[1]} for row in cursor.fetchall()]
                if not top_brands_bar:
                    top_brands_bar = [{"name": "Chưa có", "total": 0}]

                job_count = JobHistory.objects.count()

                data = {
                    "barData": [
                        { "name": 'Laptop', "total": laptop_count },
                        { "name": 'Bàn phím', "total": keyboard_count },
                        { "name": 'Màn hình', "total": monitor_count },
                    ],
                    "lineData": line_data,
                    "dynamicPieCharts": dynamic_pie_charts,
                    "areaData": area_data,
                    "categoryPie": category_pie,
                    "topBrandsBar": top_brands_bar,
                    "kpis": {
                        "totalData": f"{total_records} SP",
                        "totalDataTrend": "Dữ liệu thật",
                        "totalDataIsUp": True,
                        "mapReduceQueries": f"{job_count}",
                        "mapReduceTrend": "Số lượng Job",
                        "mapReduceIsUp": True,
                        "activeAccounts": "3",
                        "activeAccountsTrend": "Bảng dữ liệu",
                        "activeAccountsIsUp": True,
                        "reportsGenerated": "Sẵn sàng",
                        "reportsTrend": "Chờ lệnh",
                        "reportsIsUp": True,
                    }
                }
                return Response(data, status=200)
        except Exception as e:
            # Fallback nếu bảng chưa có
            return Response({"error": str(e), "message": "Lỗi lấy dữ liệu từ MySQL."}, status=500)

class DataTableDataView(APIView):
    def get(self, request):
        from django.db import connection
        category = request.query_params.get('category', 'All')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        search = request.query_params.get('search', '').strip()
        brand = request.query_params.get('brand', '').strip()
        offset = (page - 1) * limit
        
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
                    cursor.execute(f"SELECT sku, name, brand, price_vnd, source, crawl_date FROM {table_name} {where_sql} LIMIT {limit} OFFSET {offset}", params)
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
                        
                # Với category All, tạm lấy từ Laptop (vì ghép 3 bảng phân trang phức tạp hơn, có thể nâng cấp sau)
                if category == 'All':
                    fetch_table('laptop_products_common', 'LAP')
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
