from django.urls import path
from .views import RunMapReduceView, RunSqoopView, DashboardStatsView, JobHistoryView, DataTableDataView, DataRecordView, RunSqoopExportView, ActiveTasksView, ClusterStatusView, RunHiveView, RunPigView, RunSparkView, RunCustomQueryView, ExportExcelView

urlpatterns = [
    path('run-mapreduce/', RunMapReduceView.as_view(), name='run-mapreduce'),
    path('run-sqoop/', RunSqoopView.as_view(), name='run-sqoop'),
    path('run-sqoop-export/', RunSqoopExportView.as_view(), name='run-sqoop-export'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('job-history/', JobHistoryView.as_view(), name='job-history'),
    path('data-table/', DataTableDataView.as_view(), name='data-table'),
    path('data-record/', DataRecordView.as_view(), name='data-record'),
    path('active-tasks/', ActiveTasksView.as_view(), name='active-tasks'),
    path('cluster-status/', ClusterStatusView.as_view(), name='cluster-status'),
    path('run-hive/', RunHiveView.as_view(), name='run-hive'),
    path('run-pig/', RunPigView.as_view(), name='run-pig'),
    path('run-spark/', RunSparkView.as_view(), name='run-spark'),
    path('run-custom-query/', RunCustomQueryView.as_view(), name='run-custom-query'),
    path('export-excel/', ExportExcelView.as_view(), name='export-excel'),
]
