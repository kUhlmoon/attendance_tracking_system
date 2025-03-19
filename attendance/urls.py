from django.urls import path
from .views import upload_attendance_csv

urlpatterns = [
    path('upload-csv/', upload_attendance_csv, name='upload_attendance_csv'),
]
