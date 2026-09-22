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
