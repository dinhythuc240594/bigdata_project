import re

with open('c:/Users/Laptop/Documents/GitHub/bigdata_project/backend/core_api/views.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

new_view = '''class DashboardStatsView(APIView):
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
'''

start_idx = content.find('class DashboardStatsView(APIView):')
end_idx = content.find('class DataTableDataView(APIView):')

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_view + '\n' + content[end_idx:]
    with open('c:/Users/Laptop/Documents/GitHub/bigdata_project/backend/core_api/views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated DashboardStatsView successfully.")
else:
    print("Could not find the class boundaries.")
