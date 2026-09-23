from django.urls import path
from .views import RunMapReduceView, RunSqoopView, DashboardStatsView

urlpatterns = [
    path('run-mapreduce/', RunMapReduceView.as_view(), name='run-mapreduce'),
    path('run-sqoop/', RunSqoopView.as_view(), name='run-sqoop'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
