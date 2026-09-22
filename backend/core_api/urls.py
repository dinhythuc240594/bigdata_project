from django.urls import path
from .views import RunMapReduceView

urlpatterns = [
    path('run-mapreduce/', RunMapReduceView.as_view(), name='run-mapreduce'),
]
