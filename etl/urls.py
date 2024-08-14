from django.urls import path
from .views import run_etl

urlpatterns = [
    path('run-etl/', run_etl, name='run_etl'),
]
