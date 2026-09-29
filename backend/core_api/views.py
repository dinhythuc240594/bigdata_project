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
        cmd = f"/home/hadoopthuc/hadoop/bin/sqoop export --connect jdbc:mysql://192.168.10.5/bigdata_db --username root --password 123456789 --table {table_name} --export-dir {export_dir} --input-fields-terminated-by '\\t'"
        
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
                                brands.append({"name": str(row[0])[:15], "value": int(row[1])})
                            except:
                                pass
                        brands.sort(key=lambda x: x['value'], reverse=True)
                        return brands[:4] if brands else [{"name": "Chưa Export", "value": 1}]
                    except Exception:
                        return [{"name": "Chưa Export", "value": 1}]

                pie1 = get_mr_data('laptop_stats')
                pie2 = get_mr_data('monitor_stats')

                from .models import JobHistory
                job_count = JobHistory.objects.count()

                data = {
                    "barData": [
                        { "name": 'Laptop', "total": laptop_count },
                        { "name": 'Bàn phím', "total": keyboard_count },
                        { "name": 'Màn hình', "total": monitor_count },
                    ],
                    "lineData": [
                        { "month": 'T1', "success": 240, "error": 40 },
                        { "month": 'T2', "success": 139, "error": 30 },
                        { "month": 'T3', "success": 380, "error": 20 },
                        { "month": 'T4', "success": 390, "error": 27 },
                        { "month": 'T5', "success": 480, "error": 18 },
                        { "month": 'T6', "success": 520, "error": 15 },
                    ],
                    "pieData1": pie1,
                    "pieData2": pie2,
                    "areaData": [
                        { "time": '00:00', "traffic": 1200 }, { "time": '04:00', "traffic": 800 },
                        { "time": '08:00', "traffic": 3200 }, { "time": '12:00', "traffic": 4500 },
                        { "time": '16:00', "traffic": 3900 }, { "time": '20:00', "traffic": 2800 },
                    ],
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
        offset = (page - 1) * limit
        
        data = []
        total_records = 0
        
        try:
            with connection.cursor() as cursor:
                def fetch_table(table_name, cat_name):
                    nonlocal total_records
                    # Lấy tổng số lượng
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    total_records = cursor.fetchone()[0] or 0
                    
                    # Lấy dữ liệu phân trang
                    cursor.execute(f"SELECT sku, name, brand, price_vnd, source, crawl_date FROM {table_name} LIMIT {limit} OFFSET {offset}")
                    for idx, row in enumerate(cursor.fetchall()):
                        data.append({
                            'id': f"{cat_name}-{offset+idx}",
                            'sku': row[0],
                            'name': row[1],
                            'brand': row[2],
                            'price': f"{row[3]:,.0f}" if row[3] else "0",
                            'source': row[4],
                            'date': str(row[5])
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
