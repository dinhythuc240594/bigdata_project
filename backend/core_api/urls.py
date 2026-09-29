from django.urls import path
from .views import RunMapReduceView, RunSqoopView, DashboardStatsView, JobHistoryView, DataTableDataView, DataRecordView, RunSqoopExportView, ActiveTasksView, ClusterStatusView

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
]
