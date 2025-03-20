from django.urls import path
from .views import (
    attendance_list,
    upload_attendance_csv,
    upload_attendance,
    attendance_dashboard
)

urlpatterns = [
    # API endpoint to check if attendance API is working
    path('', attendance_list, name='attendance_list'),

    # API endpoint for uploading CSV via API (POST request)
    path('upload-csv/', upload_attendance_csv, name='upload_attendance_csv'),

    # Web-based form for lecturers to upload attendance CSV
    path('upload/', upload_attendance, name='upload_attendance'),

    # Dashboard to view attendance records
    path('dashboard/', attendance_dashboard, name='attendance_dashboard'),
]
