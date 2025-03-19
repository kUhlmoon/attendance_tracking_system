from django.urls import path
from .views import attendance_list, upload_attendance_csv

urlpatterns = [
    path('', attendance_list, name='attendance_list'),
    path('upload-csv/', upload_attendance_csv, name='upload_attendance_csv'),
]
