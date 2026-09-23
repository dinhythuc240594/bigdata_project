from rest_framework.views import APIView
from rest_framework.response import Response
from .utils.hadoop_ssh import HadoopTaskRunner

class RunMapReduceView(APIView):
    def post(self, request):
        runner = HadoopTaskRunner()
        result = runner.run_mapreduce_job()
        
        if result['success']:
            return Response({
                "status": "success",
                "message": "MapReduce Task đã thực thi thành công!", 
                "logs": result['output']
            }, status=200)
        else:
            return Response({
                "status": "error",
                "message": "Có lỗi khi chạy MapReduce", 
                "error_logs": result['error']
            }, status=500)

class RunSqoopView(APIView):
    def post(self, request):
        runner = HadoopTaskRunner()
        result = runner.run_sqoop_import()
        
        if result['success']:
            return Response({
                "status": "success",
                "message": "Sqoop Import đã thực thi thành công!", 
                "logs": result['output']
            }, status=200)
        else:
            return Response({
                "status": "error",
                "message": "Có lỗi khi chạy Sqoop", 
                "error_logs": result['error']
            }, status=500)

class DashboardStatsView(APIView):
    def get(self, request):
        # Mock data corresponding to the frontend requirement
        data = {
            "barData": [
                { "name": 'Loại A', "total": 4000 }, { "name": 'Loại B', "total": 3000 },
                { "name": 'Loại C', "total": 2000 }, { "name": 'Loại D', "total": 2780 },
            ],
            "lineData": [
                { "month": 'T1', "success": 240, "error": 40 },
                { "month": 'T2', "success": 139, "error": 30 },
                { "month": 'T3', "success": 380, "error": 20 },
                { "month": 'T4', "success": 390, "error": 27 },
                { "month": 'T5', "success": 480, "error": 18 },
                { "month": 'T6', "success": 520, "error": 15 },
            ],
            "pieData1": [
                { "name": 'Đã xử lý', "value": 75 }, { "name": 'Chờ xử lý', "value": 25 }
            ],
            "pieData2": [
                { "name": 'Hà Nội', "value": 45 }, { "name": 'TP.HCM', "value": 35 }, { "name": 'Đà Nẵng', "value": 20 }
            ],
            "areaData": [
                { "time": '00:00', "traffic": 1200 }, { "time": '04:00', "traffic": 800 },
                { "time": '08:00', "traffic": 3200 }, { "time": '12:00', "traffic": 4500 },
                { "time": '16:00', "traffic": 3900 }, { "time": '20:00', "traffic": 2800 },
            ],
            "kpis": {
                "totalData": "124.5 GB",
                "totalDataTrend": "+12.5%",
                "totalDataIsUp": True,
                "mapReduceQueries": "1,432",
                "mapReduceTrend": "+8.2%",
                "mapReduceIsUp": True,
                "activeAccounts": "8,924",
                "activeAccountsTrend": "-2.4%",
                "activeAccountsIsUp": False,
                "reportsGenerated": "356",
                "reportsTrend": "+15.3%",
                "reportsIsUp": True,
            }
        }
        return Response(data, status=200)
